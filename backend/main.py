from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta, date
from fastapi.security import OAuth2PasswordRequestForm
from database import engine, get_db, Base
from models import User, Profile, get_password_hash, verify_password, PayingUnit
from schemas import (UserCreate, UserOut, Token, ProfileCreate, ProfileOut, ProfileUpdate,
                     ProfileListResponse, ProfileImportResponse, ProfileImportRequest,UserListResponse,UserUpdate,
                     PayingUnitOut,PayingUnitListResponse,PayingUnitCreate,PayingUnitUpdate )
from auth import create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI(title="User Profile API")
origins = [
    "http://localhost:9000",
    "http://127.0.0.1:9000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Cho phép các nguồn trong danh sách
    allow_credentials=True,           # Cho phép gửi kèm Cookies/Auth headers
    allow_methods=["*"],              # Cho phép tất cả các phương thức (GET, POST, PUT, DELETE...)
    allow_headers=["*"],              # Cho phép tất cả các headers (Content-Type, Authorization...)
)

@app.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(400, "Email đã tồn tại")

    hashed = get_password_hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.commit()

    return new_user


@app.post("/login", response_model=Token)
def login(form_data: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.email).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Sai email hoặc mật khẩu")

    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}


# GET profile
@app.get("/profile", response_model=ProfileListResponse)
def get_all_profiles(db: Session = Depends(get_db)):
    profiles = db.query(Profile).order_by(Profile.stt, Profile.id).all()

    return {
        "data": profiles,
        "total": len(profiles)
    }


@app.get("/profile/{profile_id}", response_model=ProfileOut)
def get_profile(profile_id: int, db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ")
    return profile


@app.post("/profile", response_model=ProfileOut, status_code=201)
def create_profile(profile_data: ProfileCreate, db: Session = Depends(get_db)):
    new_profile = Profile(**profile_data.model_dump())
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return new_profile


@app.put("/profile/{profile_id}", response_model=ProfileOut)
def update_profile(
    profile_id: int,
    profile_data: ProfileUpdate,
    db: Session = Depends(get_db)
):
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ")

    update_data = profile_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)

    db.commit()
    db.refresh(profile)
    return profile


@app.delete("/profile/{profile_id}")
def delete_profile(profile_id: int, db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ")

    db.delete(profile)
    db.commit()

    return {"message": f"Đã xóa profile ID {profile_id} thành công"}


# ====================== PROFILE IMPORT API ======================

@app.post("/profile/import", response_model=ProfileImportResponse)
def import_profiles(
        import_data: ProfileImportRequest,
        db: Session = Depends(get_db)
):
    success_count = 0
    failed_count = 0
    errors = []

    for i, item in enumerate(import_data.items):
        try:
            # Chuẩn bị dữ liệu
            profile_dict = item.model_dump(exclude_unset=True)

            # Nếu không có ngay_tham_gia thì gán mặc định là hôm nay
            if 'ngay_tham_gia' not in profile_dict or profile_dict['ngay_tham_gia'] is None:
                profile_dict['ngay_tham_gia'] = date.today()

            new_profile = Profile(**profile_dict)
            db.add(new_profile)
            success_count += 1

        except Exception as e:
            failed_count += 1
            errors.append({
                "row": i + 1,
                "ho_ten": getattr(item, 'ho_ten', 'N/A'),
                "error": str(e)
            })
            # Tiếp tục import các bản ghi còn lại (không rollback toàn bộ)

    # Commit một lần ở cuối để tăng tốc độ
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi lưu dữ liệu: {str(e)}"
        )

    return ProfileImportResponse(
        success=success_count,
        failed=failed_count,
        total=len(import_data.items),
        message=f"Import hoàn tất: {success_count} thành công, {failed_count} thất bại",
        errors=errors if errors else None
    )


# ====================== USER MANAGEMENT CRUD ======================

# 1. Lấy danh sách tất cả Users
@app.get("/users", response_model=UserListResponse)
def get_all_users(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    users = db.query(User).filter(User.is_active == 1) \
        .offset(skip).limit(limit).all()
    return {"data": users, "total": len(users)}


# 2. Lấy thông tin 1 User theo ID
@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    return user


# 3. Tạo User mới (Admin tạo hoặc đăng ký)
@app.post("/users", response_model=UserOut, status_code=201)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    # Kiểm tra email đã tồn tại
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email đã tồn tại")

    # Hash password trước khi lưu vào database
    hashed_password = get_password_hash(user_data.password)

    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        is_active=user_data.is_active
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# 4. Cập nhật thông tin User
@app.put("/users/{user_id}", response_model=UserOut)
def update_user(
        user_id: int,
        user_data: UserUpdate,
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")

    update_data = user_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "email" and value is not None:
            # Kiểm tra email mới có bị trùng không
            existing = db.query(User).filter(User.email == value, User.id != user_id).first()
            if existing:
                raise HTTPException(status_code=400, detail="Email đã tồn tại")

        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


# 5. Xóa User (Soft delete - khuyến nghị)
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")

    # Soft delete
    user.is_active = 0
    db.commit()

    return {"message": f"Đã vô hiệu hóa người dùng ID {user_id}"}


# 6. Xóa cứng (Hard delete) - chỉ dùng khi thật sự cần
@app.delete("/users/{user_id}/hard")
def hard_delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")

    db.delete(user)
    db.commit()

    return {"message": f"Đã xóa vĩnh viễn người dùng ID {user_id}"}


@app.get("/paying-units", response_model=PayingUnitListResponse)
def get_paying_units(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    units = db.query(PayingUnit).offset(skip).limit(limit).all()
    return {"data": units, "total": len(units)}


@app.get("/paying-units/{unit_id}", response_model=PayingUnitOut)
def get_paying_unit(unit_id: int, db: Session = Depends(get_db)):
    unit = db.query(PayingUnit).filter(PayingUnit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn vị thanh toán")
    return unit


@app.post("/paying-units", response_model=PayingUnitOut, status_code=201)
def create_paying_unit(unit_data: PayingUnitCreate, db: Session = Depends(get_db)):
    new_unit = PayingUnit(**unit_data.model_dump())
    db.add(new_unit)
    db.commit()
    db.refresh(new_unit)
    return new_unit


@app.put("/paying-units/{unit_id}", response_model=PayingUnitOut)
def update_paying_unit(
    unit_id: int,
    unit_data: PayingUnitUpdate,
    db: Session = Depends(get_db)
):
    unit = db.query(PayingUnit).filter(PayingUnit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn vị thanh toán")

    update_data = unit_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(unit, key, value)

    db.commit()
    db.refresh(unit)
    return unit


@app.delete("/paying-units/{unit_id}")
def delete_paying_unit(unit_id: int, db: Session = Depends(get_db)):
    unit = db.query(PayingUnit).filter(PayingUnit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn vị thanh toán")

    db.delete(unit)
    db.commit()
    return {"message": f"Đã xóa Paying Unit ID {unit_id} thành công"}