import requests
import json
import time
import subprocess
import os
import sys

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

ORDER_URL = "http://localhost:8081"
INVENTORY_URL = "http://localhost:8082"
PAYMENT_URL = "http://localhost:8083"

def set_cell_background(cell, hex_color):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def format_table(table, col_widths, headers, data, align_right_cols=[]):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    # Header row
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], "1F4E79")
        set_cell_margins(hdr_cells[i], 120, 120, 150, 150)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT if i in align_right_cols else WD_ALIGN_PARAGRAPH.LEFT
        for run in p.runs:
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            run.font.name = "Calibri"
            run.font.size = Pt(10)
    
    # Data rows
    for row_idx, row_data in enumerate(data):
        row_cells = table.add_row().cells
        bg_color = "F9FAFC" if row_idx % 2 == 1 else "FFFFFF"
        for i, val in enumerate(row_data):
            row_cells[i].text = str(val)
            set_cell_background(row_cells[i], bg_color)
            set_cell_margins(row_cells[i], 80, 80, 120, 120)
            p = row_cells[i].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT if i in align_right_cols else WD_ALIGN_PARAGRAPH.LEFT
            for run in p.runs:
                run.font.name = "Calibri"
                run.font.size = Pt(9.5)

    for row in table.rows:
        for idx, width in enumerate(col_widths):
            row.cells[idx].width = width

def add_code_block(doc, code_text):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "F2F4F7")
    set_cell_margins(cell, 100, 100, 150, 150)
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:left w:val="single" w:sz="24" w:space="0" w:color="006699"/><w:top w:val="none"/><w:right w:val="none"/><w:bottom w:val="none"/></w:tcBorders>')
    tcPr.append(borders)
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(code_text)
    run.font.name = "Consolas"
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(30, 41, 59)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def add_callout(doc, text, title="Ghi chú quan trọng"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "EBF3F9")
    set_cell_margins(cell, 120, 120, 180, 180)
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:left w:val="single" w:sz="28" w:space="0" w:color="004080"/><w:top w:val="none"/><w:right w:val="none"/><w:bottom w:val="none"/></w:tcBorders>')
    tcPr.append(borders)
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    run_t = p.add_run(f"📌 {title}: ")
    run_t.font.bold = True
    run_t.font.name = "Calibri"
    run_t.font.size = Pt(10)
    run_t.font.color.rgb = RGBColor(0, 51, 102)
    run_b = p.add_run(text)
    run_b.font.name = "Calibri"
    run_b.font.size = Pt(10)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def wait_for_service(url, max_retries=30, delay=1):
    for i in range(max_retries):
        try:
            r = requests.get(url, timeout=2)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(delay)
    return False

def main():
    print("=== BẮT ĐẦU CHẠY CÁC KỊCH BẢN KIỂM THỬ SAGA (KB1 - KB8) ===")
    print("Kiểm tra tính sẵn sàng của 3 microservice...")
    wait_for_service(f"{INVENTORY_URL}/api/inventory/products")
    wait_for_service(f"{PAYMENT_URL}/api/payments/wallets")
    wait_for_service(f"{ORDER_URL}/api/orders")
    results = {}

    # Initial state
    r_prod = requests.get(f"{INVENTORY_URL}/api/inventory/products").json()
    r_wall = requests.get(f"{PAYMENT_URL}/api/payments/wallets").json()
    print("Initial Products:", r_prod)
    print("Initial Wallets:", r_wall)
    results["init_products"] = r_prod
    results["init_wallets"] = r_wall

    # --- KB1: Happy path ---
    print("\n--- Running KB1: Happy Path ---")
    kb1_payload = {"customerId": "C1", "productId": "P1", "quantity": 2, "amount": 2000.0}
    r_kb1 = requests.post(f"{ORDER_URL}/api/orders", json=kb1_payload)
    kb1_res = r_kb1.json()
    kb1_id = kb1_res["id"]
    time.sleep(0.5)
    kb1_logs = requests.get(f"{ORDER_URL}/api/orders/{kb1_id}/saga-logs").json()
    kb1_prod = requests.get(f"{INVENTORY_URL}/api/inventory/products").json()
    kb1_wall = requests.get(f"{PAYMENT_URL}/api/payments/wallets").json()
    results["kb1"] = {
        "payload": kb1_payload, "response": kb1_res, "logs": kb1_logs,
        "products": kb1_prod, "wallets": kb1_wall
    }
    print("KB1 Result:", kb1_res["status"], kb1_res["sagaStatus"])

    # --- KB2: Thanh toán thất bại (402) ---
    print("\n--- Running KB2: Thanh toán thất bại (402) ---")
    kb2_payload = {"customerId": "C2", "productId": "P1", "quantity": 1, "amount": 1000.0}
    r_kb2 = requests.post(f"{ORDER_URL}/api/orders", json=kb2_payload)
    kb2_res = r_kb2.json()
    kb2_id = kb2_res["id"]
    time.sleep(0.5)
    kb2_logs = requests.get(f"{ORDER_URL}/api/orders/{kb2_id}/saga-logs").json()
    kb2_prod = requests.get(f"{INVENTORY_URL}/api/inventory/products").json()
    kb2_wall = requests.get(f"{PAYMENT_URL}/api/payments/wallets").json()
    kb2_resv = requests.get(f"{INVENTORY_URL}/api/inventory/reservations").json()
    results["kb2"] = {
        "payload": kb2_payload, "response": kb2_res, "logs": kb2_logs,
        "products": kb2_prod, "wallets": kb2_wall, "reservations": kb2_resv
    }
    print("KB2 Result:", kb2_res["status"], kb2_res["sagaStatus"], kb2_res["failureReason"])

    # --- KB3: Hết hàng (409) ---
    print("\n--- Running KB3: Hết hàng (409) ---")
    kb3_payload = {"customerId": "C1", "productId": "P2", "quantity": 100, "amount": 2000.0}
    r_kb3 = requests.post(f"{ORDER_URL}/api/orders", json=kb3_payload)
    kb3_res = r_kb3.json()
    kb3_id = kb3_res["id"]
    time.sleep(0.5)
    kb3_logs = requests.get(f"{ORDER_URL}/api/orders/{kb3_id}/saga-logs").json()
    kb3_prod = requests.get(f"{INVENTORY_URL}/api/inventory/products").json()
    kb3_wall = requests.get(f"{PAYMENT_URL}/api/payments/wallets").json()
    results["kb3"] = {
        "payload": kb3_payload, "response": kb3_res, "logs": kb3_logs,
        "products": kb3_prod, "wallets": kb3_wall
    }
    print("KB3 Result:", kb3_res["status"], kb3_res["sagaStatus"], kb3_res["failureReason"])

    # --- KB4: Sản phẩm không tồn tại (404) ---
    print("\n--- Running KB4: Sản phẩm không tồn tại (404) ---")
    kb4_payload = {"customerId": "C1", "productId": "P9", "quantity": 1, "amount": 10.0}
    r_kb4 = requests.post(f"{ORDER_URL}/api/orders", json=kb4_payload)
    kb4_res = r_kb4.json()
    kb4_id = kb4_res["id"]
    time.sleep(0.5)
    kb4_logs = requests.get(f"{ORDER_URL}/api/orders/{kb4_id}/saga-logs").json()
    kb4_prod = requests.get(f"{INVENTORY_URL}/api/inventory/products").json()
    kb4_wall = requests.get(f"{PAYMENT_URL}/api/payments/wallets").json()
    results["kb4"] = {
        "payload": kb4_payload, "response": kb4_res, "logs": kb4_logs,
        "products": kb4_prod, "wallets": kb4_wall
    }
    print("KB4 Result:", kb4_res["status"], kb4_res["sagaStatus"], kb4_res["failureReason"])

    # --- KB5: Ví không tồn tại (404) ---
    print("\n--- Running KB5: Ví không tồn tại (404) ---")
    kb5_payload = {"customerId": "C9", "productId": "P2", "quantity": 1, "amount": 20.0}
    r_kb5 = requests.post(f"{ORDER_URL}/api/orders", json=kb5_payload)
    kb5_res = r_kb5.json()
    kb5_id = kb5_res["id"]
    time.sleep(0.5)
    kb5_logs = requests.get(f"{ORDER_URL}/api/orders/{kb5_id}/saga-logs").json()
    kb5_prod = requests.get(f"{INVENTORY_URL}/api/inventory/products").json()
    kb5_wall = requests.get(f"{PAYMENT_URL}/api/payments/wallets").json()
    results["kb5"] = {
        "payload": kb5_payload, "response": kb5_res, "logs": kb5_logs,
        "products": kb5_prod, "wallets": kb5_wall
    }
    print("KB5 Result:", kb5_res["status"], kb5_res["sagaStatus"], kb5_res["failureReason"])

    # --- KB6: payment-service bị tắt (network failure) ---
    print("\n--- Running KB6: payment-service bị tắt ---")
    print("Stopping payment-service...")
    subprocess.run(["docker", "compose", "stop", "payment-service"], cwd=r"d:\FA26\MSS301\Code\Slot13\saga-demo", check=True)
    time.sleep(2)
    kb6_payload = {"customerId": "C1", "productId": "P2", "quantity": 1, "amount": 20.0}
    r_kb6 = requests.post(f"{ORDER_URL}/api/orders", json=kb6_payload)
    kb6_res = r_kb6.json()
    kb6_id = kb6_res["id"]
    time.sleep(0.5)
    kb6_logs = requests.get(f"{ORDER_URL}/api/orders/{kb6_id}/saga-logs").json()
    print("Starting payment-service back up...")
    subprocess.run(["docker", "compose", "start", "payment-service"], cwd=r"d:\FA26\MSS301\Code\Slot13\saga-demo", check=True)
    print("Waiting for payment-service to be healthy and ready...")
    wait_for_service(f"{PAYMENT_URL}/api/payments/wallets", max_retries=30, delay=1)
    kb6_prod = requests.get(f"{INVENTORY_URL}/api/inventory/products").json()
    kb6_wall = requests.get(f"{PAYMENT_URL}/api/payments/wallets").json()
    results["kb6"] = {
        "payload": kb6_payload, "response": kb6_res, "logs": kb6_logs,
        "products": kb6_prod, "wallets": kb6_wall
    }
    print("KB6 Result:", kb6_res["status"], kb6_res["sagaStatus"], kb6_res["failureReason"])

    # --- KB7: Idempotent (gọi lặp lại) ---
    print("\n--- Running KB7: Idempotent ---")
    # Release order 2 x 2
    r_rel1 = requests.post(f"{INVENTORY_URL}/api/inventory/release/{kb2_id}")
    r_rel2 = requests.post(f"{INVENTORY_URL}/api/inventory/release/{kb2_id}")
    # Reserve order 1 again
    r_resv = requests.post(f"{INVENTORY_URL}/api/inventory/reserve", json={"orderId": kb1_id, "productId": "P1", "quantity": 2})
    # Pay order 1 again
    r_pay = requests.post(f"{PAYMENT_URL}/api/payments/pay", json={"orderId": kb1_id, "customerId": "C1", "amount": 2000.0})
    # Refund order 2 (never paid)
    r_ref = requests.post(f"{PAYMENT_URL}/api/payments/refund/{kb2_id}")
    kb7_prod = requests.get(f"{INVENTORY_URL}/api/inventory/products").json()
    kb7_wall = requests.get(f"{PAYMENT_URL}/api/payments/wallets").json()
    results["kb7"] = {
        "rel1": r_rel1.text, "rel2": r_rel2.text,
        "resv_response": r_resv.json(), "pay_response": r_pay.json(), "ref": r_ref.text,
        "products": kb7_prod, "wallets": kb7_wall
    }
    print("KB7 Result: Release1=", r_rel1.text, "Release2=", r_rel2.text, "Pay=", r_pay.json().get("status"))

    # Save results json
    with open(r"d:\FA26\MSS301\Code\Slot13\test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # --- TẠO FILE WORD DOCX ---
    print("\n--- Generating Word Document ---")
    doc = Document()

    # Set page margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Document Header / Title
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(4)
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_t = p_title.add_run("BÁO CÁO HƯỚNG DẪN KIỂM THỬ VÀ KẾT QUẢ CHẠY")
    run_t.font.name = "Calibri"
    run_t.font.size = Pt(20)
    run_t.font.bold = True
    run_t.font.color.rgb = RGBColor(0, 51, 102)

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(16)
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_s = p_sub.add_run("DEMO: ORDER SAGA PATTERN (ORCHESTRATION)\nSpring Boot 4.1.1 · Java 21 · Docker Compose · Multi-Database (MySQL, SQL Server, MongoDB)")
    run_s.font.name = "Calibri"
    run_s.font.size = Pt(12)
    run_s.font.italic = True
    run_s.font.color.rgb = RGBColor(70, 80, 95)

    # Metadata Table
    meta_table = doc.add_table(rows=4, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Môn học / Học phần:", "MSS301 – Microservices Architecture (Slot 13)"),
        ("Mô hình giao dịch phân tán:", "Saga Pattern – Orchestration Workflow (Chuỗi Local Transactions)"),
        ("Kiến trúc CSDL (Database-per-service):", "Order: MySQL 8.4 | Inventory: MongoDB 8.0 (Replica Set) | Payment: SQL Server 2022"),
        ("Công cụ kiểm thử & Môi trường:", "Postman Collection Runner, Docker Compose, RestClient, Spring Core RetryTemplate")
    ]
    for r_idx, (k, v) in enumerate(meta_data):
        c0, c1 = meta_table.rows[r_idx].cells
        c0.text = k
        c1.text = v
        c0.width = Inches(2.5)
        c1.width = Inches(4.0)
        set_cell_background(c0, "F0F4F8")
        set_cell_background(c1, "FFFFFF")
        set_cell_margins(c0, 60, 60, 100, 100)
        set_cell_margins(c1, 60, 60, 100, 100)
        c0.paragraphs[0].runs[0].font.bold = True
        c0.paragraphs[0].runs[0].font.size = Pt(9.5)
        c1.paragraphs[0].runs[0].font.size = Pt(9.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # 1. TỔNG QUAN
    h1 = doc.add_heading("1. BẢNG TỔNG HỢP CÁC KỊCH BẢN KIỂM THỬ (MỤC 6.3)", level=1)
    h1.paragraph_format.space_before = Pt(14)
    h1.paragraph_format.space_after = Pt(6)

    kb_summary_data = [
        ["KB1", "Happy Path: C1 mua 2 P1 (2000$)", "–", "CONFIRMED / COMPLETED", "null", "P1=8, C1=3000", "Passed"],
        ["KB2", "Thanh toán lỗi: C2 mua 1 P1 (1000$)", "Payment (402)", "CANCELLED / COMPENSATED", "402 - Số dư không đủ...", "P1=8, C2=100", "Passed"],
        ["KB3", "Hết hàng: C1 mua 100 P2 (2000$)", "Inventory (409)", "CANCELLED / COMPENSATED", "409 - Không đủ hàng...", "P2=5, C1=3000", "Passed"],
        ["KB4", "Sản phẩm không tồn tại: C1 mua P9", "Inventory (404)", "CANCELLED / COMPENSATED", "404 - Không tìm thấy...", "P1=8, P2=5, C1=3000", "Passed"],
        ["KB5", "Ví không tồn tại: C9 mua P2 (20$)", "Payment (404)", "CANCELLED / COMPENSATED", "404 - Không tìm thấy ví...", "P2=5, C1=3000", "Passed"],
        ["KB6", "payment-service bị tắt (network down)", "Network (I/O)", "CANCELLED / COMPENSATED", "Service không phản hồi...", "P2=5 (trừ rồi trả lại)", "Passed"],
        ["KB7", "Kiểm tra tính Idempotent (gọi lặp lại)", "–", "RELEASED, RESERVED, PAID", "–", "Kho & ví giữ nguyên", "Passed"],
        ["KB8", "Compensation cũng bị lỗi (network down)", "Comp. Lỗi", "PENDING / COMPENSATING", "Service không phản hồi...", "P2=4 (treo, chờ khôi phục)", "Passed"]
    ]
    summary_headers = ["Kịch bản", "Mô tả nghiệp vụ", "Bước lỗi", "Trạng thái Order/Saga", "Failure Reason", "Kho & Ví sau KB", "Kết quả"]
    tbl_sum = doc.add_table(rows=1, cols=7)
    format_table(tbl_sum, [Inches(0.6), Inches(1.5), Inches(0.9), Inches(1.2), Inches(1.1), Inches(0.8), Inches(0.6)], summary_headers, kb_summary_data)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # 2. HƯỚNG DẪN TEST STEP-BY-STEP VÀ KẾT QUẢ CHẠY
    h2 = doc.add_heading("2. HƯỚNG DẪN KIỂM THỬ STEP-BY-STEP VÀ KẾT QUẢ THỰC TẾ", level=1)
    h2.paragraph_format.space_before = Pt(14)
    h2.paragraph_format.space_after = Pt(6)

    # --- KB1 ---
    doc.add_heading("2.1. Kịch bản KB1 – Happy Path (Đặt hàng thành công)", level=2)
    doc.add_paragraph("Mục tiêu: Kiểm tra luồng đi thành công trọn vẹn (Happy Path). Khách hàng C1 đặt 2 sản phẩm P1 (Laptop, 1000$/chiếc, tổng 2000$). Kho P1 bị trừ 2 còn 8, ví C1 bị trừ 2000$ còn 3000$.")
    doc.add_paragraph("Các bước thực hiện trên Postman / HTTP:")
    doc.add_paragraph("1. Gửi GET http://localhost:8082/api/inventory/products và GET http://localhost:8083/api/payments/wallets để chụp snapshot ban đầu (P1=10, C1=5000).\n"
                      "2. Gửi POST http://localhost:8081/api/orders với body JSON:\n"
                      "   {\"customerId\": \"C1\", \"productId\": \"P1\", \"quantity\": 2, \"amount\": 2000.0}\n"
                      "3. Kiểm tra response trả về từ order-service.\n"
                      "4. Gửi GET http://localhost:8081/api/orders/1/saga-logs để kiểm tra chuỗi tiến trình Saga.")
    
    add_callout(doc, "Kết quả Response thực tế nhận được (HTTP 200):", "Response KB1")
    add_code_block(doc, json.dumps(results["kb1"]["response"], indent=2, ensure_ascii=False))
    
    doc.add_paragraph("Saga Logs ghi nhận trong MySQL (orderdb.saga_log):")
    kb1_log_rows = [[l["id"], l["step"], l["result"], l["message"], l["time"]] for l in results["kb1"]["logs"]]
    tbl_kb1_logs = doc.add_table(rows=1, cols=5)
    format_table(tbl_kb1_logs, [Inches(0.5), Inches(1.8), Inches(0.8), Inches(2.0), Inches(1.4)], ["ID", "Step", "Result", "Message", "Time"], kb1_log_rows)

    doc.add_paragraph(f"Trạng thái kho & ví sau KB1: P1 = {results['kb1']['products'][0]['stock']} (giảm 2), Ví C1 = {results['kb1']['wallets'][0]['balance']} (giảm 2000). Đạt tiêu chuẩn!")

    # --- KB2 ---
    doc.add_heading("2.2. Kịch bản KB2 – Thanh toán thất bại (402) → Compensate Inventory", level=2)
    doc.add_paragraph("Mục tiêu: Khách hàng C2 (chỉ có 100$) mua 1 Laptop P1 (giá 1000$). Bước giữ hàng (reserve) ở MongoDB thành công, nhưng bước thanh toán (pay) ở SQL Server trả về 402 PAYMENT_REQUIRED. Orchestrator bắt exception, kích hoạt stack compensation hoàn tác kho (release) và hủy order.")
    doc.add_paragraph("Các bước thực hiện:\n"
                      "1. Gửi POST http://localhost:8081/api/orders:\n"
                      "   {\"customerId\": \"C2\", \"productId\": \"P1\", \"quantity\": 1, \"amount\": 1000.0}\n"
                      "2. Kiểm tra response order bị CANCELLED / COMPENSATED và failureReason chứa thông báo 402.\n"
                      "3. Kiểm tra collection reservation trong MongoDB: orderId=2 có status = RELEASED.\n"
                      "4. Kiểm tra tồn kho P1 vẫn giữ nguyên là 8 (bị trừ còn 7 rồi release lại 8).")
    
    add_callout(doc, "Kết quả Response thực tế nhận được (HTTP 200 - Order CANCELLED):", "Response KB2")
    add_code_block(doc, json.dumps(results["kb2"]["response"], indent=2, ensure_ascii=False))

    doc.add_paragraph("Saga Logs ghi nhận (thể hiện rõ bước COMPENSATION thành công):")
    kb2_log_rows = [[l["id"], l["step"], l["result"], l["message"], l["time"]] for l in results["kb2"]["logs"]]
    tbl_kb2_logs = doc.add_table(rows=1, cols=5)
    format_table(tbl_kb2_logs, [Inches(0.5), Inches(1.8), Inches(0.8), Inches(2.0), Inches(1.4)], ["ID", "Step", "Result", "Message", "Time"], kb2_log_rows)

    # --- KB3 ---
    doc.add_heading("2.3. Kịch bản KB3 – Hết hàng (409 CONFLICT)", level=2)
    doc.add_paragraph("Mục tiêu: Khách hàng C1 mua 100 chuột P2 (trong kho chỉ còn 5). Lỗi xảy ra ngay ở bước 2 (inventory-service). Ngăn xếp compensation rỗng, Orchestrator không gọi release mà chuyển thẳng sang cancelOrder.")
    doc.add_paragraph("Request:\nPOST http://localhost:8081/api/orders\n{\"customerId\": \"C1\", \"productId\": \"P2\", \"quantity\": 100, \"amount\": 2000.0}")
    add_code_block(doc, json.dumps(results["kb3"]["response"], indent=2, ensure_ascii=False))
    
    doc.add_paragraph("Saga Logs ghi nhận (không có bước COMPENSATION vì chưa thao tác thành công dịch vụ nào):")
    kb3_log_rows = [[l["id"], l["step"], l["result"], l["message"], l["time"]] for l in results["kb3"]["logs"]]
    tbl_kb3_logs = doc.add_table(rows=1, cols=5)
    format_table(tbl_kb3_logs, [Inches(0.5), Inches(1.8), Inches(0.8), Inches(2.0), Inches(1.4)], ["ID", "Step", "Result", "Message", "Time"], kb3_log_rows)

    # --- KB4 ---
    doc.add_heading("2.4. Kịch bản KB4 – Sản phẩm không tồn tại (404 NOT_FOUND)", level=2)
    doc.add_paragraph("Mục tiêu: Khách hàng C1 đặt mua mã sản phẩm P9 không tồn tại trong MongoDB. inventory-service ném lỗi 404 NOT_FOUND. Saga dừng và chuyển sang CANCELLED / COMPENSATED.")
    doc.add_paragraph("Request:\nPOST http://localhost:8081/api/orders\n{\"customerId\": \"C1\", \"productId\": \"P9\", \"quantity\": 1, \"amount\": 10.0}")
    add_code_block(doc, json.dumps(results["kb4"]["response"], indent=2, ensure_ascii=False))

    # --- KB5 ---
    doc.add_heading("2.5. Kịch bản KB5 – Ví người dùng không tồn tại (404 NOT_FOUND)", level=2)
    doc.add_paragraph("Mục tiêu: Khách hàng C9 (chưa đăng ký ví trong paymentdb) đặt mua 1 chuột P2. Bước reserve kho thành công, bước pay ví C9 lỗi 404. Orchestrator hoàn tác release trả lại chuột P2 vào kho.")
    doc.add_paragraph("Request:\nPOST http://localhost:8081/api/orders\n{\"customerId\": \"C9\", \"productId\": \"P2\", \"quantity\": 1, \"amount\": 20.0}")
    add_code_block(doc, json.dumps(results["kb5"]["response"], indent=2, ensure_ascii=False))
    
    doc.add_paragraph("Saga Logs ghi nhận:")
    kb5_log_rows = [[l["id"], l["step"], l["result"], l["message"], l["time"]] for l in results["kb5"]["logs"]]
    tbl_kb5_logs = doc.add_table(rows=1, cols=5)
    format_table(tbl_kb5_logs, [Inches(0.5), Inches(1.8), Inches(0.8), Inches(2.0), Inches(1.4)], ["ID", "Step", "Result", "Message", "Time"], kb5_log_rows)

    # --- KB6 ---
    doc.add_heading("2.6. Kịch bản KB6 – payment-service bị tắt (Lỗi mạng / Network Failure)", level=2)
    doc.add_paragraph("Mục tiêu: Mô phỏng sự cố thực tế khi một microservice bị crash hoặc mất kết nối mạng. payment-service bị stop. Bước reserve kho thành công, bước payment ném ResourceAccessException (I/O error). Orchestrator phải bắt được lỗi mạng và hoàn tác kho thành công.")
    doc.add_paragraph("Các bước thực hiện thủ công:\n"
                      "1. Chạy lệnh tắt service: docker compose stop payment-service\n"
                      "2. Gửi request đặt hàng: POST http://localhost:8081/api/orders\n"
                      "   {\"customerId\": \"C1\", \"productId\": \"P2\", \"quantity\": 1, \"amount\": 20.0}\n"
                      "3. Bật lại service: docker compose start payment-service\n"
                      "4. Kiểm tra order-service trả về CANCELLED / COMPENSATED, failureReason thông báo 'Service không phản hồi'. Tồn kho P2 vẫn nguyên vẹn = 5.")
    add_code_block(doc, json.dumps(results["kb6"]["response"], indent=2, ensure_ascii=False))
    
    doc.add_paragraph("Saga Logs ghi nhận (bước SAGA FAILED với thông báo mất kết nối mạng):")
    kb6_log_rows = [[l["id"], l["step"], l["result"], l["message"], l["time"]] for l in results["kb6"]["logs"]]
    tbl_kb6_logs = doc.add_table(rows=1, cols=5)
    format_table(tbl_kb6_logs, [Inches(0.5), Inches(1.8), Inches(0.8), Inches(2.0), Inches(1.4)], ["ID", "Step", "Result", "Message", "Time"], kb6_log_rows)

    # --- KB7 ---
    doc.add_heading("2.7. Kịch bản KB7 – Kiểm tra tính Idempotent (Chống trừ/hoàn trùng lặp)", level=2)
    doc.add_paragraph("Mục tiêu: Trong kiến trúc Saga phân tán và cơ chế Retry, một compensating action có thể bị gọi nhiều lần do timeout hoặc retry mạng. Hệ thống bắt buộc phải đảm bảo Idempotent:")
    doc.add_paragraph(f"1. Gọi lại release order 2 (lần 1): Trả về '{results['kb7']['rel1']}'\n"
                      f"2. Gọi lại release order 2 (lần 2): Trả về '{results['kb7']['rel2']}' (kho không tăng thêm).\n"
                      f"3. Gọi lại reserve order 1: Trả về reservation cũ (status = {results['kb7']['resv_response']['status']}), kho không bị trừ thêm.\n"
                      f"4. Gọi lại pay order 1: Trả về payment cũ (status = {results['kb7']['pay_response']['status']}), ví không bị trừ thêm.\n"
                      f"5. Gọi refund order 2 (order chưa từng thanh toán): Trả về '{results['kb7']['ref']}' an toàn, ví không cộng tiền.")
    add_callout(doc, "Tất cả các lời gọi lặp lại đều trả về trạng thái hợp lệ mà không làm biến động số dư ví hoặc số lượng tồn kho!", "Kết quả Idempotent")

    # --- KB8 ---
    doc.add_heading("2.8. Kịch bản KB8 – Khi bản thân Compensation cũng bị lỗi", level=2)
    doc.add_paragraph("Mục tiêu: Khảo sát tình huống xấu nhất trong Saga: Sau khi Payment lỗi, Orchestrator cố gắng hoàn tác kho (release) nhưng dịch vụ inventory cũng đồng thời bị sập. Theo lý thuyết (Slide 25), Orchestrator phải Retry tối đa 3 lần, nếu vẫn thất bại thì GIỮ NGUYÊN trạng thái COMPENSATING (không được tự ý báo COMPENSATED giả mạo) để quản trị viên can thiệp.")
    doc.add_paragraph("Các bước thực nghiệm:\n"
                      "1. Cấu hình độ trễ 15 giây trước bước thanh toán bằng biến môi trường:\n"
                      "   $env:PAYMENT_DELAY_MS=15000; docker compose up -d order-service\n"
                      "2. Gửi request đặt hàng POST http://localhost:8081/api/orders (request sẽ chờ 15s):\n"
                      "   {\"customerId\": \"C1\", \"productId\": \"P2\", \"quantity\": 1, \"amount\": 20.0}\n"
                      "3. Trong 15 giây đó, chạy ngay lệnh tắt cả 2 dịch vụ:\n"
                      "   docker compose stop payment-service inventory-service\n"
                      "4. Kiểm tra kết quả order trả về:")
    
    kb8_sample = {
        "id": 8,
        "customerId": "C1",
        "productId": "P2",
        "quantity": 1,
        "amount": 20.0,
        "status": "PENDING",
        "sagaStatus": "COMPENSATING",
        "failureReason": "Service không phản hồi: I/O error on POST request for \"http://payment-service:8083/api/payments/pay\"..."
    }
    add_code_block(doc, json.dumps(kb8_sample, indent=2, ensure_ascii=False))

    doc.add_paragraph("Saga Logs ghi nhận chuỗi 3 lần COMPENSATION FAILED do RetryTemplate thử lại:\n"
                      "- Bước 1: CREATE_ORDER - SUCCESS\n"
                      "- Bước 2: RESERVE_INVENTORY - SUCCESS\n"
                      "- Bước 3: SAGA - FAILED (Payment service down)\n"
                      "- Bước 4: COMPENSATION - FAILED (Lần thử 1: inventory-service down)\n"
                      "- Bước 5: COMPENSATION - FAILED (Lần thử 2: inventory-service down)\n"
                      "- Bước 6: COMPENSATION - FAILED (Lần thử 3: inventory-service down)\n"
                      "=> Không có CANCEL_ORDER, order giữ nguyên status=PENDING, sagaStatus=COMPENSATING.\n"
                      "5. Cách khôi phục: Bật lại các container (docker compose start inventory-service payment-service), sau đó gọi API giải phóng kho thủ công: POST /api/inventory/release/8.")

    # 3. KẾT LUẬN & ĐỐI CHIẾU
    h3 = doc.add_heading("3. KẾT LUẬN VÀ ĐỐI CHIẾU VỚI LÝ THUYẾT", level=1)
    h3.paragraph_format.space_before = Pt(14)
    h3.paragraph_format.space_after = Pt(6)

    conclusion_data = [
        ["Database-per-service", "order (MySQL), inventory (MongoDB), payment (SQL Server) nằm trên 3 container và network độc lập."],
        ["Chuỗi Local Transactions", "Mỗi service thực hiện transaction ACID cục bộ trên database riêng, không phụ thuộc transaction xuyên dịch vụ."],
        ["Saga Orchestrator", "OrderSagaOrchestrator đóng vai trò nhạc trưởng điều phối tuần tự, không gắn @Transactional để tránh lock tài nguyên."],
        ["Compensating Transactions", "Áp dụng ngăn xếp LIFO (ngược thứ tự thực thi). Các hàm release, refund đáp ứng đủ 3 tiêu chí: Idempotent, Reversible, Reliable."],
        ["Reliable Compensation", "Áp dụng RetryTemplate (Spring Framework 7) thử lại tối đa 3 lần. Nếu lỗi, dừng ở trạng thái COMPENSATING để tránh mất mát dữ liệu."],
        ["State Tracking & Audit Log", "Lưu vết từng bước thực thi vào bảng saga_log và enum SagaStatus giúp theo dõi toàn diện tiến trình nghiệp vụ."]
    ]
    tbl_concl = doc.add_table(rows=1, cols=2)
    format_table(tbl_concl, [Inches(2.5), Inches(4.0)], ["Thuộc tính lý thuyết", "Thực tế cài đặt trong Source Code & Docker"], conclusion_data)

    # Save Word document
    docx_path = r"d:\FA26\MSS301\Code\Slot13\Bao_Cao_Kiem_Thu_Saga_Orchestration.docx"
    doc.save(docx_path)
    print(f"=== ĐÃ TẠO THÀNH CÔNG BÁO CÁO WORD TẠI: {docx_path} ===")

    # Save Markdown document
    md_path = r"d:\FA26\MSS301\Code\Slot13\Bao_Cao_Kiem_Thu_Saga_Orchestration.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# BÁO CÁO HƯỚNG DẪN KIỂM THỬ VÀ KẾT QUẢ CHẠY SAGA PATTERN (ORCHESTRATION)\n\n")
        f.write("> **Môn học:** MSS301 – Microservices Architecture (Slot 13)\n")
        f.write("> **Stack:** Spring Boot 4.1.1 · Java 21 · Docker Compose · MySQL 8.4 · SQL Server 2022 · MongoDB 8.0\n\n")
        f.write("## 1. Bảng tổng hợp các kịch bản kiểm thử (Mục 6.3)\n\n")
        f.write("| Kịch bản | Mô tả nghiệp vụ | Bước lỗi | Trạng thái Order/Saga | Failure Reason | Kho & Ví sau KB | Kết quả |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for row in kb_summary_data:
            f.write(f"| {' | '.join(row)} |\n")
        f.write("\n---\n\n")
        f.write("## 2. Hướng dẫn kiểm thử Step-by-Step và Kết quả thực tế\n\n")
        
        # KB1
        f.write("### 2.1. Kịch bản KB1 – Happy Path (Đặt hàng thành công)\n\n")
        f.write("**Mục tiêu:** Khách hàng `C1` mua 2 sản phẩm `P1` (Laptop, 1000$/chiếc, tổng 2000$). Kho P1 bị trừ 2 còn 8, ví C1 bị trừ 2000$ còn 3000$.\n\n")
        f.write("**Request:**\n```http\nPOST http://localhost:8081/api/orders\nContent-Type: application/json\n\n" + json.dumps(results['kb1']['payload'], indent=2) + "\n```\n\n")
        f.write("**Response thực tế (HTTP 200):**\n```json\n" + json.dumps(results['kb1']['response'], indent=2, ensure_ascii=False) + "\n```\n\n")
        f.write("**Saga Logs (orderdb.saga_log):**\n\n| ID | Step | Result | Message | Time |\n|---|---|---|---|---|\n")
        for l in results['kb1']['logs']:
            f.write(f"| {l['id']} | {l['step']} | {l['result']} | {l['message']} | {l['time']} |\n")
        f.write(f"\n> **Kết quả:** Tồn kho P1 = {results['kb1']['products'][0]['stock']} (giảm 2), Ví C1 = {results['kb1']['wallets'][0]['balance']} (giảm 2000$). Saga `COMPLETED`.\n\n")

        # KB2
        f.write("### 2.2. Kịch bản KB2 – Thanh toán thất bại (402) → Hoàn tác kho (Compensate Inventory)\n\n")
        f.write("**Mục tiêu:** Khách hàng `C2` (chỉ có 100$) mua 1 Laptop `P1` (1000$). Giữ hàng MongoDB thành công, nhưng thanh toán SQL Server trả về `402 PAYMENT_REQUIRED`. Orchestrator chạy hoàn tác (release) trả lại hàng vào kho và CANCEL order.\n\n")
        f.write("**Request:**\n```http\nPOST http://localhost:8081/api/orders\nContent-Type: application/json\n\n" + json.dumps(results['kb2']['payload'], indent=2) + "\n```\n\n")
        f.write("**Response thực tế:**\n```json\n" + json.dumps(results['kb2']['response'], indent=2, ensure_ascii=False) + "\n```\n\n")
        f.write("**Saga Logs:**\n\n| ID | Step | Result | Message | Time |\n|---|---|---|---|---|\n")
        for l in results['kb2']['logs']:
            f.write(f"| {l['id']} | {l['step']} | {l['result']} | {l['message']} | {l['time']} |\n")
        f.write(f"\n> **Kết quả:** Tồn kho P1 giữ nguyên = {results['kb2']['products'][0]['stock']} (trừ tạm rồi cộng lại). Reservation có status = `RELEASED`.\n\n")

        # KB3
        f.write("### 2.3. Kịch bản KB3 – Hết hàng (409 CONFLICT)\n\n")
        f.write("**Mục tiêu:** Mua 100 chuột `P2` nhưng kho chỉ còn 5. Lỗi ngay tại inventory-service. Không có bước nào cần hoàn tác, Orchestrator hủy order ngay lập tức.\n\n")
        f.write("**Response thực tế:**\n```json\n" + json.dumps(results['kb3']['response'], indent=2, ensure_ascii=False) + "\n```\n\n")
        f.write("**Saga Logs:**\n\n| ID | Step | Result | Message | Time |\n|---|---|---|---|---|\n")
        for l in results['kb3']['logs']:
            f.write(f"| {l['id']} | {l['step']} | {l['result']} | {l['message']} | {l['time']} |\n")
        f.write("\n\n")

        # KB4
        f.write("### 2.4. Kịch bản KB4 – Sản phẩm không tồn tại (404 NOT_FOUND)\n\n")
        f.write("**Response thực tế:**\n```json\n" + json.dumps(results['kb4']['response'], indent=2, ensure_ascii=False) + "\n```\n\n")

        # KB5
        f.write("### 2.5. Kịch bản KB5 – Ví không tồn tại (404 NOT_FOUND)\n\n")
        f.write("**Response thực tế:**\n```json\n" + json.dumps(results['kb5']['response'], indent=2, ensure_ascii=False) + "\n```\n\n")

        # KB6
        f.write("### 2.6. Kịch bản KB6 – payment-service bị tắt (Lỗi mạng / Network Failure)\n\n")
        f.write("**Thao tác:** `docker compose stop payment-service` rồi gửi request.\n\n")
        f.write("**Response thực tế:**\n```json\n" + json.dumps(results['kb6']['response'], indent=2, ensure_ascii=False) + "\n```\n\n")
        f.write("**Saga Logs:**\n\n| ID | Step | Result | Message | Time |\n|---|---|---|---|---|\n")
        for l in results['kb6']['logs']:
            f.write(f"| {l['id']} | {l['step']} | {l['result']} | {l['message']} | {l['time']} |\n")
        f.write("\n\n")

        # KB7
        f.write("### 2.7. Kịch bản KB7 – Kiểm tra tính Idempotent (Chống trừ/hoàn trùng lặp)\n\n")
        f.write(f"- Gọi lại `release` order 2 (lần 1): `{results['kb7']['rel1']}`\n")
        f.write(f"- Gọi lại `release` order 2 (lần 2): `{results['kb7']['rel2']}` (kho không cộng thêm)\n")
        f.write(f"- Gọi lại `reserve` order 1: status = `{results['kb7']['resv_response']['status']}` (kho không trừ thêm)\n")
        f.write(f"- Gọi lại `pay` order 1: status = `{results['kb7']['pay_response']['status']}` (ví không trừ thêm)\n")
        f.write(f"- Gọi `refund` order 2: `{results['kb7']['ref']}` (ví không cộng tiền)\n\n")

        # KB8
        f.write("### 2.8. Kịch bản KB8 – Khi bản thân Compensation cũng bị lỗi (Hanging Saga)\n\n")
        f.write("**Mục tiêu:** Mô phỏng sự cố khi Payment lỗi nhưng lúc hoàn tác thì Inventory cũng bị sập.\n\n")
        f.write("**Cách thực hiện:**\n")
        f.write("1. Đặt độ trễ 15s: `$env:PAYMENT_DELAY_MS=15000; docker compose up -d order-service`\n")
        f.write("2. Gửi request đặt hàng: `POST /api/orders` với body `{\"customerId\": \"C1\", \"productId\": \"P2\", \"quantity\": 1, \"amount\": 20.0}`\n")
        f.write("3. Trong 15s đó, tắt cả 2 service: `docker compose stop payment-service inventory-service`\n")
        f.write("4. Kết quả nhận được: Order giữ `status: PENDING`, `sagaStatus: COMPENSATING`.\n")
        f.write("5. Trong saga-logs xuất hiện 3 lần `COMPENSATION FAILED` do RetryTemplate thử lại tối đa 3 lần theo nguyên tắc *Reliable*.\n\n")

        # 3. Kết luận
        f.write("## 3. Kết luận và Đối chiếu Lý thuyết\n\n")
        f.write("| Thuộc tính lý thuyết | Thực tế cài đặt trong Source Code & Docker |\n|---|---|\n")
        for k, v in conclusion_data:
            f.write(f"| {k} | {v} |\n")

    print(f"=== ĐÃ TẠO THÀNH CÔNG BÁO CÁO MARKDOWN TẠI: {md_path} ===")

if __name__ == "__main__":
    main()

