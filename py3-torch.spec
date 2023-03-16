### RPM external py3-torch 1.13.1
## IMPORT build-with-pip
## INCLUDE cuda-flags

%define tag v%{realversion}
%define branch release/1.13

%define source0 git+https://github.com/pytorch/pytorch.git?obj=%{branch}/%{tag}&export=%{n}-%{realversion}&submodules=1&output=/%{n}-%{realversion}.tgz
#Patch0: py3-torch-cpp-externsion-ppc64 - TODO: is it needed? 1st part doesn't apply

BuildRequires: cmake ninja
Requires: eigen fxdiv numactl openmpi protobuf psimd py3-astunparse py3-cffi py3-future py3-numpy py3-pip py3-protobuf py3-pybind11 py3-PyYAML py3-requests py3-setuptools py3-six py3-tqdm py3-typing-extensions py3-wheel python3 cuda cudnn OpenBLAS

%define PipPreBuildPy \
%if "%{?compiling_processes:set}" == "set" \
export MAX_JOBS=%compiling_processes \
%endif \
export COLORIZE_OUTPUT=OFF \
export BUILD_TEST=OFF \
export USE_CUDA=ON \
export TORCH_CUDA_ARCH_LIST="%{cuda_arch_float}" \
 \
export CUDNN_INCLUDE_DIR=${CUDNN_ROOT}/include \
export CUDNN_LIBRARY=${CUDNN_ROOT}/lib64/libcudnn.so \
 \
export USE_NCCL=OFF \
export USE_FBGEMM=OFF \
export USE_KINETO=OFF \
export USE_MAGMA=OFF \
export USE_METAL=OFF \
export USE_MPS=OFF \
export USE_BREAKPAD=OFF \
export USE_NNPACK=OFF \
export USE_QNNPACK=OFF \
export USE_PYTORCH_QNNPACK=OFF \
export USE_XNNPACK=OFF \
 \
export USE_NUMA=ON \
export NUMA_ROOT_DIR=${NUMACTL_ROOT} \
 \
export USE_NUMPY=ON \
export USE_OPENMP=ON \
export USE_QNNPACK=OFF \
export USE_VALGRIND=OFF \
export USE_XNNPACK=OFF \
export USE_MKLDNN=OFF \
export USE_DISTRIBUTED=OFF \
export USE_MPI=ON \
export USE_GLOO=OFF \
export USE_TENSORPIPE=OFF \
export ONNX_ML=ON \
 \
export PYTORCH_BUILD_VERSION=%{realversion} \
export PYTORCH_BUILD_NUMBER=0 \
export BLAS=OpenBLAS \
export WITH_BLAS=open \
 \
export BUILD_CUSTOM_PROTOBUF=OFF \
export USE_SYSTEM_EIGEN_INSTALL=ON \
export pybind11_DIR=${PY3_PYBIND11_ROOT}/lib/python%{cms_python3_major_minor_version}/site-packages/pybind11/share/cmake/pybind11 \
export pybind11_INCLUDE_DIR=${PY3_PYBIND11_ROOT}/lib/python%{cms_python3_major_minor_version}/site-packages/pybind11/include \
export USE_SYSTEM_PYBIND11=ON \
 \
export USE_SYSTEM_PSIMD=ON \
export USE_SYSTEM_FXDIV=ON \
export USE_SYSTEM_BENCHMARK=ON \
export CMAKE_PREFIX_PATH="%{cmake_prefix_path}"

%post
%{relocateConfig}lib/python%{cms_python3_major_minor_version}/site-packages/torch/share/cmake/ATen/ATenConfig.cmake

#export USE_SYSTEM_PTHREADPOOL=ON \

# For ROCm, pre-build
# NOTICE: can't build with both cuda and rocm
# python @{_builddir}/tools/amd_build/build_amd.py