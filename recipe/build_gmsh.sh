#!/bin/bash
# see http://conda.pydata.org/docs/build.html for hacking instructions.

set -ex

if [[ "$c_compiler" == "gcc" ]]; then
  export PATH="${PATH}:${BUILD_PREFIX}/${HOST}/sysroot/usr/lib:${BUILD_PREFIX}/${HOST}/sysroot/usr/include"
fi

# unpack.
mkdir build
cd build

# build.
cmake ${CMAKE_ARGS} \
    -DCMAKE_INSTALL_PREFIX=$PREFIX \
    -DCMAKE_PREFIX_PATH=$PREFIX \
    -DCMAKE_INSTALL_LIBDIR=lib \
    -DENABLE_BUILD_DYNAMIC=ON \
    -DENABLE_BUILD_SHARED=ON \
    -DENABLE_OS_SPECIFIC_INSTALL=OFF \
    -DENABLE_PETSC=OFF \
    -DENABLE_SLEPC=OFF \
    -DBLAS_LAPACK_LIBRARIES="$PREFIX/lib/libblas${SHLIB_EXT};$PREFIX/lib/liblapack${SHLIB_EXT}" \
    -DGMSH_RELEASE=1 \
    -DENABLE_TOUCHBAR=OFF \
    ..

make -j${CPU_COUNT}

make install

rm -f ${PREFIX}/lib/gmsh.py
# vim: set ai et nu:
