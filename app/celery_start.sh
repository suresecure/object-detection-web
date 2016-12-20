# start celery workers
export C_FORCE_ROOT=1
./cudautil/get_cuda_device_count > device_count.txt
celery -A tasks.the_celery worker
