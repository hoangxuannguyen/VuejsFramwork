import os
import json
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("QuasarScaffolder")

# --- CẤU HÌNH ĐƯỜNG DẪN TUYỆT ĐỐI ---
PROJECT_ROOT = r"D:\Projects\Insurance\Insurance_App" 
MCP_ROOT = r"D:\Projects\Insurance\my-scaffold-mcp"
TEMPLATE_DIR = os.path.join(MCP_ROOT, "templates")
ROUTES_FILE = os.path.join(PROJECT_ROOT, "src", "router", "routes.ts")

@mcp.tool()
def save_manifest(file_path: str, content: str):
    """Ghi nội dung manifest vào file vật lý."""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"✅ Đã ghi file manifest thành công tại: {file_path}"
    except Exception as e:
        return f"❌ Lỗi ghi file manifest: {str(e)}"

def get_template(name):
    path = os.path.join(TEMPLATE_DIR, f"{name}.template")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Thiếu template: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_file(path, content):
    full_path = os.path.join(PROJECT_ROOT, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

def update_routes(entity_name, entity_plural):
    if not os.path.exists(ROUTES_FILE): return "⚠️ Không tìm thấy routes.ts"
    with open(ROUTES_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    new_route = f"{{ path: '{entity_plural}', component: () => import('pages/{entity_name}Page.vue') }},"
    if f"pages/{entity_name}Page.vue" in content: return "ℹ️ Route đã tồn tại."
    
    anchor = "// %GENERATED_ROUTES_HERE%"
    if anchor in content:
        updated_content = content.replace(anchor, f"{new_route}\n      {anchor}")
        with open(ROUTES_FILE, "w", encoding="utf-8") as f:
            f.write(updated_content)
        return f"🚀 Đã đăng ký route: /{entity_plural}"
    return "⚠️ Thiếu điểm neo trong routes.ts"

@mcp.tool()
def generate_from_manifest(manifest_path: str):
    """Đọc manifest và thực sự sinh file code."""
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        entity_raw = config["entity"]
        # Chuẩn hóa: paying_unit -> PayingUnit
        entity_pascal = "".join([word.capitalize() for word in entity_raw.replace('-', '_').split('_')])
        fields = config["fields"]
        endpoint = config["api_endpoint"]
        stack_type = config.get("stack", "fastapi")
        
        # Xác định đường dẫn lỗi tùy theo backend
        error_path = "axiosErr.response?.data?.detail" if stack_type == "fastapi" else "axiosErr.response?.data?.message"

        # Khởi tạo data dictionary với đầy đủ các key cho template
        data = {
            "Entity": entity_pascal,
            "Entity_Plural": f"{entity_pascal}s",
            "entity_single": entity_raw.lower().replace('_', ''),
            "entity_plural": f"{entity_raw.lower().replace('_', '')}s",
            "entity_plural_filename": f"{entity_raw.lower().replace('_', '')}s",
            "entity_single_url": endpoint.strip('/'),
            "stack_error_path": error_path
        }

        # Xử lý các khối code động (TypeScript & Vue)
        iflds, cols, f_in, d_val, csv_m, csv_e = [], [], [], [], [], []
        
        for f in fields:
            n, l = f['name'], f['label']
            ft = f.get('type', 'string')
            cp = f.get('component', 'q-input')
            
            # 1. Interface TS
            ts_type = "string" if ft == "string" else "number" if ft == "number" else "boolean"
            iflds.append(f"  {n}: {ts_type};")
            
            # 2. Table Columns
            cols.append(f"  {{ name: '{n}', label: '{l}', field: '{n}', align: 'left' as const }},")
            
            # 3. Form Inputs
            if cp == "q-select":
                opts = json.dumps(f.get('options', []))
                f_in.append(f'      <q-select v-model="form.{n}" :options="{opts}" label="{l}" outlined dense />')
            else:
                f_in.append(f'      <q-input v-model="form.{n}" label="{l}" outlined dense />')
            
            # 4. Default Values & CSV Mapping
            val = "''" if ft == "string" else "0" if ft == "number" else "true"
            d_val.append(f"  {n}: {val},")
            
            # Logic cho hàm importCSV (Map từ file CSV vào Payload)
            csv_m.append(f"                      {n}: row.{n} || {val},")
            
            # Logic cho hàm exportCSV (Map từ Store Item ra file CSV)
            csv_e.append(f"          {n}: item.{n},")

        # Cập nhật data với các chuỗi đã nối
        data.update({
            "entity_fields_interface": "\n".join(iflds),
            "column_definitions": "\n".join(cols),
            "form_fields_inputs": "\n".join(f_in),
            "default_form_values": "\n".join(d_val),
            "csv_mapping_logic": "\n".join(csv_m),
            "csv_export_mapping": "\n".join(csv_e)
        })

        # Định nghĩa các file sẽ xuất ra
        output_files = {
            f"src/pages/{data['Entity']}Page.vue": "Page.vue",
            f"src/stores/{data['entity_plural_filename']}.ts": "Store.ts",
            f"src/components/{data['Entity']}Form.vue": "Form.vue"
        }

        report = []
        for rel_path, temp_name in output_files.items():
            # Đọc template
            template_content = get_template(temp_name)
            
            # Thay thế tất cả placeholders
            rendered_content = template_content
            for k, v in data.items():
                placeholder = f"{{{{{k}}}}}"
                rendered_content = rendered_content.replace(placeholder, str(v))
            
            # Ghi file
            write_file(rel_path, rendered_content)
            report.append(f"✅ Đã tạo: {rel_path}")
            
        # Cập nhật route
        report.append(update_routes(data['Entity'], data['entity_plural']))
        
        return "\n".join(report)
        
    except Exception as e:
        return f"❌ Lỗi thực thi: {str(e)}"

if __name__ == "__main__":
    mcp.run()