gcc cudautilmodule.c `pkg-config --cflags --libs python-2.7 cudart-6.5` --shared -fPIC -o cudautilmodule.so
