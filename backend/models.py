from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    phone: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(180), nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="en")
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class SOSAlert(Base):
    __tablename__ = "sos_alerts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    message: Mapped[str] = mapped_column(Text, default="Emergency SOS")
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class IncidentReport(Base):
    __tablename__ = "incident_reports"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    disaster_type: Mapped[str] = mapped_column(String(60))
    severity: Mapped[int] = mapped_column(Integer, default=3)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    description: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Volunteer(Base):
    __tablename__ = "volunteers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    skill: Mapped[str] = mapped_column(String(80))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    available: Mapped[bool] = mapped_column(Boolean, default=True)

class Resource(Base):
    __tablename__ = "resources"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    required: Mapped[int] = mapped_column(Integer, default=0)
    available: Mapped[int] = mapped_column(Integer, default=0)
