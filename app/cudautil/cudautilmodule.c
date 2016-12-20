#include <Python.h>
#include <cuda_runtime.h>
/*
 * Function to be called from Python
 */
static PyObject *py_GetCudaDeviceCount(PyObject *self, PyObject *args) {
  int deviceCount = 0;
  cudaError_t error_id = cudaGetDeviceCount(&deviceCount);

  if (error_id != cudaSuccess) {
    printf("cudaGetDeviceCount returned %d\n-> %s\n", (int)error_id,
           cudaGetErrorString(error_id));
    printf("Result = FAIL\n");
    return Py_BuildValue("i", -1);
  }
  return Py_BuildValue("i", deviceCount);
}

/*
 * Bind Python function names to our C functions
 */
static PyMethodDef simplecudamodule_methods[] = {
    {"GetCudaDeviceCount", py_GetCudaDeviceCount, METH_VARARGS}, {NULL, NULL}};

/*
 * Python calls this to let us initialize our module
 */
void initcudautil() {
  (void)Py_InitModule("cudautil", simplecudamodule_methods);
}
