from sqlalchemy import create_engine

def test_connection():
    try:
        engine = create_engine("mysql+pymysql://root:xhnmdl0407@localhost/elderly_health_db")
        with engine.connect() as conn:
            print("✅ 数据库连接成功！")
    except Exception as e:
        print(f"❌ 连接失败: {str(e)}")

if __name__ == "__main__":
    test_connection()