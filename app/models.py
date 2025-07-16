from pymysql import Date
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, func, Boolean, DECIMAL, Index
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from datetime import datetime,timezone
from .database import Base


class Elderly(Base):
    __tablename__ = "elderly"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)
    gender = Column(Integer, default=1)  # 1 for male, 0 for female
    age = Column(Integer, default=60)
    contact = Column(String(20), default="未填写")
    address = Column(String(200), default="未填写")
    birth_date = Column(Date)  # 添加出生日期字段
    birth_place = Column(String(100))  # 添加出生地字段
    education = Column(String(50))  # 添加教育程度字段
    occupation = Column(String(50))  # 添加职业字段
    follow_ups = relationship("FollowUp", back_populates="elderly")

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True,index= True)
    name = Column(String(50), index=True)
    department = Column(String(50), default="全科")
    contact = Column(String(20), default="未填写")
    follow_ups = relationship("FollowUp", back_populates="doctor")

# models.py
class FollowUp(Base):
    __tablename__ = "follow_ups"
    # 在 models.py 的 FollowUp 类中添加
    __table_args__ = (
        Index('idx_followup_date', 'followup_date'),  # 按日期查询的索引
        Index('idx_elderly_doctor', 'elderly_id', 'doctor_id'),  # 联合索引
        Index('idx_pagination', 'followup_date', 'id')  # 分页专用索引
    )


    id = Column(Integer, primary_key=True, autoincrement=True)
    elderly_id = Column(Integer, ForeignKey("elderly.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    doctor = relationship("Doctor", back_populates="follow_ups", lazy="joined")
    elderly = relationship("Elderly", back_populates="follow_ups", lazy="joined")
    followup_date = Column(DateTime(timezone=True), default=datetime.now)
    next_follow_up_date = Column(DateTime(timezone=True), nullable=True, comment="下次随访日期")
    content = Column(Text, nullable=True)
    medication_warning = Column(Text, nullable=True, comment="用药禁忌提醒")
    height = Column(DECIMAL(6,2), nullable=True)
    weight = Column(DECIMAL(6,2), nullable=True)
    bmi = Column(DECIMAL(6,2), nullable=True)
    waist_circumference = Column(DECIMAL(6,2), nullable=True)
    hip_circumference = Column(DECIMAL(6,2), nullable=True)
    waist_hip_ratio = Column(DECIMAL(6,2), nullable=True)
    systolic_blood_pressure = Column(Integer, nullable=True)
    diastolic_blood_pressure = Column(Integer, nullable=True)
    blood_oxygen = Column(Integer, nullable=True)
    blood_glucose = Column(DECIMAL(6,2), nullable=True)
    pulse_rate = Column(Integer, nullable=True)
    fat = Column(DECIMAL(6,2), nullable=True)
    cholesterol = Column(DECIMAL(6,2), nullable=True)
    fvc = Column(DECIMAL(6,2), nullable=True)
    uric_acid = Column(Integer, nullable=True)
    bone_density = Column(DECIMAL(6,2), nullable=True)
    total_sleep_time = Column(DECIMAL(6,2), nullable=True)
    heart_rate = Column(Integer, nullable=True)
    ecg = Column(String(10), nullable=True)
    water_content = Column(DECIMAL(6,2), nullable=True)
    bmr = Column(Integer, nullable=True)
    temperature = Column(DECIMAL(6,2), nullable=True)
    hemoglobin = Column(DECIMAL(6,2), nullable=True)
    total_cholesterol = Column(DECIMAL(6,2), nullable=True)
    triglycerides = Column(DECIMAL(6,2), nullable=True)
    hdl_cholesterol = Column(DECIMAL(6,2), nullable=True)
    ldl_cholesterol = Column(DECIMAL(6,2), nullable=True)
    urine_wbc = Column(DECIMAL(6,2), nullable=True)
    urine_nitrite = Column(DECIMAL(6,2), nullable=True)
    urine_urobilinogen = Column(DECIMAL(6,2), nullable=True)
    urine_protein = Column(DECIMAL(6,2), nullable=True)
    urine_ph = Column(DECIMAL(6,2), nullable=True)
    urine_blood = Column(DECIMAL(6,2), nullable=True)
    urine_specific_gravity = Column(DECIMAL(6,2), nullable=True)
    urine_ketone = Column(DECIMAL(6,2), nullable=True)
    urine_bilirubin = Column(DECIMAL(6,2), nullable=True)
    urine_glucose = Column(DECIMAL(6,2), nullable=True)
    urine_vitamin_c = Column(DECIMAL(6,2), nullable=True)
    respiration = Column(Integer, nullable=True)
    schedule_strategy = Column(String(50), default='automated')
    is_recurring = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    @hybrid_property
    def followup_date_utc(self):
        return self.followup_date.astimezone(timezone.utc) if self.followup_date else None
