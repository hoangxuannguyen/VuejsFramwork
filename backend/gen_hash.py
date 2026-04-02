from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__truncate_error=False  # Dòng này cực kỳ quan trọng
)

# Tạo hash cho mật khẩu '123'
hashed = pwd_context.hash("123")
print(f"\nCopy chuỗi này: {hashed}\n")