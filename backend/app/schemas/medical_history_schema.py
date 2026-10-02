from pydantic import BaseModel
from typing import Optional

class MedicalHistoryBase(BaseModel):
    blood_type: Optional[str] = None
    allergies: Optional[str] = None
    chronic_diseases: Optional[str] = None
    disabilities: Optional[str] = None
    additional_notes: Optional[str] = None

class MedicalHistoryCreate(MedicalHistoryBase):
    pass

class MedicalHistoryResponse(MedicalHistoryBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True