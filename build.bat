@echo off
echo Compilando el archivo main.py...

:: Verifica que PyInstaller esté en la ruta correcta
if not exist "C:\Users\didie\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\Scripts\pyinstaller.exe" (
    echo Error: PyInstaller no se encuentra en la ruta especificada.
    pause
    exit /b
)

:: Ejecuta PyInstaller
echo Ejecutando PyInstaller...
"C:\Users\didie\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\Scripts\pyinstaller.exe" --onefile --icon=icono.ico "D:\sommerfeld\main.py"

echo Proceso de compilación completado.
pause
