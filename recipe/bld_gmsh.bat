:: Needed so we can find stdint.h from msinttypes.
set LIB=%LIBRARY_LIB%;%LIB%
set LIBPATH=%LIBRARY_LIB%;%LIBPATH%
set INCLUDE=%LIBRARY_INC%;%INCLUDE%

mkdir build
cd build

:: Configure.
cmake -G "NMake Makefiles" ^
      -D CMAKE_INSTALL_PREFIX=%LIBRARY_PREFIX% ^
      -D ENABLE_OS_SPECIFIC_INSTALL=OFF ^
      -D ENABLE_BUILD_DYNAMIC=ON ^
      -D ENABLE_BUILD_SHARED=ON ^
      -D ENABLE_PETSC=OFF ^
      -D ENABLE_SLEPC=OFF ^
      -D ENABLE_HXT=0 ^
      -D BLAS_LAPACK_LIBRARIES=%LIBRARY_PREFIX%\lib\lapack.lib;%LIBRARY_PREFIX%\lib\blas.lib ^
      -D GMSH_RELEASE=1 ^
      -D ENABLE_OPENMP=0 ^
      %SRC_DIR%
if errorlevel 1 exit 1

:: Build.
nmake package
if errorlevel 1 exit 1

:: Test.
:: ctest
:: if errorlevel 1 exit 1

:: Install.
nmake install
if errorlevel 1 exit 1

rm %LIBRARY_PREFIX%\lib\gmsh.py
move %LIBRARY_PREFIX%\lib\gmsh.dll %LIBRARY_PREFIX%\bin\
