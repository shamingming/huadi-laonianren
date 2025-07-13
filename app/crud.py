from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from . import models, schemas
import logging
from contextlib import contextmanager

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

def get_follow_ups(db: Session, skip: int = 0, limit: int = 100, elderly_id: int = None, doctor_id: int = None):
    """获取分页随访记录列表，支持筛选"""
    try:
        query = db.query(models.FollowUp)

        if elderly_id:
            query = query.filter(models.FollowUp.elderly_id == elderly_id)
        if doctor_id:
            query = query.filter(models.FollowUp.doctor_id == doctor_id)

        return query.order_by(models.FollowUp.follow_up_date.desc()).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"获取随访列表失败, 错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取随访列表失败"
        )


def create_follow_up(db: Session, follow_up: schemas.FollowUpCreate):
    try:
        # 确保老人记录存在
        elderly = db.query(models.Elderly).get(follow_up.elderly_id)
        if not elderly:
            elderly = models.Elderly(
                name=f"老人-{follow_up.elderly_id}",
                gender="未知",
                age=60,
                contact="未填写",
                address="未填写"
            )
            db.add(elderly)
            db.flush()  # 立即获取ID
            follow_up.elderly_id = elderly.id  # 使用实际生成的ID

        # 确保医生记录存在
        doctor = db.query(models.Doctor).get(follow_up.doctor_id)
        if not doctor:
            doctor = models.Doctor(
                name=f"医生-{follow_up.doctor_id}",
                department="全科",
                contact="未填写"
            )
            db.add(doctor)
            db.flush()  # 立即获取ID
            follow_up.doctor_id = doctor.id  # 使用实际生成的ID

        # 创建随访记录
        db_follow_up = models.FollowUp(
            elderly_id=follow_up.elderly_id,
            doctor_id=follow_up.doctor_id,
            follow_up_date=follow_up.follow_up_date,
            content=follow_up.content,
            result=follow_up.result or "无",
            next_follow_up_date=follow_up.next_follow_up_date,
            medication_warning=follow_up.medication_warning or "无",
            created_at = datetime.now(),
            updated_at = datetime.now()
        )
        db.add(db_follow_up)
        db.commit()
        db.refresh(db_follow_up)
        return db_follow_up

    except Exception as e:
        db.rollback()
        logger.error(f"操作失败: {str(e)}", exc_info=True)
        raise

def get_follow_up_report_data(db: Session, follow_up_id: int):
    """生成报告所需数据（增强错误处理）"""
    try:
        follow_up = db.query(models.FollowUp).filter(models.FollowUp.id == follow_up_id).first()
        if not follow_up:
            logger.warning(f"报告生成失败，随访记录不存在 ID:{follow_up_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="随访记录不存在"
            )

        return {
            "elderly_name": follow_up.elderly.name if follow_up.elderly else "",
            "doctor_name": follow_up.doctor.name if follow_up.doctor else "",
            "follow_up_date": follow_up.follow_up_date.strftime("%Y-%m-%d %H:%M") if follow_up.follow_up_date else "",
            "content": follow_up.content or "",
            "result": follow_up.result or "",
            "next_follow_up_date": follow_up.next_follow_up_date.strftime("%Y-%m-%d %H:%M")
            if follow_up.next_follow_up_date else None
        }
    except SQLAlchemyError as e:
        logger.error(f"生成报告数据失败 ID:{follow_up_id}, 错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="生成报告数据失败"
        )

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