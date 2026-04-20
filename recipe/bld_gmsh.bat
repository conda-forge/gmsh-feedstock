:: Needed so we can find stdint.h from msinttypes.
set LIB=%LIBRARY_LIB%;%LIB%
set LIBPATH=%LIBRARY_LIB%;%LIBPATH%
set INCLUDE=%LIBRARY_INC%;%INCLUDE%

mkdir build
cd build

if "%openmp_impl%" == "intel" (
    set "OPENMP_ARGS=-DOpenMP_CXX_LIB_NAMES=libiomp5md"
    set "OPENMP_ARGS=%OPENMP_ARGS% -DOpenMP_CXX_FLAGS=/clang:-fopenmp=libiomp5"
    set "OPENMP_ARGS=%OPENMP_ARGS% -DOpenMP_libiomp5md_LIBRARY=%LIBRARY_LIB%\libiomp5md.lib"
    set "CONFIG_ARGS=-D "CMAKE_C_FLAGS=/O2 /arch:AVX2 -DWIN32" -D "CMAKE_CXX_FLAGS=/O2 /arch:AVX2 -DWIN32""
) else (
    set "OPENMP_ARGS="
    set "CONFIG_ARGS="
)

:: Configure.
cmake -G "Visual Studio 17 2022" -A x64 -T ClangCL ^
      -D CMAKE_POLICY_VERSION_MINIMUM=3.5 ^
      -D CMAKE_INSTALL_PREFIX=%LIBRARY_PREFIX% ^
      %CONFIG_ARGS% ^
      -D ENABLE_OS_SPECIFIC_INSTALL=OFF ^
      -D ENABLE_BUILD_DYNAMIC=ON ^
      -D ENABLE_BUILD_SHARED=ON ^
      -D ENABLE_PETSC=OFF ^
      -D ENABLE_SLEPC=OFF ^
      -D BLAS_LAPACK_LIBRARIES=%LIBRARY_PREFIX%\lib\lapack.lib;%LIBRARY_PREFIX%\lib\blas.lib ^
      -D GMSH_RELEASE=1 ^
      -D ENABLE_OPENMP=ON ^
      %OPENMP_ARGS% ^
      -D ENABLE_CAIRO=1 ^
      -D ENABLE_MED=1 ^
      %SRC_DIR%
if errorlevel 1 exit 1

:: Build and Install.
cmake --build . --config Release --target install
if errorlevel 1 exit 1

del %LIBRARY_PREFIX%\lib\gmsh.py
move %LIBRARY_PREFIX%\lib\gmsh.dll %LIBRARY_PREFIX%\bin\
