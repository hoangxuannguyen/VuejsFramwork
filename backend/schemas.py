# schemas.py
from dateutil import parser

from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import date
from typing import Optional, Literal, List
import enum


# ========================== USER SCHEMAS ==========================
class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


# ========================== PROFILE SCHEMAS ==========================
class ProfileBase(BaseModel):
    ho_ten: str = Field(..., min_length=1, max_length=100)
    ngay_sinh: Optional[date] = None
    gioi_tinh: Optional[Literal["Nam", "Nữ"]] = None
    cccd: Optional[str] = Field(None, max_length=20)
    ngay_tham_gia: Optional[date] = None
    dia_chi: Optional[str] = Field(None, max_length=255)
    stt: Optional[int] = None


class ProfileCreate(ProfileBase):
    pass  # Kế thừa hết từ ProfileBase


class ProfileUpdate(BaseModel):          # Không kế thừa toàn bộ để kiểm soát tốt hơn
    ho_ten: Optional[str] = None
    ngay_sinh: Optional[date] = None
    gioi_tinh: Optional[Literal["Nam", "Nữ"]] = None
    cccd: Optional[str] = None
    dia_chi: Optional[str] = None
    stt: Optional[int] = None


class ProfileOut(ProfileBase):
    id: int

    class Config:
        from_attributes = True
        json_encoders = {
            date: lambda v: v.isoformat() if v else None,
        }

    @field_validator('gioi_tinh', mode='before')
    @classmethod
    def convert_gender(cls, v):
        if isinstance(v, enum.Enum):
            return v.value
        return v

    @field_validator('ngay_sinh', 'ngay_tham_gia', mode='before')
    @classmethod
    def convert_date_to_str(cls, v):
        if isinstance(v, date):
            return v.isoformat()
        return v


class ProfileListResponse(BaseModel):
    data: List[ProfileOut]
    total: int


class ProfileImportItem(BaseModel):
    ho_ten: str = Field(..., max_length=100)
    ngay_sinh: Optional[date] = None
    gioi_tinh: Optional[Literal["Nam", "Nữ"]] = None
    cccd: Optional[str] = Field(None, max_length=20)
    ngay_tham_gia: Optional[date] = None
    dia_chi: Optional[str] = Field(None, max_length=255)
    stt: Optional[int] = None


class ProfileImportRequest(BaseModel):
    items: List[ProfileImportItem] = Field(..., min_items=1, max_items=1000)  # Giới hạn tối đa 1000 bản ghi/lần


class ProfileImportResponse(BaseModel):
    success: int
    failed: int
    total: int
    message: str
    errors: Optional[List[dict]] = None

# ====================== VALIDATORS ======================
@field_validator('ngay_sinh', 'ngay_tham_gia', mode='before')
@classmethod
def parse_date(cls, v):
    if v is None:
        return None
    if isinstance(v, date):
        return v
    if isinstance(v, str):
        try:
            # Hỗ trợ nhiều định dạng: 3/26/2026, 2026-03-26, 26/03/2026...
            parsed = parser.parse(v)
            return parsed.date()
        except:
            raise ValueError(f'Không thể chuyển đổi ngày: {v}')
    return v


@field_validator('ho_ten', 'dia_chi', mode='before')
@classmethod
def clean_string(cls, v):
    if isinstance(v, str):
        return v.strip().replace('�', '')  # Xóa ký tự lỗi encoding
    return v


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str
    is_active: Optional[bool] = True


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True


class UserOut(BaseModel):
    id: int
    email: EmailStr
    is_active: bool

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    data: List[UserOut]
    total: int


class PayingUnitBase(BaseModel):
    ten_cong_ty: str = Field(..., max_length=200, description="Tên công ty")
    ma_so_thue: Optional[str] = Field(None, max_length=50, description="Mã số thuế")
    nguoi_dai_dien: Optional[str] = Field(None, max_length=100, description="Người đại diện")
    dia_chi: Optional[str] = Field(None, max_length=300, description="Địa chỉ")
    loai_cong_ty: Optional[str] = Field(None, description="Loại công ty")


class PayingUnitCreate(PayingUnitBase):
    pass


class PayingUnitUpdate(PayingUnitBase):
    ten_cong_ty: Optional[str] = None
    ma_so_thue: Optional[str] = None
    nguoi_dai_dien: Optional[str] = None
    dia_chi: Optional[str] = None
    loai_cong_ty: Optional[str] = None


class PayingUnitOut(PayingUnitBase):
    id: int

    class Config:
        from_attributes = True


class PayingUnitListResponse(BaseModel):
    data: List[PayingUnitOut]
    total: int