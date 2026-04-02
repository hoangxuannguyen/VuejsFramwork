from xmlrpc.client import DateTime

from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base
from passlib.context import CryptContext
import enum

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__truncate_error=False  # Dòng này cực kỳ quan trọng
)

class Gender(enum.Enum):
    NAM = "Nam"
    NU = "Nữ"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Integer, default=1)

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    stt = Column(Integer, nullable=True, comment="Số thứ tự (nếu cần hiển thị theo thứ tự)")
    ho_ten = Column(String(100), nullable=False, comment="Họ và tên")
    ngay_sinh = Column(Date, nullable=True, comment="Ngày sinh")
    gioi_tinh = Column(Enum(Gender), nullable=True, comment="Giới tính: Nam/Nữ")
    cccd = Column(String(20), unique=True, nullable=True, comment="Số CCCD/CMND")
    ngay_tham_gia = Column(Date, nullable=False, comment="Ngày tham gia hệ thống")
    dia_chi = Column(String(255), nullable=True, comment="Địa chỉ")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


class PayingUnit(Base):
    __tablename__ = "paying_units"

    id = Column(Integer, primary_key=True, index=True)
    ten_cong_ty = Column(String(200), nullable=False, index=True)
    ma_so_thue = Column(String(50), unique=True, nullable=True)
    nguoi_dai_dien = Column(String(100), nullable=True)
    dia_chi = Column(String(300), nullable=True)
    loai_cong_ty = Column(String(50), nullable=True)