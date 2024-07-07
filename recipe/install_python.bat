mkdir %SP_DIR%
if errorlevel 1 exit 1

copy api\gmsh.py %SP_DIR%\gmsh.py
if errorlevel 1 exit 1
