#include <cuda_runtime.h>

#include <stdio.h>

int main()
{
  int deviceCount = 0;
  cudaError_t error_id = cudaGetDeviceCount(&deviceCount);

  if (error_id != cudaSuccess) {
    /*printf("cudaGetDeviceCount returned %d\n-> %s\n", (int)error_id,*/
           /*cudaGetErrorString(error_id));*/
    /*printf("Result = FAIL\n");*/
    printf("%d\n", -1);
    return 0;
  }
  printf("%d\n", deviceCount);
  return 0;

}
