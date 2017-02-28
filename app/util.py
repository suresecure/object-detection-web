import os
import sys
import time
import datetime
import shutil
from stat import S_ISREG, S_ISDIR, ST_CTIME, ST_MODE
import pickle
import werkzeug
import logging

import celery
import celery.exceptions

import config
import cv2
import numpy as np

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


def remove_history_access_logs():
    pass
    # try:
        # datetime_ndays_ago = datetime.datetime.now(
        # ) - datetime.timedelta(days=MAX_ACCESS_LOGS_STORE_DAYS)
        # access_logs = AccessLog.query.filter(
            # AccessLog.created_datetime < datetime_ndays_ago)
        # access_logs.delete(synchronize_session='fetch')
        # db.session.commit()

        # # access_logs = AccessLog.query.all()
        # # print 'after remove access logs'
        # # for al in access_logs:
            # # print al.return_code, al.error_message, al.created_datetime
    # except Exception, ex:
        # print ex
        # db.session.rollback()
        # db.drop_all()
        # db.create_all()


def remove_history_data():
    print 'remove history images and access logs'
    remove_history_images_uploaded()
    remove_history_access_logs()

import settings
the_celery = celery.Celery('tasks')
the_celery.config_from_object(settings)

@the_celery.task(name="tasks.object_detection_task", queue="important")
def object_detection_task(imgstream, secure_filename):
    pass

# create dir each hour to store images
subdir = datetime.datetime.now().strftime('%Y%m%d%H')
storedir = os.path.join(config.UPLOAD_FOLDER, subdir)
if not os.path.exists(storedir):
    os.makedirs(storedir)
filename = os.path.join(storedir, filename_)
with open(filename, "wb") as f:
    f.write(imagestream)
