#!/bin/bash

echo "Iniciando el Gestor de Citas del Hospital..."

# 1. Iniciar el backend de Python en segundo plano
echo "Levantando el backend (FastAPI/Python)..."
cd backend
./.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# 2. Iniciar el frontend de Angular
echo "Levantando el frontend (Angular)..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "¡Sistema en ejecución!"
echo "Backend PID: $BACKEND_PID (http://localhost:8000)"
echo "Frontend PID: $FRONTEND_PID (http://localhost:4200)"
echo "Presiona Ctrl+C para detener ambos servicios."

# Esperar a que el usuario presione Ctrl+C para cerrar todo
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
