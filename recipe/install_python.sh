#!/bin/bash

set -ex

mkdir -p ${SP_DIR}
cp api/gmsh.py ${SP_DIR}/gmsh.py
mkdir -p "${SP_DIR}/gmsh-${PKG_VERSION}.dist-info"
cp build/METADATA "${SP_DIR}/gmsh-${PKG_VERSION}.dist-info/METADATA"
