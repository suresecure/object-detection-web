# from __future__ import absolute_import
import os
import sys
import time
import datetime
import shutil
from stat import S_ISREG, S_ISDIR, ST_CTIME, ST_MODE
import flask
import pickle
import werkzeug
import celery
import celery.exceptions
import logging
# import batches
import flask_restful
# import tasks
import config
import cv2
import numpy as np
from flask_apscheduler import APScheduler
from flask_sqlalchemy import SQLAlchemy

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
    try:
        datetime_ndays_ago = datetime.datetime.now(
        ) - datetime.timedelta(days=MAX_ACCESS_LOGS_STORE_DAYS)
        access_logs = AccessLog.query.filter(
            AccessLog.created_datetime < datetime_ndays_ago)
        access_logs.delete(synchronize_session='fetch')
        db.session.commit()

        # access_logs = AccessLog.query.all()
        # print 'after remove access logs'
        # for al in access_logs:
            # print al.return_code, al.error_message, al.created_datetime
    except Exception, ex:
        print ex
        db.session.rollback()
        db.drop_all()
        db.create_all()


def remove_history_data():
    print 'remove history images and access logs'
    remove_history_images_uploaded()
    remove_history_access_logs()

app = flask.Flask(__name__)

class FlaskConfig(object):
    JOBS = [
        {
            'id': 'remove_history_data',
            'func': 'app:remove_history_data',
            # 'args': (1, 2),
            'trigger': 'cron',
            'hour': 0
        }
    ]
    SCHEDULER_API_ENABLED = True

app.config.from_object(FlaskConfig())
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

class AccessLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_datetime = db.Column(
        db.DateTime, default=datetime.datetime.now, index=True)
    return_code = db.Column(db.Integer, default=-1, index=True)
    error_message = db.Column(db.String(120), default='')

    # def __init__(self, username, email):
    # self.username = username
    # self.email = email

    def __repr__(self):
        return '<User %r>' % self.error_message

db.create_all()

# def test_init_database():
    # al = AccessLog()
    # al.return_code = 1
    # al.error_message = 'yes'
    # db.session.add(al)
    # al = AccessLog()
    # db.session.add(al)
    # al = AccessLog()
    # al.created_datetime = datetime.datetime.now() - datetime.timedelta(days=20)
    # db.session.add(al)
    # db.session.commit()
    # access_logs = AccessLog.query.all()
    # print 'all access logs'
    # for al in access_logs:
        # print al.return_code, al.error_message, al.created_datetime

# test_init_database()

scheduler = APScheduler()
# it is also possible to enable the API directly
# scheduler.api_enabled = True
scheduler.init_app(app)
scheduler.start()

import settings
the_celery = celery.Celery('tasks')
the_celery.config_from_object(settings)

@the_celery.task(name="tasks.ObjectDetection", queue="important")
def ObjectDetection(imgstream, secure_filename):
    pass

# curl -X POST -F image=@hy0.jpg http://localhost:8000/person_detection
def object_detection():
    detection_result = {}
    return_code = -1
    try:
      # print len(flask.request.files)
      imagefile = flask.request.files['image']
      imagestream = imagefile.read()

      filename_ = str(datetime.datetime.now()).replace(' ', '_') + \
          werkzeug.secure_filename(imagefile.filename)

      res = ObjectDetection.apply_async(
          args=[imagestream, filename_], expires=5)

      # create dir each hour to store images
      subdir = datetime.datetime.now().strftime('%Y%m%d%H')
      storedir = os.path.join(config.UPLOAD_FOLDER, subdir)
      if not os.path.exists(storedir):
          os.makedirs(storedir)
      filename = os.path.join(storedir, filename_)
      with open(filename, "wb") as f:
          f.write(imagestream)

      result = res.get()
      # result = 1

      # if len(result)>0:
      # filename = os.path.join(config.UPLOAD_FOLDER_DETECTED, filename_)
      # with open(filename, 'w') as f:
      # pickle.dump(result, f)

      # if draw_result:
      # draw_filename = os.path.join(config.UPLOAD_FOLDER_DRAW, filename_)
      # img_data = cv2.imdecode(np.asarray(bytearray(imagestream), dtype=np.uint8), -1)
      # for t in result:
      # cv2.rectangle(img_data, (t['x'],t['y']), (t['x']+t['w'],t['y']+t['h']),
      # (255,0,0),3)
      # cv2.imwrite(draw_filename, img_data)
      detection_result = {'targets': result}
    except celery.exceptions.TaskRevokedError:
      print('time is out')
      return_code = 0
      detection_result = {'error': 'time is out'}
    except AttributeError:
      print('image is invalid')
      return_code = 1
      detection_result = {'error': 'iamge is invalid'}
    except Exception, ex:
      print(ex)
      return_code = 2
      detection_result = {'error': str(ex)}

    try:
      access_log = AccessLog()
      access_log.return_code = return_code
      db.session.add(access_log)
      db.session.commit()
    except Exception, ex:
        print ex
        db.session.rollback()
        db.session.commit()
        db.drop_all()
        db.create_all()

    return detection_result


class ObjectDetection(flask_restful.Resource):

    def post(self):
        return object_detection()


class PersonDetection(flask_restful.Resource):

    def post(self):
        return object_detection()


class Stat(flask_restful.Resource):

    def post(self):
        try:
            print flask.request.args
            # datetime string format: 20170210213021
            # xxxx(year)xx(month)xx(day)xx(24hour)xx(minute)xx(second)
            start_datetime = datetime.datetime.strptime(
                flask.request.args.get('start_datetime'), "%Y%m%d%H%M%S")
            end_datetime = datetime.datetime.strptime(
                flask.request.args.get('end_datetime'), "%Y%m%d%H%M%S")
            access_logs = AccessLog.query.filter(
                AccessLog.created_datetime.between(start_datetime, end_datetime))
            # success_access_logs = access_logs.filter(AccessLog.return_code == -1)
            total_logs_num = 0
            success_logs_num = 0
            # filter in memory, instead of querying database again
            for access_log in access_logs:
                total_logs_num += 1
                if access_log.return_code == -1:
                    success_logs_num += 1

            return{"total_calls": total_logs_num, 'sucess_calls': success_logs_num}
        except Exception, ex:
            print ex
            db.session.rollback()
            db.session.commit()
            # recreate tables
            db.drop_all()
            db.create_all()
            return {'error', str(ex)}

api = flask_restful.Api(app)
api.add_resource(PersonDetection, '/person_detection')
api.add_resource(ObjectDetection, '/object_detection')
api.add_resource(Stat, '/stat')
