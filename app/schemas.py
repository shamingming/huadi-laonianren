from datetime import datetime, timezone
from typing import Optional,List,Any,ForwardRef
from pydantic import BaseModel, Field
from pydantic import validator
from sqlalchemy.dialects.postgresql import Any


# schemas.py
from typing import List, Any, Optional, ForwardRef
from pydantic import BaseModel, Field

# 先定义基础模型
class PaginatedResponse(BaseModel):
    items: List[Any]  # 使用直接类型而不是字符串
    total: int
    page: int = Field(ge=1, default=1)
    per_page: int = Field(ge=1, le=100, default=20)
    total_pages: int

# 确保 FollowUpSimple 已经定义
class FollowUpSimple(BaseModel):
    id: int
    elderly_id: int
    doctor_id: int
    followup_date: datetime
    content: Optional[str] = None
    elderly: 'Elderly'  # 使用字符串引用来避免循环引用
    doctor: 'Doctor'

    class Config:
        from_attributes = True

# 然后定义具体响应模型
class FollowUpListResponse(PaginatedResponse):
    items: List[FollowUpSimple]



# schemas.py
class FollowUpBase(BaseModel):
    elderly_id: int = Field(..., description="老年人ID")
    doctor_id: int = Field(..., description="医生ID")
    followup_date: datetime = Field(..., description="随访日期")
    content: Optional[str] = Field(None, max_length=500, description="随访内容")
    height: Optional[float] = Field(None, description="身高")
    weight: Optional[float] = Field(None, description="体重")
    bmi: Optional[float] = Field(None, description="BMI指数")
    waist_circumference: Optional[float] = Field(None, description="腰围")
    hip_circumference: Optional[float] = Field(None, description="臀围")
    waist_hip_ratio: Optional[float] = Field(None, description="腰臀比")
    systolic_blood_pressure: Optional[int] = Field(None, description="收缩压")
    diastolic_blood_pressure: Optional[int] = Field(None, description="舒张压")
    blood_oxygen: Optional[int] = Field(None, description="血氧(%)")
    blood_glucose: Optional[float] = Field(None, description="血糖(mmol/L)")
    pulse_rate: Optional[int] = Field(None, description="脉率")
    fat: Optional[float] = Field(None, description="脂肪")
    cholesterol: Optional[float] = Field(None, description="胆固醇")
    fvc: Optional[float] = Field(None, description="用力肺活量(L)")
    uric_acid: Optional[int] = Field(None, description="尿酸")
    bone_density: Optional[float] = Field(None, description="骨密度")
    total_sleep_time: Optional[float] = Field(None, description="睡眠总时长")
    heart_rate: Optional[int] = Field(None, description="心率")
    ecg: Optional[str] = Field(None, description="心电")
    water_content: Optional[float] = Field(None, description="水分含量")
    bmr: Optional[int] = Field(None, description="基础代谢率")
    temperature: Optional[float] = Field(None, description="体温")
    hemoglobin: Optional[float] = Field(None, description="血红蛋白")
    total_cholesterol: Optional[float] = Field(None, description="总胆固醇")
    triglycerides: Optional[float] = Field(None, description="甘油三酯")
    hdl_cholesterol: Optional[float] = Field(None, description="高密度脂蛋白胆固醇")
    ldl_cholesterol: Optional[float] = Field(None, description="低密度脂蛋白胆固醇")
    urine_wbc: Optional[float] = Field(None, description="白细胞(尿常规)")
    urine_nitrite: Optional[float] = Field(None, description="亚硝酸盐(尿常规)")
    urine_urobilinogen: Optional[float] = Field(None, description="尿胆原(尿常规)")
    urine_protein: Optional[float] = Field(None, description="蛋白质(尿常规)")
    urine_ph: Optional[float] = Field(None, description="PH值(尿常规)")
    urine_blood: Optional[float] = Field(None, description="潜血(尿常规)")
    urine_specific_gravity: Optional[float] = Field(None, description="比重(尿常规)")
    urine_ketone: Optional[float] = Field(None, description="酮体(尿常规)")
    urine_bilirubin: Optional[float] = Field(None, description="胆红素(尿常规)")
    urine_glucose: Optional[float] = Field(None, description="葡萄糖(尿常规)")
    urine_vitamin_c: Optional[float] = Field(None, description="维生素C(尿常规)")
    respiration: Optional[int] = Field(None, description="呼吸")
    schedule_strategy: Optional[str] = Field("automated", description="随访策略")
    is_recurring: Optional[bool] = Field(False, description="是否定期随访")

    @validator('followup_date')
    def validate_date(cls, v):
        if isinstance(v, datetime):
            return v
        try:
            return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise ValueError("日期格式应为 YYYY-MM-DD HH:mm:ss")

class FollowUpCreate(FollowUpBase):
    pass

class FollowUp(FollowUpBase):
    id: int
    elderly: 'Elderly'
    doctor: 'Doctor'
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class FollowUpCreate(BaseModel):
    elderly_id: int
    doctor_id: int
    follow_up_date: str
    content: Optional[str] = None
    next_follow_up_date: Optional[str] = None
    medication_warning: Optional[str] = Field(
        None,
        max_length=200,
        description="药物禁忌信息"
    )
    # 新增所有健康指标字段
    height: Optional[float] = None
    weight: Optional[float] = None
    bmi: Optional[float] = None
    waist_circumference: Optional[float] = None
    hip_circumference: Optional[float] = None
    waist_hip_ratio: Optional[float] = None
    systolic_blood_pressure: Optional[int] = None
    diastolic_blood_pressure: Optional[int] = None
    blood_oxygen: Optional[int] = None
    blood_glucose: Optional[float] = None
    pulse_rate: Optional[int] = None
    fat: Optional[float] = None
    cholesterol: Optional[float] = None
    fvc: Optional[float] = None
    uric_acid: Optional[int] = None
    bone_density: Optional[float] = None
    total_sleep_time: Optional[float] = None
    heart_rate: Optional[int] = None
    ecg: Optional[str] = None
    water_content: Optional[float] = None
    bmr: Optional[int] = None
    temperature: Optional[float] = None
    hemoglobin: Optional[float] = None
    total_cholesterol: Optional[float] = None
    triglycerides: Optional[float] = None
    hdl_cholesterol: Optional[float] = None
    ldl_cholesterol: Optional[float] = None
    urine_wbc: Optional[float] = None
    urine_nitrite: Optional[float] = None
    urine_urobilinogen: Optional[float] = None
    urine_protein: Optional[float] = None
    urine_ph: Optional[float] = None
    urine_blood: Optional[float] = None
    urine_specific_gravity: Optional[float] = None
    urine_ketone: Optional[float] = None
    urine_bilirubin: Optional[float] = None
    urine_glucose: Optional[float] = None
    urine_vitamin_c: Optional[float] = None
    respiration: Optional[int] = None
    schedule_strategy: Optional[str] = "manual"
    schedule_interval: Optional[int] = None
    is_recurring: Optional[bool] = False

    @validator('follow_up_date')
    def validate_date(cls, v):
        if isinstance(v, datetime):
            return v
        try:
            return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise ValueError("日期格式应为 YYYY-MM-DD HH:mm:ss")

    @validator('next_follow_up_date')
    def validate_next_date(cls, v):
        if v is None:
            return None
        if isinstance(v, datetime):
            return v
        try:
            return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise ValueError("日期格式应为 YYYY-MM-DD HH:mm:ss")


class FollowUpReport(BaseModel):
    elderly_name: str = Field(..., description="老年人姓名")
    doctor_name: str = Field(..., description="医生姓名")
    follow_up_date: str = Field(..., description="随访日期")
    content: str = Field(..., description="随访内容")
    next_follow_up_date: Optional[str] = Field(
        None,
        description="下次随访日期"
    )
    medication_warning: Optional[str] = Field(None, description="用药禁忌")


class ElderlyBase(BaseModel):
    id: int
    name: str = Field(..., max_length=50, description="姓名")
    gender: int = Field(..., description="性别（1: 男, 0: 女）")
    age: int = Field(..., description="年龄")
    contact: str = Field(..., max_length=20, description="联系方式")
    address: str = Field(..., max_length=200, description="住址")
    birth_date: str = Field(..., description="出生日期")
    birth_place: str = Field(..., max_length=100, description="出生地")
    education: str = Field(..., max_length=50, description="教育程度")
    occupation: str = Field(..., max_length=50, description="职业")

    @validator('birth_date', pre=True)
    def parse_birth_date(cls, value):
        if isinstance(value, int):
            return f"{value:08d}"[:4] + '-' + f"{value:08d}"[4:6] + '-' + f"{value:08d}"[6:8]
        return value

    class Config:
        from_attributes = True
# 在schemas.py中添加以下内容

class ElderlyCreate(ElderlyBase):
    gender: int  # 修改为 int 类型

class ElderlyUpdate(ElderlyBase):
    gender: int  # 修改为 int 类型

class Elderly(ElderlyBase):
    id: int


    class Config:
        from_attributes = True


class DoctorBase(BaseModel):
    name: str = Field(..., max_length=50, description="姓名")
    department: str = Field("全科", max_length=50, description="科室")
    contact: str = Field("未填写", max_length=20, description="联系方式")


# schemas.py 修正FollowUp模型
# schemas.py
class FollowUp(BaseModel):
    id: int
    elderly_id: int
    doctor_id: int
    follow_up_date: datetime
    content: Optional[str]

    next_follow_up_date: Optional[datetime]
    # 包含完整的关联对象
    elderly: 'Elderly'  # 使用字符串引用来避免循环引用
    doctor: 'Doctor'

    class Config:
        from_attributes = True

class Elderly(BaseModel):
    id: int
    name: str
    gender: int  # 这里定义为字符串类型
    age: int
    contact: str
    address: str
    birth_date: str
    birth_place: str
    education: str
    occupation: str

    @validator('birth_date', pre=True)
    def parse_birth_date(cls, value):
        if isinstance(value, int):
            return f"{value:08d}"[:4] + '-' + f"{value:08d}"[4:6] + '-' + f"{value:08d}"[6:8]
        return value

    class Config:
        from_attributes = True

class Doctor(BaseModel):
    id: int
    name: str
    department: str


class DoctorCreate(DoctorBase):
    pass
# 在原有 DoctorCreate 类下方添加
class DoctorUpdate(DoctorBase):
    pass

class Doctor(DoctorBase):
    id: int

    class Config:
        from_attributes = True


