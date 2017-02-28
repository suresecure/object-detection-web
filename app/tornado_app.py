import tornado.ioloop
import tornado.web

class ObjectDetectionHandler(tornado.web.RequestHandler):
    def post(self):
        image_bytestr = self.request.files['image'][0].body
        filename = self.request.files['image'][0].filename
        detection_result = {}
        return_code = -1
        try:
          # print len(flask.request.files)
          # imagefile = flask.request.files['image']
          # imagestream = imagefile.read()
          imagestream = image_bytestr
          filename_ = str(datetime.datetime.now()).replace(' ', '_') + \
              werkzeug.secure_filename(filename)

          res = object_detection_task.apply_async(
              args=[imagestream, filename_], expires=5)

          save_file()

          result = res.get()
          detection_result = {'targets': result}
        except celery.exceptions.TaskRevokedError:
          print('time is out')
          return_code = 0
          detection_result = {'error': 'time is out'}
        except Exception, ex:
          print(ex)
          return_code = 1
          detection_result = {'error': str(ex)}

        # try:
          # access_log = AccessLog()
          # access_log.return_code = return_code
          # db.session.add(access_log)
          # db.session.commit()
        # except Exception, ex:
            # print ex
            # db.session.rollback()
            # db.session.commit()
            # db.drop_all()
            # db.create_all()

        self.write(detection_result)

def make_app():
    return tornado.web.Application([
        (r"/person_detection", ObjectDetectionHandler),
        (r"/object_detection", ObjectDetectionHandler)
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8090)
    tornado.ioloop.IOLoop.current().start()
