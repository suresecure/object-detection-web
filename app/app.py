# from __future__ import absolute_import
import os, sys, time, datetime, shutil
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

if not os.path.exists(config.UPLOAD_FOLDER):
    os.makedirs(config.UPLOAD_FOLDER)
# if not os.path.exists(config.UPLOAD_FOLDER_DETECTED):
    # os.makedirs(config.UPLOAD_FOLDER_DETECTED)
# draw_result = False
# if hasattr(config, 'UPLOAD_FOLDER_DRAW'):
    # draw_result = True
# if draw_result and not os.path.exists(config.UPLOAD_FOLDER_DRAW):
    # os.makedirs(config.UPLOAD_FOLDER_DRAW)

app = flask.Flask(__name__)

import settings
the_celery = celery.Celery('tasks')
the_celery.config_from_object(settings)
@the_celery.task(name="tasks.ObjectDetection", queue="important")
def ObjectDetection(imgstream, secure_filename):
    pass

# class ImageManagement(restful.Resource):
    # def post(self):
        # pass
MIN_AVAIL_DISK_SIZE = 40*1024*1024*1024
if hasattr(config, 'MIN_AVAIL_DISK_SIZE'):
    MIN_AVAIL_DISK_SIZE = config.MIN_AVAIL_DISK_SIZE

def remove_oldest_dirs(dirpath, num):
    # get all entries in the directory w/ stats
    entries = (os.path.join(dirpath, fn) for fn in os.listdir(dirpath))
    entries = ((os.stat(path), path) for path in entries)

    # entries = ((stat[ST_CTIME], path)
               # for stat, path in entries if S_ISREG(stat[ST_MODE]))

    # leave only dirs, insert creation date
    entries = ((stat[ST_CTIME], path)
               for stat, path in entries if S_ISDIR(stat[ST_MODE]))
    #NOTE: on Windows `ST_CTIME` is a creation date
    #  but on Unix it could be something else
    #NOTE: use `ST_MTIME` to sort by a modification date

    for cdate, path in sorted(entries)[:num]:
        print 'delete paths: ', path
        shutil.rmtree(path)


# curl -X POST -F image=@hy0.jpg http://localhost:8000/person_detection
class PersonDetection(flask_restful.Resource):
    def post(self):
        # import pdb; pdb.set_trace()  # XXX BREAKPOINT
        # print request.json
        # print request.data
        # x = int(request.args.get("x", x))
        # y = int(request.args.get("y", y))
        # print request.json
        # time.sleep(10)
        # url = request.json['url']
        # x = request.json['x']
        # y = request.json['y']
        # h = request.json['h']
        # w = request.json['w']
        # res = add.apply_async((x, y))

        # print flask.request
        try:
          # print len(flask.request.files)
          imagefile = flask.request.files['image']
          imagestream = imagefile.read()

          filename_ = str(datetime.datetime.now()).replace(' ', '_') + \
              werkzeug.secure_filename(imagefile.filename)

          res = ObjectDetection.apply_async(args=[imagestream, filename_], expires=5)

          stat = os.statvfs(config.UPLOAD_FOLDER)
          avail_size = stat.f_bsize*stat.f_bavail
          if avail_size < MIN_AVAIL_DISK_SIZE:
              remove_oldest_dirs(config.UPLOAD_FOLDER, 24)

          # create dir each hour to store images
          subdir = datetime.datetime.now().strftime('%Y%m%d%H')
          storedir = os.path.join(config.UPLOAD_FOLDER, subdir)
          if not os.path.exists(storedir):
              os.makedirs(storedir)
          filename = os.path.join(storedir, filename_)
          with open(filename, "wb") as f:
              f.write(imagestream)

          result = res.get()
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
          return {'targets':result}
        except celery.exceptions.TaskRevokedError:
          print('time is out')
          return {'error': 'time is out'}
        except AttributeError:
          print('image is invalid')
          return {'error': 'iamge is invalid'}
        except Exception, ex:
          print(ex)
          return {'error':str(ex)}

api = flask_restful.Api(app)
api.add_resource(PersonDetection, '/person_detection')

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    # start_from_terminal(app)
    app.run(debug=True, threaded=True, host='0.0.0.0', port=8000)

# start celery workers
# celery -A app.the_celery worker
# start with gunicorn and gevent
# gunicorn -k=gevent app:app -b 0.0.0.0
