from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Elderly(Base):
    __tablename__ = "elderly"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), default="未命名老人")
    gender = Column(String(10), default="未知")
    age = Column(Integer, default=60)
    contact = Column(String(20), default="未填写")
    address = Column(String(200), default="未填写")
    follow_ups = relationship("FollowUp", back_populates="elderly")


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), default="未命名医生")
    department = Column(String(50), default="全科")
    contact = Column(String(20), default="未填写")
    follow_ups = relationship("FollowUp", back_populates="doctor")


class FollowUp(Base):
    __tablename__ = "follow_ups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    elderly_id = Column(Integer, ForeignKey("elderly.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id"))  # 确保这一行存在
    doctor = relationship("Doctor", back_populates="follow_ups", lazy="joined")
    elderly = relationship("Elderly", back_populates="follow_ups", lazy="joined")
    follow_up_date = Column(DateTime(timezone=True), default=datetime.now)
    content = Column(Text, nullable=True)
    result = Column(Text, nullable=True)
    next_follow_up_date = Column(DateTime(timezone=True), nullable=True)
    medication_warning = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())