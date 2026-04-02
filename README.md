# 🛡️ Source Management System (Full-Stack)

Dự án được xây dựng với kiến trúc hiện đại, kết hợp sức mạnh của **FastAPI** cho Backend và **Quasar/Vue 3** cho Frontend. Đặc biệt, dự án tích hợp **Model Context Protocol (MCP)** giúp tự động hóa quy trình phát triển mã nguồn thông qua AI (Claude Desktop).

---

## 🏗️ Kiến trúc Hệ thống

### 1. Frontend (Quasar Framework)
* **Framework:** Vue 3 (Composition API).
* **State Management:** Pinia (Quản lý profile và dữ liệu bảo hiểm).
* **UI Components:** Quasar UI (Material Design 3).
* **Tính năng:** Responsive hoàn toàn, tích hợp xác thực JWT, điều hướng thông minh với Vue Router.

### 2. Backend (FastAPI)
* **Ngôn ngữ:** Python 3.9+.
* **Bảo mật:** OAuth2 với JWT (JSON Web Tokens).
* **Validation:** Pydantic models (Đảm bảo tính toàn vẹn dữ liệu).
* **Hiệu năng:** Xử lý bất đồng bộ (Async/Await) tối ưu cho các tác vụ I/O.

### 3. AI Automation (MCP Server)
* **Vị trí:** `my-scaffold-mcp/`
* **Chức năng:** Cung cấp các công cụ (Tools) để Claude Desktop có thể đọc cấu trúc dự án và tự động tạo Boilerplate code (Pages, Components, Stores) theo đúng chuẩn của hệ thống.

---

## 🚀 Hướng dẫn Cài đặt

### Bước 1: Thiết lập Backend (FastAPI)
```bash
cd backend
python -m venv venv

# Kích hoạt môi trường ảo
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload
```
###  Bước 2: Thiết lập Frontend (Quasar)
```Bash
cd frontend
npm install
# Chạy ở chế độ Development
quasar dev
```
## 🤖 Tích hợp MCP vào Claude Desktop
Để Claude có thể hỗ trợ bạn viết code trực tiếp, hãy làm theo các bước sau:

### 1. Build MCP Server
```Bash
cd my-scaffold-mcp
npm install
npm run build
```
### 2. Cấu hình Claude Desktop
Mở file claude_desktop_config.json theo đường dẫn:

Windows: %APPDATA%\Standard Notes\claude_desktop_config.json

macOS: ~/Library/Application Support/Claude/claude_desktop_config.json

Thêm cấu hình (Lưu ý thay [PATH_TO_PROJECT] bằng đường dẫn tuyệt đối):

```JSON
{
  "mcpServers": {
    "insurance-scaffold": {
      "command": "node",
      "args": [
        "[PATH_TO_PROJECT]/VuejsFramwork/my-scaffold-mcp/build/index.js"
      ],
      "env": {
        "PROJECT_ROOT": "[PATH_TO_PROJECT]/VuejsFramwork"
      }
    }
  }
}
```
### 3. Các lệnh AI hỗ trợ
Sau khi khởi động lại Claude, bạn có thể yêu cầu:

"Tạo một trang quản lý hợp đồng bảo hiểm mới."

"Tạo một component Quasar để hiển thị biểu đồ doanh thu."

"Tạo Pinia store để lưu trữ thông tin các gói bảo hiểm."

## 📁 Cấu trúc Thư mục
```Plaintext
├── backend/               # Mã nguồn FastAPI
│   ├── app/api/           # Các route và logic xử lý
│   └── core/              # Cấu hình bảo mật và JWT
├── frontend/              # Mã nguồn Quasar/Vue
│   ├── src/pages/         # Các trang giao diện
│   └── src/stores/        # Quản lý trạng thái (Pinia)
├── my-scaffold-mcp/       # MCP Server (AI Tools)
│   ├── src/               # Logic tạo file tự động
│   └── build/             # File JS đã biên dịch
└── README.md
```
## 🛠️ Lưu ý khi Phát triển
Môi trường macOS (M4): Đảm bảo kiến trúc Python và Node.js tương thích với chip Apple Silicon để có hiệu năng tốt nhất.

Xử lý lỗi: Nếu Claude Desktop không nhận diện được MCP, hãy kiểm tra lại đường dẫn tuyệt đối trong file cấu hình và đảm bảo đã chạy npm run build cho thư mục MCP.

Bảo mật: Không commit file .env lên repository.
