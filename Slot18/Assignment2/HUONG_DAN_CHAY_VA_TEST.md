# HƯỚNG DẪN CHẠY VÀ KIỂM THỬ HỆ THỐNG
## Watch Management Microservices (Saga Orchestration Pattern)

> **Môn học:** MSS301 – Distributed Systems & Microservices  
> **Chủ đề:** Saga Orchestration Pattern (Transactions in Microservices)  
> **Stack công nghệ:** Java 21 · Spring Boot 4.1.1 · Spring Cloud 2025.1.3 · Hibernate 7 · Jackson 3 · MS SQL Server · JWT (jjwt 0.13.0)

---

## MỤC LỤC
1. [Yêu cầu môi trường chuẩn bị](#1-yêu-cầu-môi-trường-chuẩn-bị)
2. [Cấu hình & Chuẩn bị Cơ sở dữ liệu (SQL Server)](#2-cấu-hình--chuẩn-bị-cơ-sở-dữ-liệu-sql-server)
3. [Cách 1: Chạy hệ thống trên máy cục bộ (Local / IDE)](#3-cách-1-chạy-hệ-thống-trên-máy-cục-bộ-local--ide)
4. [Cách 2: Chạy toàn bộ hệ thống bằng Docker Compose](#4-cách-2-chạy-toàn-bộ-hệ-thống-bằng-docker-compose)
5. [Kiểm tra nhanh hệ thống (Smoke Test)](#5-kiểm-tra-nhanh-hệ-thống-smoke-test)
6. [Hướng dẫn kiểm thử tự động bằng Postman Collection](#6-hướng-dẫn-kiểm-thử-tự-động-bằng-postman-collection)
7. [Hướng dẫn kiểm thử các kịch bản Saga nâng cao](#7-hướng-dẫn-kiểm-thử-các-kịch-bản-saga-nâng-cao)
8. [Câu truy vấn SQL kiểm chứng tính nhất quán dữ liệu](#8-câu-truy-vấn-sql-kiểm-chứng-tính-nhất-quán-dữ-liệu)
9. [Xử lý các lỗi thường gặp (Troubleshooting)](#9-xử-lý-các-lỗi-thường-gặp-troubleshooting)

---

## 1. Yêu cầu môi trường chuẩn bị

| Công cụ | Phiên bản tối thiểu | Ghi chú |
|---|---|---|
| **JDK** | Java 21 hoặc 24 | Đã kiểm tra tương thích hoàn toàn |
| **Maven** | 3.9+ | Dùng để build và package |
| **MS SQL Server** | 2019 hoặc 2022 | Cổng mặc định 1433, bật SQL Server Authentication |
| **Postman** | Bản mới nhất | Để chạy collection test tự động |
| **Docker Desktop** | (Tuỳ chọn) | Dành cho việc chạy container |

Kiểm tra công cụ trên máy bằng lệnh:
```bash
java -version
mvn -version
```

---

## 2. Cấu hình & Chuẩn bị Cơ sở dữ liệu (SQL Server)

Hệ thống tuân thủ nguyên tắc **Database per Service**: mỗi microservice sở hữu một DB riêng biệt.

### 2.1. Tạo 3 database và kích hoạt tài khoản `sa`
Mở SQL Server Management Studio (SSMS) hoặc chạy lệnh `sqlcmd`:

```sql
-- Kích hoạt tài khoản sa và đặt mật khẩu
ALTER LOGIN sa ENABLE;
ALTER LOGIN sa WITH PASSWORD = 'YourStrong@Password123';
GO

-- Tạo 3 database riêng cho 3 service
IF DB_ID('DBAccount') IS NULL CREATE DATABASE DBAccount;
IF DB_ID('DBBrand')   IS NULL CREATE DATABASE DBBrand;
IF DB_ID('DBWatch')   IS NULL CREATE DATABASE DBWatch;
GO
```

Hoặc chạy nhanh bằng PowerShell / Command Prompt:
```powershell
sqlcmd -S localhost,1433 -E -C -Q "ALTER LOGIN sa ENABLE; ALTER LOGIN sa WITH PASSWORD = 'YourStrong@Password123'; IF DB_ID('DBAccount') IS NULL CREATE DATABASE DBAccount; IF DB_ID('DBBrand') IS NULL CREATE DATABASE DBBrand; IF DB_ID('DBWatch') IS NULL CREATE DATABASE DBWatch;"
```

### 2.2. Quy tắc Reset dữ liệu khi muốn test lại từ đầu
> ⚠️ **LƯU Ý QUAN TRỌNG:**  
> Dữ liệu ban đầu liên kết `BrandWatches` ở `DBBrand` dựa trên `WatchID` từ 1..10 của `DBWatch`. Khi chạy test tạo mới/xoá đồng hồ, các khoá tự tăng (`IDENTITY`) sẽ tăng dần.  
> Khi muốn chạy lại Postman từ đầu để đạt kết quả chuẩn xác nhất, **hãy drop và tạo lại cả 3 database**:

```sql
USE master;
ALTER DATABASE DBAccount SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
ALTER DATABASE DBBrand   SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
ALTER DATABASE DBWatch   SET SINGLE_USER WITH ROLLBACK IMMEDIATE;

DROP DATABASE DBAccount;
DROP DATABASE DBBrand;
DROP DATABASE DBWatch;

CREATE DATABASE DBAccount;
CREATE DATABASE DBBrand;
CREATE DATABASE DBWatch;
GO
```

---

## 3. Cách 1: Chạy hệ thống trên máy cục bộ (Local / IDE)

### 3.1. Đóng gói mã nguồn (nếu chưa đóng gói)
Di chuyển vào thư mục `WatchManagement`:
```bash
cd d:\FA26\MSS301\Code\Slot18\Assignment2\WatchManagement
```
Build tất cả các service (bỏ qua test):
```bash
mvn -f MSAccount_StudentCode/pom.xml package -DskipTests
mvn -f MSBrand_StudentCode/pom.xml package -DskipTests
mvn -f MSWatch_StudentCode/pom.xml package -DskipTests
mvn -f APIGateway_StudentCode/pom.xml package -DskipTests
```

### 3.2. Thứ tự khởi động các dịch vụ
> ⚠️ **BẮT BUỘC KHỞI ĐỘNG THEO THỨ TỰ SAU:**  
> **`MSAccount (8081)` ➔ `MSBrand (8082)` ➔ `MSWatch (8083)` ➔ `APIGateway (8080)`**

Mở 4 cửa sổ Terminal riêng biệt:

* **Terminal 1 – Khởi động MSAccount (Port 8081):**
  ```bash
  cd d:\FA26\MSS301\Code\Slot18\Assignment2\WatchManagement\MSAccount_StudentCode
  java -jar target/ms-account-1.0.0.jar
  # Hoặc dùng: mvn spring-boot:run
  ```
  *Chờ thấy log: `Seeded 5 accounts` và `Started MSAccountApplication`.*

* **Terminal 2 – Khởi động MSBrand (Port 8082):**
  ```bash
  cd d:\FA26\MSS301\Code\Slot18\Assignment2\WatchManagement\MSBrand_StudentCode
  java -jar target/ms-brand-1.0.0.jar
  ```
  *Chờ thấy log: `Seeded 5 brands`, `Seeded 10 brand-watch links`.*

* **Terminal 3 – Khởi động MSWatch (Port 8083):**
  ```bash
  cd d:\FA26\MSS301\Code\Slot18\Assignment2\WatchManagement\MSWatch_StudentCode
  java -jar target/ms-watch-1.0.0.jar
  ```
  *Chờ thấy log: `Seeded 5 categories`, `Seeded 10 watches`.*

* **Terminal 4 – Khởi động APIGateway (Port 8080):**
  ```bash
  cd d:\FA26\MSS301\Code\Slot18\Assignment2\WatchManagement\APIGateway_StudentCode
  java -jar target/api-gateway-1.0.0.jar
  ```
  *Chờ thấy log: `Netty started on port 8080`.*

---

## 4. Cách 2: Chạy toàn bộ hệ thống bằng Docker Compose

Nếu máy có cài sẵn **Docker Desktop**:

1. Mở file `.env` tại thư mục gốc `WatchManagement/.env` để kiểm tra các cấu hình mật khẩu và `SAGA_FAULT_INJECTION=true`.
2. Khởi chạy toàn bộ cluster:
   ```bash
   cd d:\FA26\MSS301\Code\Slot18\Assignment2\WatchManagement
   docker compose --env-file .env up --build -d
   ```
3. Xem trạng thái các container:
   ```bash
   docker compose ps
   ```
   *Kết quả mong đợi: `sqlserver` ở trạng thái **healthy**, `db-init` báo **exited (0)**, và 4 microservices đều **running**.*
4. Xem log của orchestrator:
   ```bash
   docker compose logs -f ms-watch
   ```
5. Khi muốn dừng và reset sạch toàn bộ volume database:
   ```bash
   docker compose down -v
   ```

---

## 5. Kiểm tra nhanh hệ thống (Smoke Test)

Trước khi chạy full test, hãy kiểm tra một số endpoint cơ bản:

1. **Xem danh sách đồng hồ qua Gateway (Public - không cần token):**
   * URL: `GET http://localhost:8080/api/watches`
   * Kết quả: Trả về HTTP 200, danh sách 10 đồng hồ, mỗi đồng hồ có `categoryName` và sắp xếp mới nhất ở đầu.
2. **Xem danh sách đồng hồ của Brand 1 (Rolex) trực tiếp tại MSBrand:**
   * URL: `GET http://localhost:8082/api/brands/1/watches`
   * Kết quả: Trả về HTTP 200, `watchCount: 2`, `watchIds: [1, 8]`.
3. **Kiểm tra Swagger UI tài liệu API:**
   * MSAccount: `http://localhost:8081/swagger-ui.html`
   * MSBrand: `http://localhost:8082/swagger-ui.html`
   * MSWatch: `http://localhost:8083/swagger-ui.html`

---

## 6. Hướng dẫn kiểm thử tự động bằng Postman Collection

File collection nằm tại:  
📂 `d:\FA26\MSS301\Code\Slot18\Assignment2\WatchManagement\WatchManagement_Saga.postman_collection.json`

### 6.1. Import vào Postman
1. Mở ứng dụng **Postman**.
2. Chọn **File** ➔ **Import** (hoặc bấm tổ hợp phím `Ctrl + O`).
3. Kéo thả file `WatchManagement_Saga.postman_collection.json` vào Postman.

### 6.2. Thiết lập biến môi trường (Environment / Collection Variables)
Collection đã được cấu hình sẵn 2 biến mặc định:
* `baseUrl`: `http://localhost:8080` (Cổng của API Gateway)
* `todayDate`: `2026-11-04` *(hoặc điền ngày hiện tại dạng YYYY-MM-DD để khớp với nghiệp vụ)*

### 6.3. Chạy tự động (Collection Runner)
1. Chuột phải vào collection **`WatchManagement_Saga`** trong thanh bên trái.
2. Chọn **Run collection**.
3. **Thứ tự thực hiện:** Đảm bảo chọn chạy từ trên xuống dưới (các request sử dụng chung biến được set động như `adminAccessToken`, `newWatchId`, `createSagaId`,...).
4. Bấm **Run WatchManagement_Saga**.

### 6.4. Ý nghĩa các Folder kiểm thử
| Folder | Chức năng kiểm chứng |
|---|---|
| **00 - Authentication** | Đăng nhập tài khoản `adminsys` (Admin), `staff02` (Staff), `member01` (Member); lưu access token và refresh token. |
| **01 - Security & Authorization** | Chứng minh: GET /api/watches là public; GET /api/brands bị 401 nếu thiếu token; Staff bị 403; tài khoản inactive (`member02`) bị 403; Gateway xoá sạch header giả mạo `X-User-Role: 1`; chặn route `/internal/**`. |
| **02 - Validation Pre-Saga** | Chứng minh: Tên ≤ 10 ký tự, giá < 100, ReleaseDate khác ngày hôm nay, category không tồn tại đều bị chặn HTTP 400 **trước khi tạo Saga** (không sinh rác trong `SagaStates`). |
| **03 - CREATE Saga Success** | Tạo đồng hồ thành công (HTTP 201), có header `X-Saga-Id`, đồng hồ mới hiển thị ở đầu danh sách, `watchCount` của Brand 1 tăng từ 2 lên 3 (chứng minh cập nhật đồng thời 2 DB). |
| **04 - CREATE Brand NotFound Compensation** | Gửi request tạo watch với `brandId: 999` ➔ MSBrand báo 404 ➔ Saga Orchestrator bắt lỗi, chuyển sang trạng thái `COMPENSATING`, gọi bù trừ `DELETE_WATCH` xoá dòng đã insert ở DBWatch ➔ kết thúc `COMPENSATED`. |
| **05 - CREATE Fault Injection Compensation** | Gửi kèm header `X-Saga-Fail-After-Step: 2` ➔ Giả lập lỗi sau khi bước 2 đã ghi vào DBBrand ➔ Orchestrator bù trừ theo thứ tự **LIFO**: gọi `UNASSIGN_BRAND` gỡ khỏi MSBrand trước, sau đó gọi `DELETE_WATCH` ở MSWatch ➔ Dữ liệu 2 DB giữ nguyên tính nhất quán. |
| **06 - UPDATE Saga** | Cập nhật chuyển brand thành công; Cập nhật với brand 999 bị bù trừ (`RESTORE_WATCH`); Cập nhật có lỗi giả lập sau bước 2 được hoàn tác bằng `ASSIGN_BRAND_BACK` và `RESTORE_WATCH`. |
| **07 - DELETE Saga** | Xoá có lỗi giả lập ở bước 1 ➔ gọi `ASSIGN_BRAND_BACK` bù trừ, watch còn nguyên; Xoá có lỗi sau bước 2 ➔ Bước 2 là **Pivot transaction** đã commit nên lỗi giả bị bỏ qua (`FAULT SKIPPED`), Saga đi tiếp tới `COMPLETED`. |
| **08 - Saga Monitoring** | Xem danh sách và chi tiết các bước trong log Saga (chỉ Admin mới có quyền truy cập, Staff bị 403). |

---

## 7. Hướng dẫn kiểm thử các kịch bản Saga nâng cao

### Kịch bản 7.1: Giả lập sự cố mất kết nối mạng (MSBrand bị tắt)
Kịch bản này chứng minh khả năng xử lý khi một service tham gia Saga bị sập:
1. Đảm bảo hệ thống đang chạy bình thường.
2. **Tắt MSBrand:** Vào Terminal của MSBrand bấm `Ctrl + C` (hoặc Stop trong IntelliJ).
3. Sử dụng Postman gửi request thêm đồng hồ (với token Admin):
   * `POST http://localhost:8080/api/watches`
   * Body:
     ```json
     {
       "name": "Network Failure Test Watch",
       "categoryId": 1,
       "brandId": 1,
       "caseMaterial": "Steel",
       "strapMaterial": "Steel",
       "waterpMaterial": "100m",
       "price": 1000.0,
       "releaseDate": "2026-11-04",
       "stock": 10
     }
     ```
4. **Kết quả mong đợi:**
   * Response trả về **HTTP 503 Service Unavailable**.
   * `reason` chứa thông tin: `MSBrand is unreachable: Connection refused...`.
   * `sagaStatus`: **`COMPENSATED`**.
   * Chi tiết bước trong `GET /api/sagas/{sagaId}`:
     * `EXECUTE CREATE_WATCH SUCCESS` (bước 1 insert DBWatch xong)
     * `EXECUTE ASSIGN_BRAND FAILED` (bước 2 gọi sang MSBrand bị timeout/lỗi kết nối)
     * `COMPENSATE DELETE_WATCH SUCCESS` (tự động xoá đồng hồ vừa tạo ở DBWatch)
5. Bật lại MSBrand sau khi test xong.

### Kịch bản 7.2: Kịch bản nâng cao – Compensation thất bại (Dừng ở trạng thái `COMPENSATING`)
Kịch bản này giải thích trạng thái "kẹt" cần xử lý thủ công (hoặc recovery job):
1. Chạy `MSWatch` ở chế độ **Debug** trong IntelliJ, đặt Breakpoint tại đầu method `compensate()` của `WatchSagaOrchestrator.java`.
2. Gửi request `POST /api/watches` với header `X-Saga-Fail-After-Step: 2`.
3. Khi luồng chạy dừng lại tại Breakpoint (lúc này bước 1 và bước 2 đều đã commit thành công):
   ➔ **Tắt MSBrand** (Stop).
4. Nhấn **Resume Program** trong IntelliJ để MSWatch tiếp tục chạy bù trừ.
5. **Kết quả mong đợi:**
   * Orchestrator cố gắng gọi `UNASSIGN_BRAND` sang MSBrand nhưng thất bại.
   * Thử lại 3 lần (Attempt 1/3, 2/3, 3/3) đều thất bại.
   * Log ghi nhận `COMPENSATION_HALTED`.
   * Saga **dừng lại ở trạng thái `COMPENSATING`** (không báo `COMPENSATED` sai sự thật).
   * Dữ liệu đồng hồ vẫn giữ nguyên ở cả 2 bên để chờ quản trị viên can thiệp xử lý.

---

## 8. Câu truy vấn SQL kiểm chứng tính nhất quán dữ liệu

Sau khi thực hiện bất kỳ kịch bản thêm/sửa/xoá (kể cả thành công hay thất bại được bù trừ), mở SSMS và chạy câu truy vấn đối chiếu chéo giữa 2 database:

```sql
SELECT 
    w.WatchID   AS WatchInDBWatch,  
    w.BrandID   AS BrandInDBWatch,
    bw.WatchID  AS WatchInDBBrand,  
    bw.BrandID  AS BrandInDBBrand
FROM DBWatch.dbo.Watches w
FULL OUTER JOIN DBBrand.dbo.BrandWatches bw 
    ON w.WatchID = bw.WatchID
WHERE w.WatchID IS NULL            -- MSBrand còn giữ liên kết tới watch đã bị xoá
   OR bw.WatchID IS NULL           -- Watch có ở DBWatch nhưng MSBrand không biết
   OR w.BrandID <> bw.BrandID;     -- Hai bên lệch BrandID
```

* **Kết quả đạt chuẩn:** Luôn trả về **0 dòng** (dữ liệu 2 phía hoàn toàn nhất quán).

---

## 9. Xử lý các lỗi thường gặp (Troubleshooting)

| Vấn đề | Nguyên nhân | Cách khắc phục |
|---|---|---|
| **Lỗi `Cannot open database "DB..."` khi khởi động** | Chưa tạo database trên SQL Server | Chạy lại lệnh tạo 3 DB ở Mục 2.1 |
| **Lỗi `Login failed for user 'sa'`** | Mật khẩu tài khoản `sa` khác với cấu hình | Đặt lại mật khẩu `sa` thành `YourStrong@Password123` bằng lệnh ở Mục 2.1 |
| **Postman báo lỗi `Release date must be today's date` (400)** | Ngày truyền vào request body không khớp với ngày hiện tại của máy chạy service | Cập nhật biến `todayDate` trong Postman khớp với ngày hôm nay (YYYY-MM-DD) |
| **Postman báo lỗi `Watch count mismatch` ở Folder 03 hoặc 06** | Các lần test trước đã thêm/xoá làm lệch số lượng đồng hồ | Chạy script SQL Reset ở Mục 2.2 và khởi động lại các service |
| **Header `X-Saga-Fail-After-Step` không có tác dụng giả lập lỗi** | Biến `saga.fault-injection.enabled` đang là `false` | Đổi thành `true` trong `application.yml` của MSWatch hoặc trong file `.env` |
| **Gateway trả về 503 "Watch Service is currently unavailable" sau 1-2s** | TimeLimiter của Resilience4j bị để mặc định 1s | Đã được cấu hình `timeout-duration: 15s` trong `APIGateway/src/main/resources/application.yml` |
| **Lỗi Lombok không nhận Getter/Setter trong IntelliJ** | Chưa bật Annotation Processing | Mở IntelliJ ➔ Settings ➔ Build, Execution, Deployment ➔ Compiler ➔ Annotation Processors ➔ Tích chọn **Enable annotation processing** |

