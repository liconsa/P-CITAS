import sys
from pathlib import Path
from datetime import datetime, timedelta

# Asegurar que el directorio raíz del backend esté en sys.path
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.database import SessionLocal, engine, Base
from app.models.user import User, DoctorProfile, RolUsuario
from app.models.jornada import Jornada
from app.models.appointment import Appointment
from app.models.prescription import Prescription
from app.models.medical_history import MedicalHistory

def reset_and_seed_db():
    print("Recreando esquema completo de base de datos (con recetas y sin caja)...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    print("Conectando a la base de datos...")
    db = SessionLocal()
    try:
        # 1. Crear Usuarios para cada Rol
        print("Creando nuevos usuarios para cada rol...")

        # Administrador
        admin = User(
            nombre="Administrador General",
            correo="admin@hospital.com",
            hashed_password="admin123",
            rol=RolUsuario.ADMIN,
            activo=True
        )
        db.add(admin)
        db.flush()

        # Recepcionista
        recepcionista = User(
            nombre="Ana López (Recepcionista)",
            correo="recepcion@hospital.com",
            hashed_password="recep123",
            rol=RolUsuario.RECEPCIONISTA,
            activo=True
        )
        db.add(recepcionista)

        # Paciente 1 - Juan Pérez
        paciente1 = User(
            nombre="Juan Pérez",
            correo="paciente@hospital.com",
            hashed_password="paciente123",
            rol=RolUsuario.PACIENTE,
            activo=True
        )
        # Paciente 2 - María González
        paciente2 = User(
            nombre="María González",
            correo="maria@hospital.com",
            hashed_password="paciente123",
            rol=RolUsuario.PACIENTE,
            activo=True
        )
        db.add(paciente1)
        db.add(paciente2)
        db.flush()

        # Expedientes clínicos para los pacientes
        historial1 = MedicalHistory(
            user_id=paciente1.id,
            blood_type="O+",
            allergies="Penicilina, Mariscos",
            chronic_diseases="Hipertensión controlada",
            disabilities="Ninguna",
            additional_notes="Paciente deportista, sin cirugías previas."
        )
        historial2 = MedicalHistory(
            user_id=paciente2.id,
            blood_type="A+",
            allergies="Polen, AINES (Ibuprofeno)",
            chronic_diseases="Asma leve",
            disabilities="Ninguna",
            additional_notes="Chequeo médico anual regular."
        )
        db.add(historial1)
        db.add(historial2)

        # Médicos con sus respectivos perfiles y especialidades
        doctores_data = [
            {
                "nombre": "Dr. Roberto García",
                "correo": "dr.garcia@hospital.com",
                "password": "medico123",
                "especialidad": "Cardiología"
            },
            {
                "nombre": "Dra. Elena Martínez",
                "correo": "dra.martinez@hospital.com",
                "password": "medico123",
                "especialidad": "Pediatría"
            },
            {
                "nombre": "Dr. Carlos Rodríguez",
                "correo": "dr.rodriguez@hospital.com",
                "password": "medico123",
                "especialidad": "Medicina General"
            },
            {
                "nombre": "Dra. Sofía Ramírez",
                "correo": "dra.ramirez@hospital.com",
                "password": "medico123",
                "especialidad": "Dermatología"
            }
        ]

        medicos_creados = []
        for doc in doctores_data:
            user_doc = User(
                nombre=doc["nombre"],
                correo=doc["correo"],
                hashed_password=doc["password"],
                rol=RolUsuario.MEDICO,
                activo=True
            )
            db.add(user_doc)
            db.flush()

            perfil = DoctorProfile(
                user_id=user_doc.id,
                especialidad=doc["especialidad"]
            )
            db.add(perfil)
            medicos_creados.append(user_doc)

        db.commit()

        # 2. Crear jornadas/postulaciones iniciales de horarios para los médicos
        print("Creando jornadas/horarios disponibles para los médicos...")
        hoy = datetime.now()
        horas = ["08:00", "09:00", "10:00", "11:00", "12:00", "15:00", "16:00", "17:00"]
        total_jornadas = 0

        # Sembrar para los próximos 7 días a partir de 3 días en el futuro (cumple anticipación >48h)
        for dia_offset in range(3, 10):
            fecha_dia = (hoy + timedelta(days=dia_offset)).date()
            for doc in medicos_creados:
                for h_str in horas:
                    h, m = map(int, h_str.split(":"))
                    dt = datetime(fecha_dia.year, fecha_dia.month, fecha_dia.day, h, m)
                    jornada = Jornada(
                        medico_id=doc.id,
                        fecha_hora=dt,
                        duracion_minutos=60,
                        estado="DISPONIBLE",
                        asignado_por_id=admin.id
                    )
                    db.add(jornada)
                    total_jornadas += 1

        db.commit()
        print(f"Base de datos reiniciada con éxito!")
        print(f"- Usuarios creados:")
        print(f"  * Administrador (ID: {admin.id}): admin@hospital.com / admin123")
        print(f"  * Recepcionista (ID: {recepcionista.id}): recepcion@hospital.com / recep123")
        print(f"  * Paciente Juan Pérez (ID: {paciente1.id}): paciente@hospital.com / paciente123")
        print(f"  * Paciente María González (ID: {paciente2.id}): maria@hospital.com / paciente123")
        print(f"  * Médicos ({len(medicos_creados)}):")
        for doc in doctores_data:
            print(f"    - {doc['nombre']} ({doc['especialidad']}): {doc['correo']} / {doc['password']}")
        print(f"- Jornadas iniciales creadas: {total_jornadas} slots disponibles")

    except Exception as e:
        db.rollback()
        print(f"Error al sembrar base de datos: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    reset_and_seed_db()
