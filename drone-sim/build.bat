@echo off
setlocal

python -m pip install -r requirements.txt
pyinstaller --onefile --windowed --name DroneFlightSimulator main.py

if exist dist\DroneFlightSimulator.exe (
    echo Build complete: dist\DroneFlightSimulator.exe
) else (
    echo Build failed. Check the PyInstaller output above.
)

pause
