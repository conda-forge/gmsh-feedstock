:: Needed so we can find stdint.h from msinttypes.
set LIB=%LIBRARY_LIB%;%LIB%
set LIBPATH=%LIBRARY_LIB%;%LIBPATH%
set INCLUDE=%LIBRARY_INC%;%INCLUDE%

mkdir build
cd build

:: Configure.
cmake -G "Visual Studio 17 2022" -A x64 -T ClangCL ^
      -D CMAKE_POLICY_VERSION_MINIMUM=3.5 ^
      -D CMAKE_INSTALL_PREFIX=%LIBRARY_PREFIX% ^
      -D ENABLE_OS_SPECIFIC_INSTALL=OFF ^
      -D ENABLE_BUILD_DYNAMIC=ON ^
      -D ENABLE_BUILD_SHARED=ON ^
      -D ENABLE_PETSC=OFF ^
      -D ENABLE_SLEPC=OFF ^
      -D BLAS_LAPACK_LIBRARIES=%LIBRARY_PREFIX%\lib\lapack.lib;%LIBRARY_PREFIX%\lib\blas.lib ^
      -D GMSH_RELEASE=1 ^
      -D ENABLE_OPENMP=ON ^
      -D OpenMP_C_LIB_NAMES=libiomp5md ^
      -D OpenMP_CXX_LIB_NAMES=libiomp5md ^
      -D OpenMP_libiomp5md_LIBRARY=%LIBRARY_PREFIX%\lib\libiomp5md.lib ^
      -D ENABLE_CAIRO=1 ^
      -D ENABLE_MED=1 ^
      ..
if errorlevel 1 exit 1

:: Build.
cmake --build . --target package
if errorlevel 1 exit 1

:: Test.
:: ctest
:: if errorlevel 1 exit 1

:: Install.
cmake --build . --target install
if errorlevel 1 exit 1

del %LIBRARY_PREFIX%\lib\gmsh.py
move %LIBRARY_PREFIX%\lib\gmsh.dll %LIBRARY_PREFIX%\bin\
