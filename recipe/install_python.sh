#!/bin/bash

set -ex

mkdir -p ${SP_DIR}
cp api/gmsh.py ${SP_DIR}/gmsh.py
cp  build/METADATA ${SP_DIR}/gmsh-${PKG_VERSION}.dist-info
