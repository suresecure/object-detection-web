# start with gunicorn and gevent
./cudautil/get_cuda_device_count > device_count.txt
gunicorn -k=gevent app:app -b 0.0.0.0:8090
