from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# مسار ملف قاعدة البيانات المحلية
SQLALCHEMY_DATABASE_URL = "sqlite:///./crm_database.db"

# إنشاء محرك الاتصال بقاعدة البيانات
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# إنشاء الجلسة (Session) للتفاعل مع البيانات
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# الفئة الأساسية لتحديد الجداول (Models)
Base = declarative_base()

# دالة مخصصة لفتح وإغلاق الاتصال بقاعدة البيانات مع كل طلب API
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()