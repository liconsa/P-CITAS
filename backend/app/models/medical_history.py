from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.core.database import Base  # Ajusta la ruta si tu Base está en otro lado


class MedicalHistory(Base):
    __tablename__ = "medical_histories"

    id = Column(Integer, primary_key=True, index=True)
    # Se relaciona directamente con la tabla users
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)

    blood_type = Column(String(10))
    allergies = Column(Text)
    chronic_diseases = Column(Text)
    disabilities = Column(Text)
    additional_notes = Column(Text)