from datetime import datetime, timezone,timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from . import models, schemas
import logging
from contextlib import contextmanager
from sqlalchemy.orm import joinedload


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
def get_follow_ups(db: Session, skip: int = 0, limit: int = 100, elderly_id: int = None, doctor_id: int = None):
    try:
        query = db.query(models.FollowUp).options(
            joinedload(models.FollowUp.elderly),
            joinedload(models.FollowUp.doctor)
        )

        if elderly_id is not None:
            query = query.filter(models.FollowUp.elderly_id == elderly_id)
        if doctor_id is not None:
            query = query.filter(models.FollowUp.doctor_id == doctor_id)

        return query.order_by(models.FollowUp.follow_up_date.desc()).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"获取随访列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取随访数据失败")


def create_follow_up(db: Session, follow_up: schemas.FollowUpCreate):
    try:
        # 确保follow_up_date是datetime对象
        follow_up_date = follow_up.follow_up_date
        if isinstance(follow_up_date, str):
            follow_up_date = datetime.strptime(follow_up_date, "%Y-%m-%d %H:%M:%S")

        # 计算自动排期的下次随访日期
        next_follow_up_date = None
        if follow_up.schedule_strategy == 'automated' and follow_up.schedule_interval:
            next_follow_up_date = follow_up_date + timedelta(days=follow_up.schedule_interval)
        elif follow_up.schedule_strategy == 'manual' and follow_up.next_follow_up_date:
            next_follow_up_date = follow_up.next_follow_up_date
            if isinstance(next_follow_up_date, str):
                next_follow_up_date = datetime.strptime(next_follow_up_date, "%Y-%m-%d %H:%M:%S")


        db_follow_up = models.FollowUp(
            elderly_id=follow_up.elderly_id,
            doctor_id=follow_up.doctor_id,
            follow_up_date=follow_up_date,
            content=follow_up.content,
            result=follow_up.result,
            next_follow_up_date=next_follow_up_date,  # 存储下次随访日期
            medication_warning=follow_up.medication_warning,  # 存储用药禁忌
            schedule_strategy=follow_up.schedule_strategy or "manual",  # 默认值
            schedule_interval=follow_up.schedule_interval,
            is_recurring=follow_up.is_recurring or False
        )

        db.add(db_follow_up)
        db.commit()
        db.refresh(db_follow_up)
        return db_follow_up
    except Exception as e:
        db.rollback()
        logger.error(f"创建失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
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

        # 获取老人和医生的名字
        elderly_name = follow_up.elderly.name if follow_up.elderly else ""
        doctor_name = follow_up.doctor.name if follow_up.doctor else ""

        return {
            "elderly_name": follow_up.elderly.name if follow_up.elderly else "",
            "doctor_name": follow_up.doctor.name if follow_up.doctor else "",
            "follow_up_date": follow_up.follow_up_date.strftime("%Y-%m-%d %H:%M") if follow_up.follow_up_date else "",
            "content": follow_up.content or "",
            "result": follow_up.result or "",
            "next_follow_up_date": follow_up.next_follow_up_date.strftime("%Y-%m-%d %H:%M")
            if follow_up.next_follow_up_date else None,
            "medication_warning": follow_up.medication_warning or "无特殊用药禁忌"
        }
    except SQLAlchemyError as e:
        logger.error(f"生成报告数据失败 ID:{follow_up_id}, 错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="生成报告数据失败"
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
            address=elderly.address
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

#查询功能
def get_elderlies(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Elderly).offset(skip).limit(limit).all()

def get_doctors(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Doctor).offset(skip).limit(limit).all()


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
                content="系统自动生成的随访计划",
                result="待填写"
            )
            db.add(new_follow_up)
            db.commit()

            print(f"已为老人 {elderly.name} 创建随访计划")

    except Exception as e:
        db.rollback()
        logger.error(f"自动排期失败: {str(e)}")