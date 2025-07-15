from datetime import datetime, timezone
from typing import Optional,List
from pydantic import BaseModel, Field
from pydantic import validator


class FollowUpBase(BaseModel):
    elderly_id: int = Field(..., description="老年人ID")
    doctor_id: int = Field(..., description="医生ID")
    follow_up_date: datetime = Field(..., description="随访日期")
    content: str = Field(..., max_length=500, description="随访内容")
    result: str = Field(..., max_length=500, description="随访结果")
    next_follow_up_date: Optional[datetime] = Field(
        None,
        description="下次随访日期"
    )


class FollowUpCreate(FollowUpBase):
    pass


class FollowUpCreate(BaseModel):
    elderly_id: int
    doctor_id: int
    follow_up_date: str
    content: Optional[str] = None
    result: Optional[str] = None
    next_follow_up_date: Optional[datetime] = None
    medication_warning: Optional[str] = Field(
        None,
        max_length=200,
        description="药物禁忌信息"
    )
    # 新增以下字段
    schedule_strategy: Optional[str] = "manual"  # 默认手动
    schedule_interval: Optional[int] = None
    is_recurring: Optional[bool] = False

    @validator('follow_up_date')
    def validate_date(cls, v):
        try:
            # 允许带或不带时区的 ISO 格式
            if 'Z' not in v and '+' not in v:
                v += 'Z'  # 默认 UTC 时区
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError as e:
            raise ValueError(f"日期格式无效，应为 ISO 8601 格式: {e}")


class FollowUpReport(BaseModel):
    elderly_name: str = Field(..., description="老年人姓名")
    doctor_name: str = Field(..., description="医生姓名")
    follow_up_date: str = Field(..., description="随访日期")
    content: str = Field(..., description="随访内容")
    result: str = Field(..., description="随访结果")
    next_follow_up_date: Optional[str] = Field(
        None,
        description="下次随访日期"
    )
    medication_warning: Optional[str] = Field(None, description="用药禁忌")


class ElderlyBase(BaseModel):
    name: str = Field(..., max_length=50, description="姓名")
    gender: str = Field("未知", max_length=10, description="性别")
    age: int = Field(60, description="年龄")
    contact: str = Field("未填写", max_length=20, description="联系方式")
    address: str = Field("未填写", max_length=200, description="住址")


# 在schemas.py中添加以下内容

class ElderlyCreate(ElderlyBase):
    pass


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
    result: Optional[str]
    next_follow_up_date: Optional[datetime]
    # 包含完整的关联对象
    elderly: 'Elderly'  # 使用字符串引用来避免循环引用
    doctor: 'Doctor'

    class Config:
        from_attributes = True

class Elderly(BaseModel):
    id: int
    name: str
    gender: str
    age: int

class Doctor(BaseModel):
    id: int
    name: str
    department: str


class DoctorCreate(DoctorBase):
    pass


class Doctor(DoctorBase):
    id: int

    class Config:
        from_attributes = True
