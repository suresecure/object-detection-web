# start with gunicorn and gevent
gunicorn -k=gevent app:app -b 0.0.0.0:8080
