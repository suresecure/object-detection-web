# -*- coding: utf-8 -*-
from __future__ import absolute_import

from itertools import count

from celery.task import Task
from celery.five import Empty, Queue
from celery.utils.log import get_logger
from celery.worker.job import Request
from celery.utils import noop

from datetime import datetime

__all__ = ['Batches']

logger = get_logger(__name__)


def consume_queue(queue):
    """Iterator yielding all immediately available items in a
    :class:`Queue.Queue`.

    The iterator stops as soon as the queue raises :exc:`Queue.Empty`.

    *Examples*

        >>> q = Queue()
        >>> map(q.put, range(4))
        >>> list(consume_queue(q))
        [0, 1, 2, 3]
        >>> list(consume_queue(q))
        []

    """
    get = queue.get_nowait
    while 1:
        try:
            yield get()
        except Empty:
            break


def apply_batches_task(task, args, loglevel, logfile):
    logger.info("apply batches task")
    task.push_request(loglevel=loglevel, logfile=logfile)
    try:
        result = task(*args)
    except Exception as exc:
        result = None
        logger.error('Error: %r', exc, exc_info=True)
    finally:
        task.pop_request()
    return result


class SimpleRequest(object):
    """Pickleable request."""

    #: task id
    id = None

    #: task name
    name = None

    #: positional arguments
    args = ()

    #: keyword arguments
    kwargs = {}

    #: message delivery information.
    delivery_info = None

    #: worker node name
    hostname = None

    def __init__(self, id, name, args, kwargs, delivery_info, hostname):
        self.id = id
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.delivery_info = delivery_info
        self.hostname = hostname

    @classmethod
    def from_request(cls, request):
        return cls(request.id, request.name, request.args,
                   request.kwargs, request.delivery_info, request.hostname)


class Batches(Task):
    abstract = True

    #: Maximum number of message in buffer.
    flush_every = 10

    #: Timeout in seconds before buffer is flushed anyway.
    flush_interval = 30

    worker_controller = None

    def __init__(self):
        self._buffer = Queue()
        self._count = count(1)
        self._tref = None
        self._pool = None

    def run(self, requests):
        raise NotImplementedError('must implement run(requests)')

    def Strategy(self, task, app, consumer):
        self._pool = consumer.pool
        self.worker_controller = consumer.controller
        hostname = consumer.hostname
        eventer = consumer.event_dispatcher
        Req = Request
        connection_errors = consumer.connection_errors
        timer = consumer.timer
        put_buffer = self._buffer.put
        flush_buffer = self._do_flush

        def task_message_handler(message, body, ack, reject, callbacks, **kw):
            request = Req(body, on_ack=ack, app=app, hostname=hostname,
                          events=eventer, task=task,
                          connection_errors=connection_errors,
                          delivery_info=message.delivery_info)
            put_buffer(request)

            if self._tref is None:     # first request starts flush timer.
                self._tref = timer.call_repeatedly(
                    self.flush_interval, flush_buffer,
                )

            if not next(self._count) % self.flush_every:
                flush_buffer()

        return task_message_handler

    def flush(self, requests):
        return self.worker_controller._quick_acquire(self.apply_buffer, requests, ([SimpleRequest.from_request(r)
                                             for r in requests], ))
        # return self.apply_buffer(requests, ([SimpleRequest.from_request(r)
                                             # for r in requests], ))

    def _do_flush(self):
        logger.debug('Batches: Wake-up to flush buffer...')
        requests = None
        if self._buffer.qsize():
            requests = list(consume_queue(self._buffer))
            if requests:
                logger.debug('Batches: Buffer complete: %s', len(requests))
                self.flush(requests)
        if not requests:
            logger.debug('Batches: Canceling timer: Nothing in buffer.')
            if self._tref:
                self._tref.cancel()  # cancel timer.
            self._tref = None

    def apply_buffer(self, requests, args=(), kwargs={}):
        all_revoked = True
        for req in requests:
            if req.expires:
                now = datetime.now(req.expires.tzinfo)
                if now <= req.expires:
                    all_revoked = False
        if all_revoked:
            logger.info("All batch task revoked")
            for req in requests:
                req.revoked()
            self.worker_controller._quick_release()
            return

        logger.info("apply buffer")
        acks_late = [], []
        [acks_late[r.task.acks_late].append(r) for r in requests]
        assert requests and (acks_late[True] or acks_late[False])

        def on_accepted(pid, time_accepted):
            [req.acknowledge() for req in acks_late[False]]

        def on_return(result):
            [req.acknowledge() for req in acks_late[True]]

        return self._pool.apply_async(
            apply_batches_task,
            (self, args, 0, None),
            accept_callback=on_accepted,
            callback=acks_late[True] and on_return or noop,
        )
