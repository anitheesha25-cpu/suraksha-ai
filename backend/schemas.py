from pydantic import BaseModel, Field

class RegisterIn(BaseModel):
    name: str
    phone: str
    email: str | None = None
    language: str = "en"
    latitude: float | None = None
    longitude: float | None = None

class SOSIn(BaseModel):
    name: str
    latitude: float
    longitude: float
    message: str = "Emergency SOS"

class ReportIn(BaseModel):
    disaster_type: str
    severity: int = Field(ge=1, le=5)
    latitude: float
    longitude: float
    description: str = ""

class VolunteerIn(BaseModel):
    name: str
    skill: str
    latitude: float
    longitude: float
