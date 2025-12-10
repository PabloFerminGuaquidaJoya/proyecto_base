@echo off
echo Configurando entorno virtual para el proyecto SENA...

REM Crear entorno virtual
python -m venv venv

REM Activar entorno virtual
call venv\Scripts\activate

REM Instalar dependencias
pip install -r requirements.txt

echo.
echo Entorno configurado. Para activar el entorno virtual, ejecuta:
echo venv\Scripts\activate

pause