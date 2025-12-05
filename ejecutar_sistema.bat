@echo off
cd /d "C:\Users\gvar_\OneDrive\Desktop\Final"

echo Iniciando backend...
start cmd /k "cd backend && venv311\Scripts\activate && cd app && python main.py"

echo Iniciando frontend...
start cmd /k "cd frontend && npm start"

echo Servicios iniciados.
pause