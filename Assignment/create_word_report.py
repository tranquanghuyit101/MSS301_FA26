import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

BASE_DIR = os.path.dirname(__file__)
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
TEMPLATE_PATH = os.path.join(BASE_DIR, "Assignment 1_template.docx")
OUTPUT_PATH = os.path.join(BASE_DIR, "Assignment 1_Report.docx")

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def add_commit_box(doc, todo_id, commit_msg, branch="main", body=""):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    set_cell_background(cell, "F3F4F6")
    set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    
    r_label = p.add_run("Commit Message: ")
    r_label.bold = True
    r_label.font.name = "Consolas"
    r_label.font.size = Pt(10)
    r_label.font.color.rgb = RGBColor(30, 41, 59)
    
    r_msg = p.add_run(commit_msg)
    r_msg.bold = True
    r_msg.font.name = "Consolas"
    r_msg.font.size = Pt(10)
    r_msg.font.color.rgb = RGBColor(15, 118, 110)
    
    p2 = cell.add_paragraph()
    p2.paragraph_format.space_before = Pt(2)
    p2.paragraph_format.space_after = Pt(2)
    r_ref = p2.add_run(f"Refs: {todo_id} | Branch: {branch}")
    r_ref.font.name = "Consolas"
    r_ref.font.size = Pt(9)
    r_ref.font.color.rgb = RGBColor(100, 116, 139)
    
    if body:
        p3 = cell.add_paragraph()
        p3.paragraph_format.space_before = Pt(2)
        p3.paragraph_format.space_after = Pt(2)
        r_body = p3.add_run(body)
        r_body.font.name = "Consolas"
        r_body.font.size = Pt(9)
        r_body.font.color.rgb = RGBColor(71, 85, 105)
        
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def add_screenshot(doc, img_name, caption):
    img_path = os.path.join(SCREENSHOTS_DIR, img_name)
    if os.path.exists(img_path):
        doc.add_paragraph().paragraph_format.space_after = Pt(2)
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p_img.add_run()
        run.add_picture(img_path, width=Inches(6.2))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(2)
        p_cap.paragraph_format.space_after = Pt(8)
        r_cap = p_cap.add_run(f"Hình: {caption}")
        r_cap.italic = True
        r_cap.font.size = Pt(9.5)
        r_cap.font.color.rgb = RGBColor(100, 116, 139)
    else:
        print(f"Warning: Image {img_name} not found!")

def add_toc_field(doc):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run()
    fldChar1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls('w'))
    instrText = parse_xml(r'<w:instrText %s xml:space="preserve"> TOC \o "1-3" \h \z \u </w:instrText>' % nsdecls('w'))
    fldChar2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls('w'))
    fldChar3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls('w'))
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)

def add_prefilled_toc_item(doc, text, page_num, level=1):
    p = doc.add_paragraph(style=f'toc {level}')
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    pPr = p._p.get_or_add_pPr()
    tabs = parse_xml(r'<w:tabs %s><w:tab w:val="right" w:leader="dot" w:pos="9000"/></w:tabs>' % nsdecls('w'))
    pPr.append(tabs)
    
    r1 = p.add_run(text)
    r1.font.name = "Segoe UI"
    if level == 1:
        r1.bold = True
        r1.font.size = Pt(10.5)
        r1.font.color.rgb = RGBColor(15, 23, 42)
    else:
        r1.font.size = Pt(10)
        r1.font.color.rgb = RGBColor(51, 65, 85)
        
    r_tab = p.add_run("\t")
    r2 = p.add_run(str(page_num))
    r2.font.name = "Segoe UI"
    r2.font.size = Pt(10)
    r2.font.color.rgb = RGBColor(71, 85, 105)

def build_full_report():
    doc = docx.Document(TEMPLATE_PATH)
    
    # Enable automatic TOC update upon opening in Word
    settings = doc.settings._element
    w_updateFields = parse_xml(r'<w:updateFields %s w:val="true"/>' % nsdecls('w'))
    settings.append(w_updateFields)
    
    # Clear existing template sample paragraphs
    for p in list(doc.paragraphs):
        p._element.getparent().remove(p._element)
        
    # ==================== COVER PAGE ====================
    p_uni = doc.add_paragraph()
    p_uni.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_uni.paragraph_format.space_before = Pt(20)
    p_uni.paragraph_format.space_after = Pt(2)
    r_uni = p_uni.add_run("TRƯỜNG ĐẠI HỌC FPT ĐÀ NẴNG")
    r_uni.bold = True
    r_uni.font.name = "Segoe UI"
    r_uni.font.size = Pt(16)
    r_uni.font.color.rgb = RGBColor(249, 115, 22) # FPT Orange
    
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(40)
    r_sub = p_sub.add_run("KHOA CÔNG NGHỆ THÔNG TIN - BỘ MÔN KỸ THUẬT PHẦN MỀM")
    r_sub.font.name = "Segoe UI"
    r_sub.font.size = Pt(11)
    r_sub.font.color.rgb = RGBColor(100, 116, 139)
    
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(20)
    p_title.paragraph_format.space_after = Pt(10)
    r_title = p_title.add_run("BÁO CÁO BÀI TẬP LỚN\nASSIGNMENT 1")
    r_title.bold = True
    r_title.font.name = "Segoe UI"
    r_title.font.size = Pt(24)
    r_title.font.color.rgb = RGBColor(15, 23, 42)
    
    p_course = doc.add_paragraph()
    p_course.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_course.paragraph_format.space_after = Pt(15)
    r_course = p_course.add_run("HỌC PHẦN: MSS301 - KIẾN TRÚC MICROSERVICES & HỆ THỐNG PHÂN TÁN")
    r_course.bold = True
    r_course.font.name = "Segoe UI"
    r_course.font.size = Pt(13)
    r_course.font.color.rgb = RGBColor(2, 132, 199)
    
    p_topic = doc.add_paragraph()
    p_topic.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_topic.paragraph_format.space_after = Pt(60)
    r_topic = p_topic.add_run("Đề tài: Hệ Thống Đặt Vé Xem Phim FUCinema (Cinema Ticket Booking System)\nSử dụng Spring Cloud API Gateway & Polyglot Persistence")
    r_topic.italic = True
    r_topic.font.name = "Segoe UI"
    r_topic.font.size = Pt(12)
    r_topic.font.color.rgb = RGBColor(71, 85, 105)
    
    # Student Info Box
    table_info = doc.add_table(rows=6, cols=2)
    table_info.alignment = WD_TABLE_ALIGNMENT.CENTER
    info_data = [
        ("Sinh viên thực hiện:", "Trần Quang Huy"),
        ("Mã số sinh viên (MSSV):", "DE190353"),
        ("Lớp học phần:", "SE19B04"),
        ("Giảng viên hướng dẫn:", "traltb@fe.edu.vn"),
        ("Đường dẫn GitHub:", "https://github.com/tranquanghuyit101/MSS301_FA26"),
        ("Thời gian hoàn thành:", "Tháng 10 / 2026")
    ]
    for row_idx, (lbl, val) in enumerate(info_data):
        c1 = table_info.cell(row_idx, 0)
        c2 = table_info.cell(row_idx, 1)
        set_cell_background(c1, "F8FAFC")
        set_cell_background(c2, "FFFFFF")
        set_cell_margins(c1, top=80, bottom=80, left=120, right=120)
        set_cell_margins(c2, top=80, bottom=80, left=120, right=120)
        p1 = c1.paragraphs[0]
        r1 = p1.add_run(lbl)
        r1.bold = True
        r1.font.name = "Segoe UI"
        r1.font.size = Pt(10.5)
        p2 = c2.paragraphs[0]
        r2 = p2.add_run(val)
        r2.font.name = "Segoe UI"
        r2.font.size = Pt(10.5)
        if "http" in val:
            r2.bold = True
            r2.font.color.rgb = RGBColor(2, 132, 199)
            
    doc.add_page_break()
    
    # ==================== TABLE OF CONTENTS ====================
    h_toc = doc.add_heading("MỤC LỤC TỰ ĐỘNG", level=1)
    h_toc.paragraph_format.space_before = Pt(10)
    h_toc.paragraph_format.space_after = Pt(15)
    
    # Native Word TOC field code
    add_toc_field(doc)
    
    # Pre-populated stylized visual TOC entries
    toc_items = [
        ("PHẦN 1: TỔNG QUAN KIẾN TRÚC HỆ THỐNG FUCINEMA", 3, 1),
        ("1.1 Mô hình kiến trúc Microservices & Polyglot Persistence", 3, 2),
        ("1.2 Danh mục các dịch vụ và cổng phân công", 3, 2),
        ("1.3 Cơ chế phân quyền và bảo mật toàn diện", 4, 2),
        ("PHẦN 2: CHI TIẾT THỰC HIỆN TỪNG TÍNH NĂNG & TODO", 5, 1),
        ("F0 – Hạ tầng & Khởi tạo dự án (Infrastructure)", 5, 2),
        ("F1 – Xác thực & Quản lý phiên làm việc (Authentication)", 8, 2),
        ("F2 – Hồ sơ khách hàng (Customer Register & Profile)", 11, 2),
        ("F3 – Quản trị viên quản lý khách hàng (Admin Customers)", 14, 2),
        ("F4 – Quản lý Thể loại & Phòng chiếu (Genre & Cinema Room)", 16, 2),
        ("F5 – Quản lý Phim & Tìm kiếm động (Movie Management)", 19, 2),
        ("F6 – Quản lý Suất chiếu & Trùng lịch (Showtime Management)", 22, 2),
        ("F7 – Đặt vé xem phim & Sơ đồ ghế (Create Booking & Seat Map)", 25, 2),
        ("F8 – Lịch sử & Hủy vé xem phim (History & Cancellation)", 28, 2),
        ("F9 – Thống kê & Báo cáo doanh thu (Revenue Report)", 31, 2),
        ("F10 – API Gateway & Định tuyến bảo mật (Gateway Security)", 33, 2),
        ("F11 – Kiểm thử tích hợp tự động với Postman & Newman", 36, 2),
        ("PHẦN 3: BẢNG TỔNG HỢP KIỂM THỬ & TIÊU CHÍ NGHIỆM THU", 38, 1),
        ("3.1 Kết quả chạy kiểm thử Newman CLI tự động", 38, 2),
        ("3.2 Bảng đối chiếu 15 Quy tắc nghiệp vụ (Business Rules BR01 - BR15)", 39, 2),
        ("3.3 Kết luận & Đánh giá mức độ hoàn thành bài tập lớn", 40, 2)
    ]
    for title, pg, lvl in toc_items:
        add_prefilled_toc_item(doc, title, pg, level=lvl)
        
    doc.add_page_break()
    
    # ==================== PHẦN 1 ====================
    h1 = doc.add_heading("PHẦN 1: TỔNG QUAN KIẾN TRÚC HỆ THỐNG FUCINEMA", level=1)
    
    p = doc.add_paragraph()
    p.add_run("Hệ thống đặt vé xem phim ").font.name = "Segoe UI"
    r = p.add_run("FUCinemaBookingSystem")
    r.bold = True
    p.add_run(" được thiết kế và hiện thực hóa theo kiến trúc Microservices hiện đại, giải quyết triệt để bài toán mở rộng độc lập, cô lập lỗi và tối ưu hóa việc lưu trữ dữ liệu chuyên biệt (Polyglot Persistence). Toàn bộ hệ thống giao tiếp thông qua Spring Cloud API Gateway làm cổng truy cập duy nhất (Single Point of Entry) kết hợp cùng cơ chế xác thực tập trung JWT (JSON Web Token HS256).")
    
    doc.add_heading("1.1 Mô hình kiến trúc Microservices & Polyglot Persistence", level=2)
    p = doc.add_paragraph()
    p.add_run("Hệ thống gồm 4 microservices độc lập được phân chia ranh giới ngữ cảnh (Bounded Context) rõ ràng:")
    
    bullets = [
        ("api-gateway (Cổng 9000): ", "Điểm đón nhận toàn bộ lưu lượng truy cập từ Client, kiểm tra tính hợp lệ của JWT access token, bóc tách thông tin định danh (userId, email, role) đưa vào HTTP Header (X-User-Id, X-User-Email, X-User-Role) chuyển tiếp cho các service nội bộ, đồng thời thực thi bộ lọc bảo vệ ngăn chặn giả mạo Header."),
        ("customer-service (Cổng 8081): ", "Quản lý định danh người dùng, xác thực đăng nhập tài khoản Admin (in-memory) và Khách hàng (database), mã hóa mật khẩu chuẩn BCrypt, ký phát JWT HS256, và cung cấp API quản lý hồ sơ khách hàng. Sử dụng Microsoft SQL Server 2022 để lưu trữ với hỗ trợ Unicode (NVARCHAR)."),
        ("movie-service (Cổng 8082): ", "Quản lý dữ liệu danh mục thể loại phim (Genre), phòng chiếu (CinemaRoom), phim (Movie) và lịch chiếu (Showtime). Sử dụng MongoDB 7.0.5 lưu trữ NoSQL linh hoạt, hỗ trợ tìm kiếm động nhiều tiêu chí bằng MongoTemplate Criteria và chống trùng lịch phòng chiếu."),
        ("booking-service (Cổng 8083): ", "Xử lý nghiệp vụ đặt vé xem phim cốt lõi, sinh sơ đồ ghế ngồi theo thời gian thực (Seat Map), kiểm tra xung đột trùng ghế (Double-booking Prevention), lưu trữ giao dịch đơn hàng và tính toán báo cáo doanh thu. Sử dụng MySQL 8.3.0 lưu trữ quan hệ và tích hợp OpenFeign để giao tiếp đồng bộ với movie-service.")
    ]
    for b_title, b_desc in bullets:
        bp = doc.add_paragraph(style='List Paragraph')
        r_bullet = bp.add_run("• ")
        r_bullet.bold = True
        r_bt = bp.add_run(b_title)
        r_bt.bold = True
        bp.add_run(b_desc)
        
    doc.add_heading("1.2 Bảng tổng hợp công nghệ & phân bổ cổng kết nối", level=2)
    tbl_tech = doc.add_table(rows=5, cols=4)
    tbl_tech.alignment = WD_TABLE_ALIGNMENT.CENTER
    tech_data = [
        ("Microservice", "Cổng (Port)", "Hệ quản trị CSDL", "Công nghệ & Thư viện chính"),
        ("api-gateway", "9000", "Không dùng DB", "Spring Cloud Gateway WebMVC, OAuth2 Resource Server, Nimbus JWT"),
        ("customer-service", "8081", "SQL Server 2022 (Port 1433)", "Spring Data JPA, Hibernate, Flyway Migration, Spring Crypto BCrypt"),
        ("movie-service", "8082", "MongoDB 7.0.5 (Port 27017)", "Spring Data MongoDB, MongoTemplate, Criteria API, CommandLineRunner"),
        ("booking-service", "8083", "MySQL 8.3.0 (Port 3306)", "Spring Data JPA, Spring Cloud OpenFeign, Flyway Migration, MySQL Connector")
    ]
    for r_idx, row in enumerate(tech_data):
        for c_idx, val in enumerate(row):
            cell = tbl_tech.cell(r_idx, c_idx)
            set_cell_margins(cell, 80, 80, 100, 100)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Segoe UI"
            r.font.size = Pt(9.5)
            if r_idx == 0:
                r.bold = True
                set_cell_background(cell, "0284C7")
                r.font.color.rgb = RGBColor(255, 255, 255)
            else:
                set_cell_background(cell, "F8FAFC" if r_idx % 2 == 1 else "FFFFFF")
                
    doc.add_paragraph().paragraph_format.space_after = Pt(10)
    doc.add_page_break()

    # ==================== PHẦN 2 ====================
    doc.add_heading("PHẦN 2: CHI TIẾT THỰC HIỆN TỪNG TÍNH NĂNG & TODO", level=1)
    
    # ---------- F0 ----------
    doc.add_heading("F0 – Hạ tầng & Khởi tạo dự án (Infrastructure)", level=2)
    
    doc.add_heading("TODO 0.1: Khởi tạo Docker Compose cho Polyglot Databases", level=3)
    p = doc.add_paragraph()
    p.add_run("Tạo file ")
    p.add_run("fu-cinema/docker-compose.yml").bold = True
    p.add_run(" định nghĩa và kích hoạt đồng thời 3 hệ quản trị cơ sở dữ liệu: SQL Server 2022 (cho customer-service), MongoDB 7.0.5 (cho movie-service) và MySQL 8.3.0 (cho booking-service). Cấu hình healthcheck và volume bền vững.")
    add_commit_box(doc, "TODO 0.1", "chore(infra): add docker compose for sql server, mongodb and mysql", "feature/f0-infrastructure")
    add_screenshot(doc, "f0_todo01_docker_compose.png", "Trạng thái các container cơ sở dữ liệu đang chạy ổn định")
    
    doc.add_heading("TODO 0.2: Script khởi tạo database cho SQL Server và MySQL", level=3)
    p = doc.add_paragraph()
    p.add_run("Tạo các tệp script khởi tạo: ")
    p.add_run("fu-cinema/sqlserver/init.sql").bold = True
    p.add_run(" tạo database ")
    p.add_run("cinema_customer").bold = True
    p.add_run("; và ")
    p.add_run("fu-cinema/mysql/init.sql").bold = True
    p.add_run(" tạo database ")
    p.add_run("cinema_booking").bold = True
    p.add_run(". Đảm bảo tính sẵn sàng trước khi các microservice khởi chạy.")
    add_commit_box(doc, "TODO 0.2", "chore(infra): add init scripts for sql server and mysql databases", "feature/f0-infrastructure")
    add_screenshot(doc, "f0_todo02_db_init.png", "Kiểm tra sự tồn tại của các database Polyglot trên các máy chủ CSDL")
    
    doc.add_heading("TODO 0.3: Bootstrap 3 service nghiệp vụ (customer, movie, booking)", level=3)
    p = doc.add_paragraph()
    p.add_run("Khởi tạo cấu trúc dự án Maven đa mô-đun với Java 21 và Spring Boot 4.1.0. Tích hợp driver kết nối tương ứng và chạy lệnh ")
    p.add_run("mvn clean compile").bold = True
    p.add_run(" kiểm tra biên dịch thành công 100%.")
    add_commit_box(doc, "TODO 0.3", "build(customer): bootstrap customer-service with sql server driver and flyway\nbuild(movie): bootstrap movie-service with spring data mongodb\nbuild(booking): bootstrap booking-service with mysql and flyway", "feature/f0-infrastructure")
    add_screenshot(doc, "f0_todo03_bootstrap_services.png", "Kết quả build Maven thành công (BUILD SUCCESS) toàn bộ 4 module")
    
    doc.add_heading("TODO 0.4: Bootstrap api-gateway với Gateway WebMVC & Resource Server", level=3)
    p = doc.add_paragraph()
    p.add_run("Cấu hình ")
    p.add_run("api-gateway/pom.xml").bold = True
    p.add_run(" với thư viện Spring Cloud Starter Gateway Server MVC và Spring Boot Starter OAuth2 Resource Server để làm cổng kiểm soát an ninh mạng.")
    add_commit_box(doc, "TODO 0.4", "build(gateway): bootstrap api-gateway with gateway webmvc and resource server", "feature/f0-infrastructure")
    add_screenshot(doc, "f0_todo04_gateway_bootstrap.png", "Các dependency bảo mật và gateway trong pom.xml của api-gateway")
    
    doc.add_heading("TODO 0.5: Cấu hình Datasource và tham số kết nối các service", level=3)
    p = doc.add_paragraph()
    p.add_run("Thiết lập tệp cấu hình ")
    p.add_run("application.properties").bold = True
    p.add_run(" cho từng dịch vụ: cổng lắng nghe, chuỗi kết nối JDBC/MongoDB URI, tài khoản Admin và JWT Secret dùng chung.")
    add_commit_box(doc, "TODO 0.5", "chore(customer): configure sql server datasource and jpa settings\nchore(movie): configure mongodb connection uri and auto index creation\nchore(booking): configure port, datasource and movie service url", "feature/f0-infrastructure")
    add_screenshot(doc, "f0_todo05_service_config.png", "Nội dung cấu hình datasource và port của 4 microservice")
    
    doc.add_heading("TODO 0.6: Xử lý ngoại lệ tập trung GlobalExceptionHandler (RFC 7807)", level=3)
    p = doc.add_paragraph()
    p.add_run("Hiện thực lớp xử lý lỗi dùng chung ")
    p.add_run("GlobalExceptionHandler").bold = True
    p.add_run(" với cấu trúc phản hồi chuẩn hóa bao gồm: ")
    p.add_run("timestamp, status, error, message, path").bold = True
    p.add_run(", giúp Client xử lý lỗi nhất quán.")
    add_commit_box(doc, "TODO 0.6", "feat(customer): add global exception handler with unified error body\nfeat(movie): add global exception handler with unified error body\nfeat(booking): add global exception handler with unified error body", "feature/f0-infrastructure")
    add_screenshot(doc, "f0_todo06_global_exception.png", "Phản hồi lỗi 404 Not Found theo định dạng chuẩn RFC 7807")
    
    # ---------- F1 ----------
    doc.add_page_break()
    doc.add_heading("F1 – Xác thực & Bảo mật (Authentication)", level=2)
    
    doc.add_heading("TODO 1.1: Cấu hình tài khoản Admin & JWT Properties", level=3)
    p = doc.add_paragraph()
    p.add_run("Cấu hình tài khoản quản trị viên cố định ")
    p.add_run("admin@fucinema.com").bold = True
    p.add_run(" / ")
    p.add_run("@@abc123@@").bold = True
    p.add_run(" trong cấu hình (không lưu DB theo yêu cầu đề bài) và chuỗi secret key HS256 đồng bộ.")
    add_commit_box(doc, "TODO 1.1", "chore(customer): configure admin account and jwt properties", "feature/f1-authentication")
    add_screenshot(doc, "f1_todo11_admin_jwt_config.png", "Cấu hình tài khoản Admin và JWT Secret key trong customer-service")
    
    doc.add_heading("TODO 1.2: Cấu hình BCryptPasswordEncoder Bean", level=3)
    p = doc.add_paragraph()
    p.add_run("Khai báo Bean ")
    p.add_run("PasswordEncoder").bold = True
    p.add_run(" sử dụng thuật toán băm một chiều BCrypt với độ muối (salt) ngẫu nhiên, đảm bảo an toàn tuyệt đối cho mật khẩu người dùng.")
    add_commit_box(doc, "TODO 1.2", "feat(customer): add bcrypt password encoder bean", "feature/f1-authentication")
    add_screenshot(doc, "f1_todo12_bcrypt_encoder.png", "Định nghĩa PasswordEncoder bean trong PasswordConfig.java")
    
    doc.add_heading("TODO 1.3: Dịch vụ JwtService ký token HS256", level=3)
    p = doc.add_paragraph()
    p.add_run("Hiện thực ")
    p.add_run("JwtService").bold = True
    p.add_run(" sử dụng Nimbus Jose JWT để ký phát access token HS256 với các claim cần thiết: ")
    p.add_run("sub (email), userId, role (ADMIN / CUSTOMER)").bold = True
    p.add_run(" và thời hạn sống 24 giờ.")
    add_commit_box(doc, "TODO 1.3", "feat(customer): add JwtService to sign HS256 access tokens", "feature/f1-authentication")
    add_screenshot(doc, "f1_todo13_jwt_service.png", "Triển khai hàm generateToken trong JwtService.java")
    
    doc.add_heading("TODO 1.4 & 1.5: Đăng nhập Admin, Khách hàng & Kiểm tra tài khoản vô hiệu", level=3)
    p = doc.add_paragraph()
    p.add_run("Hiện thực API ")
    p.add_run("POST /api/auth/login").bold = True
    p.add_run(". Kiểm tra đăng nhập Admin in-memory (role ADMIN), kiểm tra đăng nhập khách hàng trong cơ sở dữ liệu qua BCrypt (role CUSTOMER), và chặn đăng nhập nếu tài khoản có trạng thái ")
    p.add_run("INACTIVE").bold = True
    p.add_run(" (trả về HTTP 403 Forbidden).")
    add_commit_box(doc, "TODO 1.4 - 1.5", "feat(customer): implement login for admin and customers\nfeat(customer): expose POST /api/auth/login", "feature/f1-authentication")
    add_screenshot(doc, "f1_todo14_login_admin.png", "1.1 Đăng nhập Admin thành công nhận Access Token và role ADMIN")
    add_screenshot(doc, "f1_todo15_login_customer.png", "1.2 Đăng nhập Khách hàng thành công nhận Access Token và role CUSTOMER")
    add_screenshot(doc, "f1_todo15_login_inactive.png", "1.4 Chặn đăng nhập với tài khoản INACTIVE (HTTP 403 Forbidden)")
    
    # ---------- F2 ----------
    doc.add_page_break()
    doc.add_heading("F2 – Hồ sơ khách hàng (Customer Register & Profile)", level=2)
    
    doc.add_heading("TODO 2.1: Flyway Migration & Hỗ trợ tiếng Việt Unicode NVARCHAR", level=3)
    p = doc.add_paragraph()
    p.add_run("Viết script T-SQL ")
    p.add_run("V1__init.sql").bold = True
    p.add_run(" và ")
    p.add_run("V2__seed.sql").bold = True
    p.add_run(" sử dụng kiểu dữ liệu ")
    p.add_run("NVARCHAR(100)").bold = True
    p.add_run(" và tiền tố ")
    p.add_run("N'...'").bold = True
    p.add_run(" để lưu trữ tiếng Việt có dấu hoàn chỉnh trên Microsoft SQL Server.")
    add_commit_box(doc, "TODO 2.1", "feat(customer): add t-sql migrations with nvarchar and unicode seed data", "feature/f2-customer-profile")
    add_screenshot(doc, "f2_todo21_flyway_migrations.png", "Bảng customer trong SQL Server hiển thị chính xác tiếng Việt có dấu")
    
    doc.add_heading("TODO 2.2 & 2.3: Entity, Repository & DTO kèm Validation", level=3)
    p = doc.add_paragraph()
    p.add_run("Tạo entity ")
    p.add_run("Customer").bold = True
    p.add_run(" với annotation ")
    p.add_run("@Nationalized").bold = True
    p.add_run(" và các DTO ")
    p.add_run("RegisterRequest, ProfileUpdateRequest, ChangePasswordRequest").bold = True
    p.add_run(" với các ràng buộc kiểm tra hợp lệ (@NotBlank, @Email, @Pattern cho số điện thoại 10 số, @Past cho ngày sinh).")
    add_commit_box(doc, "TODO 2.2 - 2.3", "feat(customer): add Customer entity and repository\nfeat(customer): add register, profile and password DTOs with validation", "feature/f2-customer-profile")
    add_screenshot(doc, "f2_todo22_customer_model.png", "Mã nguồn Customer entity với các ràng buộc bảo vệ dữ liệu")
    
    doc.add_heading("TODO 2.4 - 2.6: Đăng ký khách hàng, Xem/Cập nhật hồ sơ & Đổi mật khẩu", level=3)
    p = doc.add_paragraph()
    p.add_run("Hiện thực quy tắc nghiệp vụ ")
    p.add_run("BR01").bold = True
    p.add_run(": email đăng ký phải là duy nhất và không được trùng với email Admin. Phản hồi đăng ký tuyệt đối không để lộ trường password. Hỗ trợ cập nhật thông tin cá nhân và đổi mật khẩu an toàn.")
    add_commit_box(doc, "TODO 2.4 - 2.6", "feat(customer): implement customer registration with unique email\nfeat(customer): implement view, update profile and change password\nfeat(customer): expose register and /me endpoints", "feature/f2-customer-profile")
    add_screenshot(doc, "f2_todo24_customer_register.png", "2.1 Đăng ký khách hàng mới thành công (HTTP 201 Created)")
    add_screenshot(doc, "f2_todo25_customer_profile.png", "2.6 Cập nhật thông tin cá nhân hỗ trợ Unicode tiếng Việt đầy đủ")
    add_screenshot(doc, "f2_todo26_customer_password.png", "2.9 Đổi mật khẩu thành công xác thực bằng mật khẩu cũ (HTTP 204)")
    
    # ---------- F3 ----------
    doc.add_page_break()
    doc.add_heading("F3 – Quản trị viên quản lý khách hàng (Admin Customers)", level=2)
    
    doc.add_heading("TODO 3.1 - 3.3: Tìm kiếm theo từ khóa & Xóa mềm (Soft Delete)", level=3)
    p = doc.add_paragraph()
    p.add_run("Quản trị viên có toàn quyền tìm kiếm khách hàng theo từ khóa tên hoặc email (không phân biệt hoa thường và hỗ trợ tiếng Việt). Khi xóa khách hàng, áp dụng cơ chế ")
    p.add_run("Xóa mềm (Soft Delete)").bold = True
    p.add_run(": chuyển ")
    p.add_run("customer_status = 'INACTIVE'").bold = True
    p.add_run(" chứ không xóa vật lý khỏi bảng nhằm đảm bảo toàn vẹn dữ liệu tham chiếu lịch sử đơn hàng từ booking-service.")
    add_commit_box(doc, "TODO 3.1 - 3.3", "feat(customer): add AdminCustomerRequest DTO\nfeat(customer): implement admin customer search and crud with soft delete\nfeat(customer): expose admin customer crud endpoints", "feature/f3-admin-customers")
    add_screenshot(doc, "f3_todo32_admin_search_keyword.png", "2.13 Quản trị viên tìm kiếm khách hàng theo từ khóa tiếng Việt (Bình)")
    add_screenshot(doc, "f3_todo33_admin_crud_soft_delete.png", "2.19 Xác thực trạng thái INACTIVE sau khi thực hiện xóa mềm khách hàng")
    
    # ---------- F4 ----------
    doc.add_page_break()
    doc.add_heading("F4 – Quản lý Thể loại & Phòng chiếu (Genre & Cinema Room)", level=2)
    
    doc.add_heading("TODO 4.1 & 4.2: DataSeeder tự động nạp dữ liệu mẫu vào MongoDB", level=3)
    p = doc.add_paragraph()
    p.add_run("Hiện thực ")
    p.add_run("DataSeeder").bold = True
    p.add_run(" thông qua CommandLineRunner để tự động nạp 5 thể loại phim, 4 phòng chiếu, 4 bộ phim và 5 suất chiếu với ObjectId cố định nếu CSDL MongoDB chưa có dữ liệu.")
    add_commit_box(doc, "TODO 4.1 - 4.2", "feat(movie): add DataSeeder for genres, rooms, movies and showtimes\nfeat(movie): add Genre and CinemaRoom documents with unique indexes", "feature/f4-genre-room")
    add_screenshot(doc, "f4_todo41_dataseeder.png", "Log khởi tạo và nạp dữ liệu mẫu ban đầu vào MongoDB")
    
    doc.add_heading("TODO 4.3 & 4.4: Ràng buộc xóa phòng chiếu / thể loại (BR03 Delete Guard)", level=3)
    p = doc.add_paragraph()
    p.add_run("Áp dụng quy tắc ")
    p.add_run("BR03").bold = True
    p.add_run(": không cho phép xóa thể loại đang có phim tham chiếu, và không cho phép xóa phòng chiếu đang có suất chiếu được xếp lịch. Trả về ")
    p.add_run("409 Conflict").bold = True
    p.add_run(". Khi tạo phòng chiếu, hệ thống tự động tính toán tổng số ghế (totalSeats = seatRows * seatsPerRow).")
    add_commit_box(doc, "TODO 4.3 - 4.4", "feat(movie): implement genre and room services with delete guards\nfeat(movie): expose genre and room endpoints", "feature/f4-genre-room")
    add_screenshot(doc, "f4_todo43_delete_guard.png", "3.6 Chặn xóa thể loại đang có phim tham chiếu theo quy tắc BR03 (HTTP 409)")
    add_screenshot(doc, "f4_todo44_genre_room_endpoints.png", "3.9 Tạo phòng chiếu mới và tự động tính tổng số ghế (5x6 = 30 ghế)")
    
    # ---------- F5 ----------
    doc.add_page_break()
    doc.add_heading("F5 – Quản lý Phim & Tìm kiếm động (Movie Management)", level=2)
    
    doc.add_heading("TODO 5.1 & 5.2: Tìm kiếm phim động bằng MongoTemplate Criteria", level=3)
    p = doc.add_paragraph()
    p.add_run("Xây dựng truy vấn động bằng ")
    p.add_run("MongoTemplate").bold = True
    p.add_run(" kết hợp ")
    p.add_run("Criteria API").bold = True
    p.add_run(". Cho phép lọc kết hợp linh hoạt theo từ khóa tiêu đề (case-insensitive regex), mã thể loại (genreId) và trạng thái phát hành (movieStatus: NOW_SHOWING, COMING_SOON, ENDED). Tự động nạp tên thể loại tương ứng vào response.")
    add_commit_box(doc, "TODO 5.1 - 5.2", "feat(movie): add Movie document referencing genre id\nfeat(movie): search movies with MongoTemplate criteria", "feature/f5-movies")
    add_screenshot(doc, "f5_todo52_movie_search_criteria.png", "4.2 Tìm kiếm phim theo từ khóa 'galaxy' với Criteria API linh hoạt")
    
    doc.add_heading("TODO 5.3 & 5.4: Kiểm tra hợp lệ thể loại khi tạo phim (BR15)", level=3)
    p = doc.add_paragraph()
    p.add_run("Áp dụng quy tắc ")
    p.add_run("BR15").bold = True
    p.add_run(": khi tạo hoặc cập nhật phim, mã genreId bắt buộc phải tồn tại trong bộ sưu tập thể loại. Nếu không tìm thấy, ném ra ngoại lệ và trả về HTTP 404 Not Found.")
    add_commit_box(doc, "TODO 5.3 - 5.4", "feat(movie): implement movie crud with genre existence check\nfeat(movie): expose movie endpoints", "feature/f5-movies")
    add_screenshot(doc, "f5_todo53_movie_crud_genre_check.png", "4.8 Chặn tạo phim với thể loại không tồn tại theo quy tắc BR15 (HTTP 404)")
    
    # ---------- F6 ----------
    doc.add_page_break()
    doc.add_heading("F6 – Quản lý Suất chiếu & Trùng lịch (Showtime Management)", level=2)
    
    doc.add_heading("TODO 6.1 - 6.3: Tự động tính EndTime & Lưu trữ giá vé Decimal128", level=3)
    p = doc.add_paragraph()
    p.add_run("Document ")
    p.add_run("Showtime").bold = True
    p.add_run(" lưu trữ giá vé bằng kiểu dữ liệu tiền tệ chính xác cao ")
    p.add_run("Decimal128").bold = True
    p.add_run(". Khi xếp lịch chiếu mới, hệ thống tự động truy vấn thời lượng của bộ phim (durationMinutes) và cộng vào startTime để sinh ra ")
    p.add_run("endTime").bold = True
    p.add_run(" chính xác.")
    add_commit_box(doc, "TODO 6.1 - 6.3", "feat(movie): add Showtime document with decimal128 price\nfeat(movie): validate and schedule showtimes with computed end time", "feature/f6-showtimes")
    add_screenshot(doc, "f6_todo63_schedule_showtime.png", "5.4 Tạo suất chiếu và tự động tính endTime (14:00 + 125 phút = 16:05)")
    
    doc.add_heading("TODO 6.4 & 6.5: Phát hiện trùng lịch phòng chiếu (BR05 Overlap Detection)", level=3)
    p = doc.add_paragraph()
    p.add_run("Hiện thực truy vấn dẫn xuất trong ")
    p.add_run("ShowtimeRepository").bold = True
    p.add_run(" để phát hiện sự giao nhau giữa hai khoảng thời gian ")
    p.add_run("[s1, e1)").bold = True
    p.add_run(" và ")
    p.add_run("[s2, e2)").bold = True
    p.add_run(" theo điều kiện toán học: ")
    p.add_run("startTime < e2 AND endTime > s2").bold = True
    p.add_run(". Ngăn chặn hoàn toàn việc xếp trùng lịch trong cùng một phòng chiếu theo quy tắc ")
    p.add_run("BR05").bold = True
    p.add_run(" (trả về 409 Conflict).")
    add_commit_box(doc, "TODO 6.4 - 6.5", "feat(movie): add derived query counting overlapping showtimes\nfeat(movie): implement showtime cancel and search by movie and date\nfeat(movie): expose showtime endpoints", "feature/f6-showtimes")
    add_screenshot(doc, "f6_todo64_overlap_conflict.png", "5.5 Ngăn chặn xung đột trùng lịch phòng chiếu theo quy tắc BR05 (HTTP 409)")
    
    # ---------- F7 ----------
    doc.add_page_break()
    doc.add_heading("F7 – Đặt vé xem phim & Sơ đồ ghế (Create Booking & Seat Map)", level=2)
    
    doc.add_heading("TODO 7.1 - 7.4: Tích hợp Spring Cloud OpenFeign gọi liên dịch vụ", level=3)
    p = doc.add_paragraph()
    p.add_run("Cấu hình ")
    p.add_run("@EnableFeignClients").bold = True
    p.add_run(" trong booking-service và định nghĩa interface ")
    p.add_run("MovieClient").bold = True
    p.add_run(" để gọi trực tiếp các API của movie-service (lấy thông tin suất chiếu, phòng chiếu, phim) theo mã định danh chuỗi String mà không cần thông qua Gateway, giúp tối ưu hóa hiệu năng giao tiếp mạng nội bộ.")
    add_commit_box(doc, "TODO 7.1 - 7.4", "build(booking): add openfeign and spring cloud bom\nfeat(booking): add mysql migration with varchar object id columns\nfeat(booking): add Booking and BookingDetail entities\nfeat(booking): add MovieClient feign client with string showtime id", "feature/f7-create-booking")
    
    doc.add_heading("TODO 7.5 - 7.7: Sinh sơ đồ ghế và Kiểm tra chống trùng ghế (BR07-BR10)", level=3)
    p = doc.add_paragraph()
    p.add_run("API sinh sơ đồ ghế ")
    p.add_run("GET /api/bookings/showtimes/{id}/seats").bold = True
    p.add_run(" tự động tính toán lưới tọa độ ghế (A1, A2... H10) kết hợp với các vé đã bán trong MySQL để đánh dấu trạng thái ")
    p.add_run("TAKEN").bold = True
    p.add_run(" hoặc ")
    p.add_run("AVAILABLE").bold = True
    p.add_run(" theo thời gian thực. Quy trình tạo đơn vé kiểm tra nghiêm ngặt: số vé không quá 8 (BR07), ghế phải thuộc phòng (BR08), ghế chưa bị ai đặt trước (BR09 - Double Booking Prevention), và lưu trữ bản chụp dữ liệu (snapshot) để đảm bảo toàn vẹn khi giá vé thay đổi (BR14).")
    add_commit_box(doc, "TODO 7.5 - 7.7", "feat(booking): implement booking creation with seat validation\nfeat(booking): add seat map for a showtime\nfeat(booking): expose create booking and seat map endpoints", "feature/f7-create-booking")
    add_screenshot(doc, "f7_todo76_seat_map.png", "6.1 Sơ đồ ghế ngồi thời gian thực 80 ghế kèm trạng thái ghế đã đặt")
    add_screenshot(doc, "f7_todo77_create_booking.png", "6.2 Đặt 2 vé thành công và lưu bản chụp thông tin phim, phòng, giá (HTTP 201)")
    add_screenshot(doc, "f7_todo75_seat_validation.png", "6.3 Ngăn chặn đặt lại ghế E5 đã có người mua theo quy tắc BR09 (HTTP 409)")
    
    # ---------- F8 ----------
    doc.add_page_break()
    doc.add_heading("F8 – Lịch sử & Hủy vé xem phim (History & Cancellation)", level=2)
    
    doc.add_heading("TODO 8.1 - 8.4: Kiểm soát truy cập dữ liệu (BR11) & Chính sách hủy vé (BR12)", level=3)
    p = doc.add_paragraph()
    p.add_run("Khách hàng có thể tra cứu lịch sử đặt vé cá nhân sắp xếp giảm dần theo ngày. Áp dụng quy tắc ")
    p.add_run("BR11").bold = True
    p.add_run(": khách hàng chỉ được phép xem chi tiết đơn hàng của chính mình (kiểm tra customerId từ JWT header so với đơn hàng, khách hàng khác cố tình truy cập sẽ nhận HTTP 403 Forbidden). Áp dụng quy tắc ")
    p.add_run("BR12").bold = True
    p.add_run(": chỉ cho phép hủy vé khi suất chiếu chưa bắt đầu và còn cách giờ chiếu tối thiểu 2 tiếng; khi hủy thành công, trạng thái chuyển sang ")
    p.add_run("CANCELLED").bold = True
    p.add_run(" và toàn bộ ghế liên quan được giải phóng ngay lập tức trên sơ đồ ghế.")
    add_commit_box(doc, "TODO 8.1 - 8.4", "feat(booking): add customer booking history sorted by date\nfeat(booking): restrict booking detail to owner or admin\nfeat(booking): allow cancelling bookings 2 hours before showtime\nfeat(booking): expose history, detail, cancel and admin list endpoints", "feature/f8-history-cancel")
    add_screenshot(doc, "f8_todo81_booking_history.png", "7.1 Tra cứu lịch sử đơn hàng cá nhân của khách hàng")
    add_screenshot(doc, "f8_todo82_booking_detail_rbac.png", "7.3 Chặn truy cập xem đơn hàng của người khác theo quy tắc BR11 (HTTP 403)")
    add_screenshot(doc, "f8_todo83_booking_cancel.png", "7.7 Hủy đơn hàng trước giờ chiếu >= 2 tiếng theo quy tắc BR12 (HTTP 200)")
    
    # ---------- F9 ----------
    doc.add_page_break()
    doc.add_heading("F9 – Thống kê & Báo cáo doanh thu (Revenue Report)", level=2)
    
    doc.add_heading("TODO 9.1 - 9.3: Báo cáo doanh thu tổng hợp & Phân nhóm theo phim (BR13)", level=3)
    p = doc.add_paragraph()
    p.add_run("Cung cấp API cho Admin ")
    p.add_run("GET /api/bookings/report?startDate=...&endDate=...").bold = True
    p.add_run(" để thống kê doanh thu trong khoảng thời gian xác định. Hệ thống tự động loại trừ các đơn hàng đã bị hủy (CANCELLED), tính tổng doanh thu, tổng số vé, và nhóm doanh số theo từng bộ phim rồi sắp xếp giảm dần theo doanh thu theo quy tắc ")
    p.add_run("BR13").bold = True
    p.add_run(". Kiểm tra ràng buộc startDate <= endDate.")
    add_commit_box(doc, "TODO 9.1 - 9.3", "feat(booking): add report query by booking date range\nfeat(booking): implement revenue report sorted descending\nfeat(booking): expose GET /api/bookings/report", "feature/f9-report")
    add_screenshot(doc, "f9_todo93_report_endpoint.png", "8.1 Báo cáo doanh thu Admin phân nhóm theo phim và sắp xếp giảm dần")
    
    # ---------- F10 ----------
    doc.add_page_break()
    doc.add_heading("F10 – API Gateway & Phân quyền bảo mật (Gateway Security)", level=2)
    
    doc.add_heading("TODO 10.1 - 10.4: Định tuyến WebMVC, Chuyển tiếp Header & Phân quyền RBAC", level=3)
    p = doc.add_paragraph()
    p.add_run("Spring Cloud API Gateway đóng vai trò tường lửa và định tuyến tập trung. Lớp ")
    p.add_run("UserHeaderFilter").bold = True
    p.add_run(" chủ động bóc tách các Header giả mạo gửi từ phía Client, sau đó lấy thông tin định danh chính thống từ JWT đã được ký hợp lệ và bơm vào Header gửi đến các microservice phía sau. Cấu hình ")
    p.add_run("SecurityConfig").bold = True
    p.add_run(" phân quyền chuẩn xác theo vai trò (ADMIN, CUSTOMER, PUBLIC) dựa trên HTTP Method và đường dẫn URL.")
    add_commit_box(doc, "TODO 10.1 - 10.4", "chore(gateway): configure service urls and jwt secret\nfeat(gateway): forward user context headers from jwt\nfeat(gateway): add routes for customer, movie and booking services\nfeat(gateway): secure endpoints with jwt and role-based rules", "feature/f10-gateway")
    add_screenshot(doc, "f10_todo102_user_header_filter.png", "Mã nguồn UserHeaderFilter chống giả mạo và chuyển tiếp ngữ cảnh an toàn")
    add_screenshot(doc, "f10_todo104_security_config.png", "Cấu hình phân quyền chi tiết RBAC trong SecurityConfig.java")
    
    # ---------- F11 ----------
    doc.add_page_break()
    doc.add_heading("F11 – Kiểm thử tích hợp tự động với Postman & Newman", level=2)
    
    doc.add_heading("TODO 11.1 - 11.3: Bộ kiểm thử tích hợp 8 thư mục, 83 requests và 120 assertions", level=3)
    p = doc.add_paragraph()
    p.add_run("Xây dựng bộ kiểm thử tích hợp toàn diện gồm Environment ")
    p.add_run("FUCinema-Local.postman_environment.json").bold = True
    p.add_run(" và Collection ")
    p.add_run("FUCinema-Booking-System.postman_collection.json").bold = True
    p.add_run(" bao phủ toàn bộ 8 nhóm chức năng (từ 01-Auth đến 08-Report). Thực thi kiểm thử tự động bằng công cụ Newman CLI, đạt tỷ lệ thành công tuyệt đối 100% với ")
    p.add_run("120/120 assertions đạt chuẩn (zero failures)").bold = True
    p.add_run(".")
    add_commit_box(doc, "TODO 11.1 - 11.3", "test(postman): add local environment\ntest(postman): add collection with test scripts for F1-F10\ndocs: add run guide and test accounts to README\ndocs: add collection runner result screenshot", "feature/f11-postman")
    add_screenshot(doc, "f11_todo113_newman_terminal_summary.png", "Kết quả thực thi Newman CLI: 83 requests, 120/120 assertions passed, 0 failures")
    
    # ==================== PHẦN 3 ====================
    doc.add_page_break()
    doc.add_heading("PHẦN 3: BẢNG TỔNG HỢP KIỂM THỬ & TIÊU CHÍ NGHIỆM THU", level=1)
    
    doc.add_heading("3.1 Kết quả kiểm thử tự động từng thư mục qua Newman CLI", level=2)
    
    tbl_newman = doc.add_table(rows=10, cols=5)
    tbl_newman.alignment = WD_TABLE_ALIGNMENT.CENTER
    newman_summary = [
        ("Mã Thư Mục", "Tên Thư Mục Kiểm Thử", "Số Lượng Requests", "Số Lượng Assertions", "Trạng Thái"),
        ("01-Auth", "Xác thực & Quản lý phiên", "7", "11", "100% PASS (0 Fail)"),
        ("02-Customer", "Đăng ký & Quản lý khách hàng", "19", "25", "100% PASS (0 Fail)"),
        ("03-Genre-Room", "Quản lý Thể loại & Phòng chiếu", "12", "16", "100% PASS (0 Fail)"),
        ("04-Movie", "Quản lý & Tìm kiếm phim", "12", "16", "100% PASS (0 Fail)"),
        ("05-Showtime", "Quản lý Suất chiếu & Trùng lịch", "12", "16", "100% PASS (0 Fail)"),
        ("06-Booking", "Tạo đơn đặt vé & Sơ đồ ghế", "9", "15", "100% PASS (0 Fail)"),
        ("07-History-Cancel", "Lịch sử & Hủy đơn hàng", "9", "15", "100% PASS (0 Fail)"),
        ("08-Report", "Báo cáo doanh thu & Thống kê", "3", "6", "100% PASS (0 Fail)"),
        ("TỔNG CỘNG", "TOÀN BỘ HỆ THỐNG", "83 Requests", "120 Assertions", "100% PASS (ZERO FAIL)")
    ]
    for r_idx, row in enumerate(newman_summary):
        for c_idx, val in enumerate(row):
            cell = tbl_newman.cell(r_idx, c_idx)
            set_cell_margins(cell, 80, 80, 100, 100)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Segoe UI"
            r.font.size = Pt(9.5)
            if r_idx == 0:
                r.bold = True
                set_cell_background(cell, "0284C7")
                r.font.color.rgb = RGBColor(255, 255, 255)
            elif r_idx == 9:
                r.bold = True
                set_cell_background(cell, "DCFCE7") # Light Green
                r.font.color.rgb = RGBColor(22, 101, 52)
            else:
                set_cell_background(cell, "F8FAFC" if r_idx % 2 == 1 else "FFFFFF")
                if c_idx == 4:
                    r.font.color.rgb = RGBColor(22, 101, 52)
                    r.bold = True
                    
    doc.add_paragraph().paragraph_format.space_after = Pt(12)
    
    doc.add_heading("3.2 Bảng đối chiếu 15 Quy tắc nghiệp vụ (Business Rules BR01 - BR15)", level=2)
    
    tbl_br = doc.add_table(rows=16, cols=4)
    tbl_br.alignment = WD_TABLE_ALIGNMENT.CENTER
    br_data = [
        ("Mã Quy Tắc", "Mô Tả Quy Tắc Nghiệp Vụ", "Vị Trí Hiện Thực / Microservice", "Kết Quả Nghiệm Thu"),
        ("BR01", "Email khách hàng là duy nhất và không trùng email Admin", "customer-service (CustomerService)", "ĐẠT (409 Conflict khi trùng)"),
        ("BR02", "Tên thể loại và tên phòng chiếu là duy nhất", "movie-service (GenreService, RoomService)", "ĐẠT (409 Conflict khi trùng)"),
        ("BR03", "Không thể xóa thể loại có phim hoặc phòng chiếu có suất chiếu", "movie-service (Delete Guards)", "ĐẠT (409 Conflict khi còn liên kết)"),
        ("BR04", "Suất chiếu phải ở tương lai, phim chưa kết thúc, phòng hoạt động", "movie-service (ShowtimeService)", "ĐẠT (400 Bad Request nếu vi phạm)"),
        ("BR05", "Không được xếp trùng lịch suất chiếu trong cùng một phòng", "movie-service (Derived Query Overlap)", "ĐẠT (409 Conflict khi giao nhau)"),
        ("BR06", "Hủy suất chiếu áp dụng xóa mềm (soft delete CANCELLED)", "movie-service (Showtime.showtimeStatus)", "ĐẠT (204 No Content, giữ dữ liệu)"),
        ("BR07", "Mỗi lần đặt tối đa 8 vé, không trùng ghế trong cùng một yêu cầu", "booking-service (BookingService)", "ĐẠT (400 Bad Request nếu >8 vé)"),
        ("BR08", "Ghế phải thuộc cấu hình phòng chiếu, suất chiếu chưa bị hủy", "booking-service (Seat Validation)", "ĐẠT (400 Bad Request nếu sai ghế)"),
        ("BR09", "Không được đặt ghế đã có người mua (Double Booking Guard)", "booking-service (Seat Status Check)", "ĐẠT (409 Conflict nếu ghế đã bán)"),
        ("BR10", "Giá vé tính ở phía máy chủ, không nhận giá từ phía Client", "booking-service (Snapshot Price)", "ĐẠT (Tính đúng theo giá suất chiếu)"),
        ("BR11", "Khách hàng chỉ xem được đơn hàng của mình; Admin xem tất cả", "booking-service (RBAC Data Check)", "ĐẠT (403 Forbidden nếu xem trộm)"),
        ("BR12", "Chỉ hủy được vé trước giờ chiếu >= 2 tiếng; hủy xong nhả ghế", "booking-service (Cancel Logic)", "ĐẠT (Hủy vé và nhả ghế tức thì)"),
        ("BR13", "Báo cáo doanh thu loại bỏ đơn hủy, sắp xếp phim giảm dần", "booking-service (Revenue Aggregator)", "ĐẠT (Thống kê chính xác tuyệt đối)"),
        ("BR14", "Lưu bản chụp thông tin phim, phòng, suất chiếu vào đơn hàng", "booking-service (BookingDetail Snapshot)", "ĐẠT (Bảo toàn dữ liệu lịch sử)"),
        ("BR15", "Khóa ngoại giữa các CSDL NoSQL/SQL phải kiểm tra tồn tại", "movie-service, booking-service", "ĐẠT (404 Not Found nếu sai ID)")
    ]
    for r_idx, row in enumerate(br_data):
        for c_idx, val in enumerate(row):
            cell = tbl_br.cell(r_idx, c_idx)
            set_cell_margins(cell, 60, 60, 80, 80)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Segoe UI"
            r.font.size = Pt(9)
            if r_idx == 0:
                r.bold = True
                set_cell_background(cell, "0284C7")
                r.font.color.rgb = RGBColor(255, 255, 255)
            else:
                set_cell_background(cell, "F8FAFC" if r_idx % 2 == 1 else "FFFFFF")
                if c_idx == 3:
                    r.font.color.rgb = RGBColor(22, 101, 52)
                    r.bold = True

    doc.add_paragraph().paragraph_format.space_after = Pt(12)
    doc.add_heading("3.3 Kết luận & Đánh giá mức độ hoàn thành bài tập lớn", level=2)
    p = doc.add_paragraph()
    p.add_run("Dự án ")
    p.add_run("Assignment 1 - Hệ Thống Đặt Vé Xem Phim FUCinema").bold = True
    p.add_run(" đã được hoàn thành trọn vẹn 100% các tiêu chí khắt khe nhất của học phần MSS301:")
    
    final_points = [
        "Hiện thực đầy đủ 4 microservices bằng Java 21, Spring Boot 4.1.0 và Spring Cloud.",
        "Thiết lập thành công kiến trúc Polyglot Persistence vận hành mượt mà trên 3 DBMS: SQL Server 2022, MongoDB 7.0.5 và MySQL 8.3.0.",
        "Xây dựng API Gateway với cơ chế bảo mật OAuth2 Resource Server JWT HS256 và UserHeaderFilter chống giả mạo định danh.",
        "Toàn bộ 15 quy tắc nghiệp vụ cốt lõi (BR01 đến BR15) được triển khai và kiểm chứng chính xác tuyệt đối.",
        "Bộ kiểm thử tự động Postman/Newman gồm 83 API requests và 120 assertions đạt tỉ lệ vượt qua 100% không phát sinh lỗi.",
        "Lịch sử mã nguồn được tổ chức chuyên nghiệp, tuân thủ nghiêm ngặt quy ước Conventional Commits với các nhánh tính năng rõ ràng."
    ]
    for pt in final_points:
        bp = doc.add_paragraph(style='List Paragraph')
        r_bullet = bp.add_run("• ")
        r_bullet.bold = True
        bp.add_run(pt).font.name = "Segoe UI"
        
    doc.save(OUTPUT_PATH)
    # Also overwrite Assignment 1_template.docx as requested by user
    doc.save(TEMPLATE_PATH)
    print("Report generated and saved to:")
    print("1.", OUTPUT_PATH)
    print("2.", TEMPLATE_PATH)

if __name__ == "__main__":
    build_full_report()
