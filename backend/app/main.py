import sys
from pathlib import Path

# Asegurar que el directorio raíz del backend esté en sys.path al ejecutar directamente
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi import FastAPI
from app.core.database import engine, Base
from fastapi.middleware.cors import CORSMiddleware
from app.models import user, appointment, jornada, prescription
from app.models.medical_history import MedicalHistory
from app.api import routes_auth, routes_patient, routes_doctor, routes_receptionist, routes_admin

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Gestor de Citas Médicas API")

# Registro de rutas modulares
app.include_router(routes_auth.router)
app.include_router(routes_patient.router)
app.include_router(routes_doctor.router)
app.include_router(routes_receptionist.router)
app.include_router(routes_admin.router)

# Configuración estricta de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
