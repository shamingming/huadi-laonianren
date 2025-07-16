from datetime import datetime, timezone,timedelta
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from . import models, schemas
import logging
from contextlib import contextmanager
from sqlalchemy.orm import joinedload

from .schemas import Elderly

logger = logging.getLogger(__name__)

@contextmanager
def db_session_scope(db: Session):
    """提供数据库会话作用域管理"""
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"数据库操作失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="数据库操作失败"
        )

def get_follow_up(db: Session, follow_up_id: int):
    """获取单个随访记录"""
    try:
        return db.query(models.FollowUp).filter(models.FollowUp.id == follow_up_id).first()
    except SQLAlchemyError as e:
        logger.error(f"获取随访记录失败 ID:{follow_up_id}, 错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取随访记录失败"
        )



# crud.py 的get_follow_ups方法
# crud.py
# 在crud.py中的get_follow_ups_paginated方法
def get_follow_ups_paginated(db: Session, page: int, per_page: int, elderly_id: int = None, doctor_id: int = None):
    try:
        query = db.query(models.FollowUp).options(
            joinedload(models.FollowUp.elderly),
            joinedload(models.FollowUp.doctor)
        )

        if elderly_id:
            query = query.filter(models.FollowUp.elderly_id == elderly_id)
        if doctor_id:
            query = query.filter(models.FollowUp.doctor_id == doctor_id)

        total = query.count()
        items = query.order_by(
            models.FollowUp.followup_date.desc()
        ).offset((page - 1) * per_page).limit(per_page).all()

        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }
    except SQLAlchemyError as e:
        logger.error(f"分页查询失败: {str(e)}")
        raise HTTPException(status_code=500, detail="分页查询失败")


def create_follow_up(db: Session, follow_up: schemas.FollowUpCreate):
    try:
        # 转换日期格式
        follow_up_data = follow_up.dict()
        follow_up_data['followup_date'] = datetime.strptime(follow_up_data['follow_up_date'], "%Y-%m-%d %H:%M:%S")

        # 处理下次随访日期
        if follow_up_data['next_follow_up_date']:
            follow_up_data['next_follow_up_date'] = datetime.strptime(
                follow_up_data['next_follow_up_date'], "%Y-%m-%d %H:%M:%S"
            )

        # 移除前端使用的字段名，使用数据库字段名
        follow_up_data.pop('follow_up_date', None)

        # 创建随访记录
        db_follow_up = models.FollowUp(**follow_up_data)
        db.add(db_follow_up)
        db.commit()
        db.refresh(db_follow_up)
        return db_follow_up
    except Exception as e:
        db.rollback()
        logger.error(f"创建随访记录失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

def get_follow_up_report_data(db: Session, follow_up_id: int):
    """生成报告所需数据（包含所有健康指标）"""
    try:
        follow_up = db.query(models.FollowUp).filter(models.FollowUp.id == follow_up_id).first()
        if not follow_up:
            raise HTTPException(status_code=404, detail="随访记录不存在")

        # 处理 next_follow_up_date（兼容空值）
        next_follow_up_str = None
        if hasattr(follow_up, 'next_follow_up_date') and follow_up.next_follow_up_date:
            next_follow_up_str = follow_up.next_follow_up_date.strftime("%Y-%m-%d %H:%M")


        return {
            # 基本信息
            "elderly_name": follow_up.elderly.name if follow_up.elderly else "",
            "doctor_name": follow_up.doctor.name if follow_up.doctor else "",
            "followup_date": follow_up.followup_date.strftime("%Y-%m-%d %H:%M") if follow_up.followup_date else "",
            "content": follow_up.content or "",
            "next_follow_up_date": next_follow_up_str,  # 使用处理后的值
            "medication_warning": follow_up.medication_warning or "无特殊用药禁忌",

            # 体格检查
            "height": follow_up.height,
            "weight": follow_up.weight,
            "bmi": follow_up.bmi,
            "waist_circumference": follow_up.waist_circumference,
            "hip_circumference": follow_up.hip_circumference,
            "waist_hip_ratio": follow_up.waist_hip_ratio,
            "temperature": follow_up.temperature,

            # 生命体征
            "systolic_blood_pressure": follow_up.systolic_blood_pressure,
            "diastolic_blood_pressure": follow_up.diastolic_blood_pressure,
            "blood_oxygen": follow_up.blood_oxygen,
            "pulse_rate": follow_up.pulse_rate,
            "heart_rate": follow_up.heart_rate,
            "respiration": follow_up.respiration,

            # 血液检查
            "blood_glucose": follow_up.blood_glucose,
            "uric_acid": follow_up.uric_acid,
            "hemoglobin": follow_up.hemoglobin,
            "total_cholesterol": follow_up.total_cholesterol,
            "triglycerides": follow_up.triglycerides,
            "hdl_cholesterol": follow_up.hdl_cholesterol,
            "ldl_cholesterol": follow_up.ldl_cholesterol,

            # 其他检查
            "fat": follow_up.fat,
            "water_content": follow_up.water_content,
            "bmr": follow_up.bmr,
            "bone_density": follow_up.bone_density,
            "fvc": follow_up.fvc,
            "ecg": follow_up.ecg,
            "total_sleep_time": follow_up.total_sleep_time,

            # 尿常规
            "urine_wbc": follow_up.urine_wbc,
            "urine_nitrite": follow_up.urine_nitrite,
            "urine_urobilinogen": follow_up.urine_urobilinogen,
            "urine_protein": follow_up.urine_protein,
            "urine_ph": follow_up.urine_ph,
            "urine_blood": follow_up.urine_blood,
            "urine_specific_gravity": follow_up.urine_specific_gravity,
            "urine_ketone": follow_up.urine_ketone,
            "urine_bilirubin": follow_up.urine_bilirubin,
            "urine_glucose": follow_up.urine_glucose,
            "urine_vitamin_c": follow_up.urine_vitamin_c,

            # 其他
            "cholesterol": follow_up.cholesterol
        }
    except Exception as e:
        logger.error(f"生成报告数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail="生成报告数据失败")


def delete_follow_up(db: Session, follow_up_id: int):
    """删除随访记录"""
    try:
        follow_up = db.query(models.FollowUp).filter(models.FollowUp.id == follow_up_id).first()
        if not follow_up:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="随访记录不存在"
            )

        db.delete(follow_up)
        db.commit()
        return {"message": "随访记录删除成功"}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"删除随访记录失败 ID:{follow_up_id}, 错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除随访记录失败"
        )
def delete_follow_up(db: Session, follow_up_id: int):
    """删除随访记录"""
    try:
        follow_up = db.query(models.FollowUp).filter(models.FollowUp.id == follow_up_id).first()
        if not follow_up:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="随访记录不存在"
            )

        db.delete(follow_up)
        db.commit()
        return {"message": "随访记录删除成功"}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"删除随访记录失败 ID:{follow_up_id}, 错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除随访记录失败"
        )
def update_follow_up(db: Session, follow_up_id: int, follow_up_update: schemas.FollowUpCreate):
    try:
        db_follow_up = db.query(models.FollowUp).filter(models.FollowUp.id == follow_up_id).first()
        if not db_follow_up:
            raise HTTPException(status_code=404, detail="随访记录不存在")

        update_data = follow_up_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_follow_up, key, value)

        db.commit()
        db.refresh(db_follow_up)
        return db_follow_up
    except Exception as e:
        db.rollback()
        logger.error(f"更新随访记录失败: {str(e)}")
        raise HTTPException(status_code=500, detail="更新随访记录失败")

def get_elderly(db: Session, elderly_id: int):
    """获取老人信息"""
    try:
        elderly = db.query(models.Elderly).filter(models.Elderly.id == elderly_id).first()
        if not elderly:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="老人信息不存在"
            )
        return elderly
    except SQLAlchemyError as e:
        logger.error(f"获取老人信息失败 ID:{elderly_id}, 错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取老人信息失败"
        )

def get_doctor(db: Session, doctor_id: int):
    """获取医生信息"""
    try:
        doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="医生信息不存在"
            )
        return doctor
    except SQLAlchemyError as e:
        logger.error(f"获取医生信息失败 ID:{doctor_id}, 错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取医生信息失败"
        )


# 在crud.py中添加以下函数

# 患者管理
def create_elderly(db: Session, elderly: schemas.ElderlyCreate):
    try:
        db_elderly = models.Elderly(
            name=elderly.name,
            gender=elderly.gender,
            age=elderly.age,
            contact=elderly.contact,
            address=elderly.address,
            birth_date=elderly.birth_date,
            birth_place=elderly.birth_place,
            education=elderly.education,
            occupation=elderly.occupation
        )
        db.add(db_elderly)
        db.commit()
        db.refresh(db_elderly)
        return db_elderly
    except Exception as e:
        db.rollback()
        logger.error(f"创建老人信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建老人信息失败"
        )

def delete_elderly(db: Session, elderly_id: int):
    try:
        elderly = db.query(models.Elderly).filter(models.Elderly.id == elderly_id).first()
        if not elderly:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="老人信息不存在"
            )
        db.delete(elderly)
        db.commit()
        return {"message": "老人信息删除成功"}
    except Exception as e:
        db.rollback()
        logger.error(f"删除老人信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除老人信息失败"
        )


# 在老人管理部分添加
def update_elderly(db: Session, elderly_id: int, elderly_update: schemas.ElderlyUpdate):
    try:
        db_elderly = db.query(models.Elderly).filter(models.Elderly.id == elderly_id).first()
        if not db_elderly:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="老人信息不存在"
            )

        update_data = elderly_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_elderly, key, value)

        db.commit()
        db.refresh(db_elderly)
        return db_elderly
    except Exception as e:
        db.rollback()
        logger.error(f"更新老人信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新老人信息失败"
        )

# 医生管理
def create_doctor(db: Session, doctor: schemas.DoctorCreate):
    try:
        db_doctor = models.Doctor(
            name=doctor.name,
            department=doctor.department,
            contact=doctor.contact
        )
        db.add(db_doctor)
        db.commit()
        db.refresh(db_doctor)
        return db_doctor
    except Exception as e:
        db.rollback()
        logger.error(f"创建医生信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建医生信息失败"
        )

def delete_doctor(db: Session, doctor_id: int):
    try:
        doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="医生信息不存在"
            )
        db.delete(doctor)
        db.commit()
        return {"message": "医生信息删除成功"}
    except Exception as e:
        db.rollback()
        logger.error(f"删除医生信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除医生信息失败"
        )


# 在医生管理部分添加
def update_doctor(db: Session, doctor_id: int, doctor_update: schemas.DoctorUpdate):
    try:
        db_doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
        if not db_doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="医生信息不存在"
            )

        update_data = doctor_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_doctor, key, value)

        db.commit()
        db.refresh(db_doctor)
        return db_doctor
    except Exception as e:
        db.rollback()
        logger.error(f"更新医生信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新医生信息失败"
        )

#查询功能
# crud.py
# crud.py
def get_doctors(db: Session, skip: int = 0, limit: int = 100, name: str = None):
    try:
        query = db.query(models.Doctor)
        # 仅当 name 有值时才过滤（避免 name 为 None 时的无效过滤）
        if name is not None and name.strip() != "":
            query = query.filter(models.Doctor.name.ilike(f"%{name}%"))
        # 执行查询并返回结果（即使无过滤条件，也返回所有医生）
        return query.offset(skip).limit(limit).all()
    except Exception as e:
        logger.error(f"获取医生列表失败: {str(e)}")
        # 抛出具体错误信息，方便前端排查
        raise HTTPException(
            status_code=500,
            detail=f"获取医生数据失败: {str(e)}"
        )

from sqlalchemy import cast, String

# 修改app/crud.py中的get_elderlies方法
def get_elderlies(db: Session, skip: int = 0, limit: int = 100, search: str = None):
    try:
        query = db.query(models.Elderly)
        if search:
            query = query.filter(models.Elderly.name.ilike(f"%{search}%"))
        return query.order_by(models.Elderly.id).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"获取老人列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取老人数据失败")

def schedule_follow_up_automation(db: Session):
    """自动为需要随访的老人生成随访计划"""
    try:
        # 1. 获取所有需要随访的老人（例如：上次随访超过30天的老人）
        elderly_list = db.query(models.Elderly).all()

        for elderly in elderly_list:
            last_follow_up = db.query(models.FollowUp) \
                .filter(models.FollowUp.elderly_id == elderly.id) \
                .order_by(models.FollowUp.follow_up_date.desc()) \
                .first()

            # 2. 判断是否需要新随访（示例：超过30天未随访）
            if last_follow_up:
                days_since_last = (datetime.now() - last_follow_up.follow_up_date).days
                if days_since_last < 30:
                    continue

            # 3. 自动创建随访记录
            new_follow_up = models.FollowUp(
                elderly_id=elderly.id,
                doctor_id=1,  # 默认分配ID为1的医生
                follow_up_date=datetime.now() + timedelta(days=1),  # 默认明天
                content="系统自动生成的随访计划"
            )
            db.add(new_follow_up)
            db.commit()

            print(f"已为老人 {elderly.name} 创建随访计划")

    except Exception as e:
        db.rollback()
        logger.error(f"自动排期失败: {str(e)}")