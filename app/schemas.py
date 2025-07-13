from datetime import datetime, timezone
from typing import Optional
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
    follow_up_date: datetime
    content: str = Field(..., max_length=500)
    result: str = Field(..., max_length=500)
    next_follow_up_date: Optional[datetime] = None
    medication_warning: Optional[str] = Field(
        None,
        max_length=200,
        description="药物禁忌信息"
    )

    @validator('follow_up_date')
    def validate_future_date(cls, v):
        if v and v < datetime.now(timezone.utc):
            raise ValueError("随访日期不能是过去时间")
        return v


class FollowUp(FollowUpBase):
    id: int = Field(..., description="随访记录ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True  # 替换原来的orm_mode=True


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