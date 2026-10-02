from fastapi import FastAPI
from app.core.database import engine, Base
from fastapi.middleware.cors import CORSMiddleware
from app.models import user, appointment
from app.models.medical_history import MedicalHistory
# 1. Importa tu archivo de rutas de recepcionista (ajusta la ruta si está en otra carpeta, por ejemplo app.api o app.routers)
from app.api import routes_auth, routes_patient, routes_doctor, routes_receptionist


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Gestor de Citas Médicas API")

# Registro de rutas modulares
app.include_router(routes_auth.router)
app.include_router(routes_patient.router)
app.include_router(routes_doctor.router)
# 2. Regístralo aquí junto con las demás rutas
app.include_router(routes_receptionist.router)

app.include_router(routes_doctor.router)

# Configuración estricta de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)