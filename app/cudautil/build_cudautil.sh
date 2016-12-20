gcc cudautilmodule.c `pkg-config --cflags --libs python-2.7 cudart-7.5` --shared -fPIC -o cudautilmodule.so
gcc get_cuda_device_count.c `pkg-config --cflags --libs cudart-7.5` -o get_cuda_device_count
