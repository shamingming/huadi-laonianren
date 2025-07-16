import mysql.connector
from mysql.connector import Error

# 数据库配置信息，根据实际情况修改
config = {
    "host": "localhost",
    "user": "root",
    "password": "xhnmdl0407",
    "database": "elderly_health_db"
}


def get_db_connection():
    """获取数据库连接"""
    try:
        connection = mysql.connector.connect(**config)
        return connection
    except Error as e:
        print(f"数据库连接失败: {e}")
        return None

def drop_follow_ups_table():
    """删除现有 follow_ups 表"""
    connection = get_db_connection()
    if not connection:
        return
    cursor = connection.cursor()
    try:
        cursor.execute("DROP TABLE IF EXISTS follow_ups")
        connection.commit()
        print("follow_ups 表已删除")
    except Error as e:
        print(f"删除 follow_ups 表失败: {e}")
    finally:
        cursor.close()
        connection.close()

def create_follow_ups_table():
    """创建新的 follow_ups 表"""
    connection = get_db_connection()
    if not connection:
        return
    cursor = connection.cursor()
    try:
        create_table_sql = """
        CREATE TABLE follow_ups (
            id INT AUTO_INCREMENT PRIMARY KEY,
            elderly_id INT NOT NULL COMMENT '老人ID',
            doctor_id INT NOT NULL DEFAULT 1 COMMENT '默认医生ID=1',
            followup_date DATETIME NOT NULL COMMENT '随访日期',
            content TEXT COMMENT '随访内容',
            height DECIMAL(6,2) COMMENT '身高',
            weight DECIMAL(6,2) COMMENT '体重',
            bmi DECIMAL(6,2) COMMENT 'bmi指数',
            waist_circumference DECIMAL(6,2) COMMENT '腰围',
            hip_circumference DECIMAL(6,2) COMMENT '臀围',
            waist_hip_ratio DECIMAL(6,2) COMMENT '腰臀比',
            systolic_blood_pressure INT COMMENT '收缩压(血压)',
            diastolic_blood_pressure INT COMMENT '舒张压(血压)',
            blood_oxygen INT COMMENT '血氧(%)',
            blood_glucose DECIMAL(6,2) COMMENT '血糖(mmol/L)',
            pulse_rate INT COMMENT '脉率',
            fat DECIMAL(6,2) COMMENT '脂肪',
            cholesterol DECIMAL(6,2) COMMENT '胆固醇',
            fvc DECIMAL(6,2) COMMENT '用力肺活量(L)(肺功能)',
            uric_acid INT COMMENT '尿酸',
            bone_density DECIMAL(6,2) COMMENT '骨密度',
            total_sleep_time DECIMAL(6,2) COMMENT '睡眠总时长',
            heart_rate INT COMMENT '心率',
            ecg VARCHAR(10) COMMENT '心电',
            water_content DECIMAL(6,2) COMMENT '水分含量',
            bmr INT COMMENT '基础代谢率',
            temperature DECIMAL(6,2) COMMENT '体温',
            hemoglobin DECIMAL(6,2) COMMENT '血红蛋白',
            total_cholesterol DECIMAL(6,2) COMMENT '总胆固醇(血脂)',
            triglycerides DECIMAL(6,2) COMMENT '甘油三酯(血脂)',
            hdl_cholesterol DECIMAL(6,2) COMMENT '高密度脂蛋白胆固醇(血脂)',
            ldl_cholesterol DECIMAL(6,2) COMMENT '低密度脂蛋白胆固醇(血脂)',
            urine_wbc DECIMAL(6,2) COMMENT '白细胞(尿常规)',
            urine_nitrite DECIMAL(6,2) COMMENT '亚硝酸盐(尿常规)',
            urine_urobilinogen DECIMAL(6,2) COMMENT '尿胆原(尿常规)',
            urine_protein DECIMAL(6,2) COMMENT '蛋白质(尿常规)',
            urine_ph DECIMAL(6,2) COMMENT 'PH值(尿常规)',
            urine_blood DECIMAL(6,2) COMMENT '潜血(尿常规)',
            urine_specific_gravity DECIMAL(6,2) COMMENT '比重(尿常规)',
            urine_ketone DECIMAL(6,2) COMMENT '酮体(尿常规)',
            urine_bilirubin DECIMAL(6,2) COMMENT '胆红素(尿常规)',
            urine_glucose DECIMAL(6,2) COMMENT '葡萄糖(尿常规)',
            urine_vitamin_c DECIMAL(6,2) COMMENT '维生素C(尿常规)',
            respiration INT COMMENT '呼吸',
            schedule_strategy VARCHAR(50) DEFAULT 'automated' COMMENT '随访策略',
            is_recurring BOOLEAN DEFAULT FALSE COMMENT '是否定期随访',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (elderly_id) REFERENCES elderly(id) ON DELETE CASCADE,
            FOREIGN KEY (doctor_id) REFERENCES doctors(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        cursor.execute(create_table_sql)
        connection.commit()
        print("follow_ups 表创建成功！")
    except Error as e:
        print(f"创建 follow_ups 表失败: {e}")
    finally:
        cursor.close()
        connection.close()

def migrate_data_to_follow_ups():
    """迁移数据，增加详细调试输出"""
    connection = get_db_connection()
    if not connection:
        return
    cursor = connection.cursor()
    try:
        # 1. 先检查 table_generated_data 和 elderly 表是否有数据
        cursor.execute("SELECT COUNT(*) FROM table_generated_data")
        t_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM elderly")
        e_count = cursor.fetchone()[0]
        print(f"调试：table_generated_data 有 {t_count} 条数据，elderly 表有 {e_count} 条数据")
        if t_count == 0 or e_count == 0:
            print("错误：源表或目标关联表无数据，无法迁移")
            return

        # 2. 调整查询：使用实际存在的字段（关键修复）
        # 假设 table_generated_data 中无 followup_date 和 content，用当前时间和默认内容替代
        select_query = """
        SELECT 
            e.id AS elderly_id,
            1 AS doctor_id,  -- 强制关联医生ID=1
            NOW() AS followup_date,  -- 用当前时间作为随访日期
            CONCAT('自动导入的健康记录：', t.record_id) AS content,  -- 生成默认内容
            t.height,
            t.weight,
            t.bmi,
            t.waist_circumference,
            t.hip_circumference,
            t.waist_hip_ratio,
            t.systolic_blood_pressure,
            t.diastolic_blood_pressure,
            t.blood_oxygen,
            t.blood_glucose,
            t.pulse_rate,
            t.fat,
            t.cholesterol,
            t.fvc,
            t.uric_acid,
            t.bone_density,
            t.total_sleep_time,
            t.heart_rate,
            t.ecg,
            t.water_content,
            t.bmr,
            t.temperature,
            t.hemoglobin,
            t.total_cholesterol,
            t.triglycerides,
            t.hdl_cholesterol,
            t.ldl_cholesterol,
            t.urine_wbc,
            t.urine_nitrite,
            t.urine_urobilinogen,
            t.urine_protein,
            t.urine_ph,
            t.urine_blood,
            t.urine_specific_gravity,
            t.urine_ketone,
            t.urine_bilirubin,
            t.urine_glucose,
            t.urine_vitamin_c,
            t.respiration
        FROM table_generated_data t
        JOIN elderly e 
          ON t.name = e.name 
         AND t.birth_date = e.birth_date  -- 通过姓名+出生日期关联
        """
        print("调试：执行查询语句：", select_query)
        cursor.execute(select_query)
        rows = cursor.fetchall()

        # 3. 检查查询结果
        if not rows:
            print("警告：查询未返回任何匹配数据，可能关联条件不匹配")
            # 打印样本数据辅助排查
            cursor.execute("SELECT name, birth_date FROM table_generated_data LIMIT 5")
            print("调试：table_generated_data 前5条样本：", cursor.fetchall())
            cursor.execute("SELECT name, birth_date FROM elderly LIMIT 5")
            print("调试：elderly 表前5条样本：", cursor.fetchall())
            return

        # 4. 插入数据
        insert_query = """
        INSERT INTO follow_ups (
            elderly_id, doctor_id, followup_date, content,
            height, weight, bmi, waist_circumference, hip_circumference, waist_hip_ratio,
            systolic_blood_pressure, diastolic_blood_pressure, blood_oxygen, blood_glucose,
            pulse_rate, fat, cholesterol, fvc, uric_acid, bone_density, total_sleep_time,
            heart_rate, ecg, water_content, bmr, temperature, hemoglobin,
            total_cholesterol, triglycerides, hdl_cholesterol, ldl_cholesterol,
            urine_wbc, urine_nitrite, urine_urobilinogen, urine_protein, urine_ph,
            urine_blood, urine_specific_gravity, urine_ketone, urine_bilirubin,
            urine_glucose, urine_vitamin_c, respiration
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.executemany(insert_query, rows)
        connection.commit()
        print(f"成功迁移 {cursor.rowcount} 条记录到 follow_ups 表")

    except Error as e:
        print(f"数据迁移失败: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    drop_follow_ups_table()
    create_follow_ups_table()
    migrate_data_to_follow_ups()