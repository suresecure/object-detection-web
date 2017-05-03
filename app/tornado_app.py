import tornado.ioloop
import tornado.web
import tornado.httpclient
# import tornado.gen
# import tcelery
from tornado import gen, web
from apscheduler.schedulers.tornado import TornadoScheduler
from stat import S_ISREG, S_ISDIR, ST_CTIME, ST_MODE

import os
import shutil
import werkzeug
import logging
import celery
import celery.exceptions
import settings
import config
import time

import datetime
# from sqlalchemy import create_engine
# engine = create_engine('sqlite:///test.sqlite.db', echo=False)
# from sqlalchemy.orm import sessionmaker
# Session = sessionmaker(bind=engine)
# from sqlalchemy.ext.declarative import declarative_base
# Base = declarative_base()
# from sqlalchemy import Column, DateTime, Integer, String

# class AccessLog(Base):
    # __tablename__ = 'access_logs'
    # id = Column(Integer, primary_key=True)
    # created_datetime = Column(
        # DateTime, default=datetime.datetime.now, index=True)
    # return_code = Column(Integer, default=-1, index=True)
    # error_message = Column(String, default='')

    # def __repr__(self):
       # return "<AccessLog(created_datetime='%s', return_code='%d', error_message='%s')>" % (self.created_datetime, self.return_code, self.error_message)
# Base.metadata.create_all(engine)

the_celery = celery.Celery('tasks')
the_celery.config_from_object(settings)

@the_celery.task(name="tasks.object_detection_task", queue="important")
def object_detection_task(imgstream, secure_filename):
    pass

# tcelery.setup_nonblocking_producer()
# request_count = 0
# response_count = 0

class ObjectDetectionHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def post(self):
        try:
            # access_log = AccessLog()

            image_bytestr = self.request.files['image'][0].body
            filename = self.request.files['image'][0].filename
            imagestream = image_bytestr
            filename_ = str(datetime.datetime.now()).replace(' ', '_') + \
                werkzeug.secure_filename(filename)

            # print 'yield task'
            # res = yield gen.Task(object_detection_task.apply_async, args=[imagestream, filename_], expires=5)
            # print 'after yield task'

            # print 'send task start', local_count
            res = object_detection_task.apply_async(
                args=[imagestream, filename_], expires=2)
            # print 'send task over', local_count
            wait_times = 3
            while wait_times>0:
                yield gen.sleep(1)
                result = res.result
                if result is None:
                    wait_times -= 1
                else:
                    break
            # store_upload_image(imagestream, filename_)
            result = res.result
            if result is None:
                res.revoke()
                # res.forget()
                self.write({'error': 'time is out'})
            elif isinstance(result, celery.exceptions.TaskRevokedError):
                self.write({'error': 'time is out'})
            elif isinstance(result, Exception):
                self.write({'error': str(result)})
            else:
                self.write({'targets': result})
            # print '2', local_count
        # except celery.exceptions.TaskRevokedError:
            # print('time is out')
            # # access_log.return_code = 0
            # # access_log.error_message = "time is out"
            # self.write({'error': 'time is out'})
        except Exception, ex:
            print(ex)
            # access_log.return_code = 1
            # access_log.error_message = str(ex)
            self.write({'error': str(ex)})
        finally:
            pass
            # response_count += 1

        # try:
            # session = Session()
            # session.add(access_log)
            # session.commit()
        # except Exception, ex:
            # print(ex)
            # session.rollback()
        # finally:
            # session.close()

        # print '3', local_count
        self.finish()
        # print '4', local_count

MIN_AVAIL_DISK_SIZE = 1000 * 1024 * 1024 * 1024
if hasattr(config, 'MIN_AVAIL_DISK_SIZE'):
    MIN_AVAIL_DISK_SIZE = config.MIN_AVAIL_DISK_SIZE
MAX_IMAGE_STORE_DAYS = 7
if hasattr(config, 'MAX_IMAGE_STORE_DAYS'):
    MAX_IMAGE_STORE_DAYS = config.MAX_IMAGE_STORE_DAYS
MAX_ACCESS_LOGS_STORE_DAYS = 14
if hasattr(config, 'MAX_ACCESS_LOGS_STORE_DAYS'):
    MAX_ACCESS_LOGS_STORE_DAYS = config.MAX_ACCESS_LOGS_STORE_DAYS

if not os.path.exists(config.UPLOAD_FOLDER):
    os.makedirs(config.UPLOAD_FOLDER)

def remove_history_images_uploaded():
    dirpath = config.UPLOAD_FOLDER
    # get all entries in the directory w/ stats
    entries = (os.path.join(dirpath, fn) for fn in os.listdir(dirpath))
    entries = ((os.stat(path), path) for path in entries)

    # delete all image files
    entries = (path for stat, path in entries if S_ISREG(stat[ST_MODE]))
    for path in entries:
        print 'remove tmp file: ', path
        os.remove(path)

    # handle dirs
    entries = (os.path.join(dirpath, fn) for fn in os.listdir(dirpath))
    entries = ((os.stat(path), path) for path in entries)
    # leave only dirs, insert creation date
    entries = ((stat[ST_CTIME], path)
               for stat, path in entries if S_ISDIR(stat[ST_MODE]))

    #NOTE: on Windows `ST_CTIME` is a creation date
    #  but on Unix it could be something else
    #NOTE: use `ST_MTIME` to sort by a modification date
    oldest_datetime = datetime.datetime.now(
    ) - datetime.timedelta(days=MAX_IMAGE_STORE_DAYS)
    for cdate, path in sorted(entries):
        try:
            print path
            created_datetime = datetime.datetime.strptime(
                os.path.basename(path), '%Y%m%d%H')
            if created_datetime < oldest_datetime:
                print 'rm too old image dir: ', path
                shutil.rmtree(path)
            else:
                #if we are short of disk space, delete the folder still
                stat = os.statvfs(config.UPLOAD_FOLDER)
                avail_size = stat.f_bsize * stat.f_bavail
                if avail_size < MIN_AVAIL_DISK_SIZE:
                    print 'rm tmp image dir due to lack of disk space: ', path
                    shutil.rmtree(path)
        except ValueError, verror:
            print verror
            # delete dirs not created by app
            shutil.rmtree(path)
        except Exception, ex:
            print ex


# def remove_history_access_logs():
    # # sqlalchemy objects created in a thread can only be used in that same
    # # thread
    # try:
        # local_engine = create_engine('sqlite:///test.sqlite.db', echo=False)
        # LocalSession = sessionmaker(bind=local_engine)
        # session = LocalSession()
        # datetime_ndays_ago = datetime.datetime.now(
        # ) - datetime.timedelta(days=MAX_ACCESS_LOGS_STORE_DAYS)
        # access_logs = session.query(AccessLog).filter(
            # AccessLog.created_datetime < datetime_ndays_ago)
        # access_logs.delete(synchronize_session='fetch')
        # session.commit()
    # except Exception, ex:
        # print ex

def remove_history_data():
    print 'remove history images and access logs'
    remove_history_images_uploaded()
    # remove_history_access_logs()


def store_upload_image(imagestream, filename):
    # create dir each hour to store images
    subdir = datetime.datetime.now().strftime('%Y%m%d%H')
    storedir = os.path.join(config.UPLOAD_FOLDER, subdir)
    if not os.path.exists(storedir):
        os.makedirs(storedir)
    filename = os.path.join(storedir, filename)
    with open(filename, "wb") as f:
        f.write(imagestream)

scheduler = TornadoScheduler()
# scheduler.add_job(remove_history_data, 'date')
scheduler.add_job(remove_history_data, 'interval', hours=1)
scheduler.start()

def make_app():
    return tornado.web.Application([
        (r"/person_detection", ObjectDetectionHandler),
        (r"/object_detection", ObjectDetectionHandler)
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(8090)
    tornado.ioloop.IOLoop.current().start()
