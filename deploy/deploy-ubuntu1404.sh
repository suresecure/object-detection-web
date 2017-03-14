#1 add cuda lib64 to ld library path
#edit ldconfig-cuda/cuda.conf
sudo cp ldconfig-cuda/cuda.conf /etc/ld.so.conf.d/
sudo ldconfig

#2 add celery worker to /etc/init
sudo cp celeryobjdetd/init.d/celeryobjdetd /etc/init.d/
#edit line 12,22,35,36 of service configuration file
sudo cp celeryobjdetd/default/celeryobjdetd /etc/default/
#to add run on startup
sudo update-rc.d celeryobjdetd defaults 
#to remove run on startup
#sudo update-rc.d -f celeryobjdetd remove

#3 gunicorn auto start using upstart 
#edit line 9 of gunicorn-objdet/objdet-gunicorn
sudo cp gunicorn-upstart /etc/init/

#3 tornado auto start using upstart
#edit line 9 of tornado-upstart/objdet-tornado.conf
sudo cp tornado-upstart/objdet-tornado.conf /etc/init

#4 install and config nginx
sudo apt-get install nginx
sudo cp nginx/sites-available/default /etc/nginx/sites-available/
