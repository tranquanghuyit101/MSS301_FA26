# Assignment 02 – Watch Management Microservices (Saga Pattern)

> **Môn:** MSS301 · **Chủ đề:** Transactions in Microservices – Saga Orchestration (Chapter 06, Slide 19 → 27)
> **Stack bắt buộc:** Java 21 · Spring Boot 4.1.1 · Spring Cloud 2025.1.3 · Hibernate 7 · Jackson 3 · MS SQL Server · JWT (jjwt 0.13.0)
> **Tài liệu đi kèm:** `WatchManagement/WatchManagement_Saga.postman_collection.json` (script kiểm thử). Lời giải nằm ở `Assignment_Solution.md` (dành cho giảng viên).

---

## Mục lục

- [1. Mô tả đề bài](#1-mô-tả-đề-bài)
- [2. Kiến thức nền: Saga Pattern](#2-kiến-thức-nền-saga-pattern)
- [3. Kiến trúc & đặc tả API](#3-kiến-trúc--đặc-tả-api)
- [4. Quy ước Git & Commit](#4-quy-ước-git--commit)
- [5. Các bước thực hiện (TODO + Checklist)](#5-các-bước-thực-hiện-todo--checklist)
- [6. Kiểm thử chứng minh Saga](#6-kiểm-thử-chứng-minh-saga)
- [7. Definition of Done](#7-definition-of-done)
- [8. Câu hỏi vấn đáp](#8-câu-hỏi-vấn-đáp)

> **Cách đọc:** mỗi bước có 🎯 **TODO** (mã `TODO-x.y`), ☑️ **Checklist kiểm tra** (bắt buộc đạt trước khi commit) và 📝 **Yêu cầu commit**.

---

## 1. Mô tả đề bài

Xây dựng hệ thống microservices cho cửa hàng đồng hồ. Thách thức chính: **giữ dữ liệu nhất quán giữa nhiều service mà không dùng distributed transaction kiểu 2PC**, bằng **Saga Pattern (Orchestration)**.

### 1.1. Thành phần

| Project | Cổng | Database | Vai trò |
|---|---|---|---|
| `APIGateway_StudentCode` | 8080 | – | Điểm vào duy nhất: routing, xác thực JWT, Circuit Breaker |
| `MSAccount_StudentCode` | 8081 | DBAccount (`StoreAccounts`) | Đăng nhập, phát JWT |
| `MSBrand_StudentCode` | 8082 | DBBrand (`WatchBrands`, `BrandWatches`) | Quản lý thương hiệu – **Saga participant** |
| `MSWatch_StudentCode` | 8083 | DBWatch (`Watches`, `WatchCategories`, `SagaStates`, `SagaLogs`) | Quản lý đồng hồ – **Saga orchestrator** |

Mỗi service chỉ kết nối tới database của chính nó (**Database per Service**), dùng JPA/Hibernate code-first.

### 1.2. Yêu cầu chức năng

1. Liệt kê toàn bộ đồng hồ (kèm `CategoryName`). **Không cần quyền.**
2. Admin (role = 1) **xoá** đồng hồ, đồng thời cập nhật các microservice liên quan.
3. Admin **thêm** đồng hồ: hiển thị ở **đầu** danh sách; mọi field bắt buộc; `Price ≥ 100`; `Name` dài hơn 10 ký tự; `ReleaseDate` = ngày hiện tại; sau đó cập nhật các microservice liên quan.
4. Admin **sửa** đồng hồ với cùng ràng buộc như thêm; sau đó cập nhật các microservice liên quan.
5. Viết Postman script kiểm thử qua API Gateway.

> "Cập nhật các microservice liên quan" trong bài này: MSBrand lưu danh sách đồng hồ của từng thương hiệu (bảng `BrandWatches`). Mỗi thao tác thêm/sửa/xoá đồng hồ phải cập nhật **cả DBWatch lẫn DBBrand** một cách nhất quán.

### 1.3. Dữ liệu bắt buộc

Tài khoản (mật khẩu đều là `@1`):

| AccountID | Username | Email | Role | IsActive |
|---|---|---|---|---|
| 1 | adminsys | admin@drawingpen.com.vn | 1 | 1 |
| 2 | staff02 | staff02@drawingpen.com.vn | 2 | 1 |
| 3 | member01 | member01@drawingpen.com.vn | 3 | 1 |
| 4 | member02 | member02@drawingpen.com.vn | 3 | 0 |
| 5 | staff01 | staff01@drawingpen.com.vn | 2 | 0 |

Thương hiệu: 1 Rolex (Switzerland), 2 Omega (Switzerland), 3 Seiko (Japan), 4 Casio (Japan), 5 TAG Heuer (Switzerland).

Danh mục: 1 Dive, 2 Chronograph, 3 Dress, 4 Digital, 5 Pilot (mô tả, MovementType, PriceRange **nguyên văn** theo file đề).

Đồng hồ (rút gọn – đủ cột xem file đề `MMS301_Assignment 02_Watch Management_Saga Pattern.docx`):

| WatchID | Name | CategoryID | BrandID |
|---|---|---|---|
| 1 | Submariner Date | 1 | 1 |
| 2 | Speedmaster Moonwatch Professional | 2 | 2 |
| 3 | Presage Cocktail Time | 3 | 3 |
| 4 | G-Shock DW-5600E-1V | 4 | 4 |
| 5 | Carrera Calibre Heuer 02 | 2 | 5 |
| 6 | Seamaster Diver 300M | 1 | 2 |
| 7 | Prospex SPB143 | 1 | 3 |
| 8 | Daytona | 2 | 1 |
| 9 | F-91W | 4 | 4 |
| 10 | IWC Pilot's Watch Mark XVIII | 5 | 4 |

`BrandWatches` ban đầu phải khớp cột BrandID ở trên → số đồng hồ: **Rolex 2, Omega 2, Seiko 2, Casio 3, TAG Heuer 1**.

---

## 2. Kiến thức nền: Saga Pattern

### 2.1. Vì sao cần Saga?

Đề bài yêu cầu: thêm/sửa/xoá đồng hồ **"and then update other related Microservices"**. Trong project này, MSBrand lưu danh sách đồng hồ thuộc từng thương hiệu (bảng `BrandWatches`). Vậy mỗi thao tác chạm vào **2 database**:

```
POST /api/watches  ──►  DBWatch.Watches         (MSWatch)
                   ──►  DBBrand.BrandWatches    (MSBrand)
```

- **Không dùng được `@Transactional`**: nó chỉ quản lý được 1 database (DBWatch). Lời gọi HTTP sang MSBrand nằm ngoài transaction.
- **Không nên dùng 2PC**: phải lock tài nguyên ở cả hai service, coordinator là single point of failure.
- **Saga**: chia thành **chuỗi local transaction**; mỗi bước có một **compensating transaction**. Nếu một bước lỗi, các bước **đã commit** được hoàn tác theo **thứ tự ngược**.

### 2.2. Thiết kế 3 Saga (Orchestration)

MSWatch đóng vai **Orchestrator**, MSBrand là **Participant**.

**Saga CREATE_WATCH**

| Bước | Local transaction | Database | Compensating transaction |
|---|---|---|---|
| 1 | `CREATE_WATCH`: INSERT watch | DBWatch | `DELETE_WATCH` (xoá watch vừa thêm) |
| 2 | `ASSIGN_BRAND`: gán watch vào brand | DBBrand | `UNASSIGN_BRAND` (gỡ ra) |

**Saga UPDATE_WATCH**

| Bước | Local transaction | Database | Compensating transaction |
|---|---|---|---|
| 1 | `UPDATE_WATCH`: ghi dữ liệu mới | DBWatch | `RESTORE_WATCH` (ghi lại snapshot cũ) |
| 2 | `ASSIGN_BRAND`: chuyển watch sang brand mới | DBBrand | `ASSIGN_BRAND_BACK` (gán lại brand cũ) |

**Saga DELETE_WATCH**

| Bước | Local transaction | Database | Compensating transaction |
|---|---|---|---|
| 1 | `UNASSIGN_BRAND`: gỡ watch khỏi brand | DBBrand | `ASSIGN_BRAND_BACK` |
| 2 | `DELETE_WATCH`: xoá watch | DBWatch | **không có → PIVOT** |

> **Pivot transaction:** là bước mà sau khi commit, Saga **không thể quay lui** nữa. Xoá cứng một dòng có `IDENTITY` thì không khôi phục được đúng `WatchID` cũ, nên `DELETE_WATCH` được đặt **cuối cùng** làm pivot. Bước có rủi ro lỗi cao (gọi qua mạng) được làm **trước**, khi còn có thể bù trừ.

### 2.3. Máy trạng thái Saga 

```
PENDING ──► EXECUTING ──────────────────────────────► COMPLETED
                │ (một bước lỗi)
                ▼
             FAILED ──► COMPENSATING ──► COMPENSATED      (đã bù trừ xong, dữ liệu nhất quán)
                              │
                              └─ (compensation lỗi sau 3 lần) dừng ở COMPENSATING → cần xử lý thủ công
```

### 2.4. Luồng thất bại điển hình (tạo watch với brand 999)

```
MSWatch (Orchestrator)                 DBWatch                 MSBrand / DBBrand
   │ [1] CREATE_WATCH ───────────────► INSERT Watches (id=11) ✔ COMMIT
   │ [2] ASSIGN_BRAND ──── PUT /internal/brands/999/watches/11 ──► 404 Brand not found
   │      → FAILED
   │      → COMPENSATING
   │ [C1] DELETE_WATCH ──────────────► DELETE Watches id=11 ✔
   │      → COMPENSATED
   ▼  HTTP 400 {"sagaStatus":"COMPENSATED","failedStep":"ASSIGN_BRAND"}
```

Điểm mấu chốt để sinh viên hiểu: watch id=11 **đã thực sự được commit** vào DBWatch rồi mới bị xoá. Đây là *compensation*, khác với *rollback* của `@Transactional`. Bằng chứng: WatchID 11 bị "nhảy cóc", watch tạo thành công tiếp theo sẽ có id = 12.

### 2.5. Yêu cầu đối với compensating transaction 

| Thuộc tính | Ý nghĩa | Áp dụng trong bài |
|---|---|---|
| **Idempotent** | Gọi nhiều lần cho cùng kết quả | Gán/gỡ watch ở MSBrand gọi lặp lại vẫn an toàn |
| **Reversible** | Hoàn tác được tác dụng của bước gốc | Lưu snapshot `before` để RESTORE, lưu brand cũ để gán lại |
| **Reliable** | Hiếm khi thất bại; nếu lỗi tạm thời thì thử lại | Retry tối đa 3 lần; vẫn lỗi thì dừng ở `COMPENSATING` |

### 2.6. Anti-pattern khi cài Saga (KHÔNG làm theo)

Đây là những cách viết "trông giống Saga" nhưng **sai bản chất**. Sinh viên rất hay mắc phải:

| # | Cách viết sai | Hậu quả thực tế | Cách đúng |
|---|---|---|---|
| 1 | Gắn `@CircuitBreaker(fallbackMethod = ...)` lên hàm Saga, fallback nhận `Exception ex` rồi vẫn `save(watch)` | Fallback bắt **mọi** exception, kể cả lỗi "Brand not found" do chính code ném ra → tạo watch với brandId = 999 vẫn trả **201** | Không có fallback "lưu tạm". Lỗi từ MSBrand luôn dẫn tới **compensation** |
| 2 | Đặt `@Transactional` bao cả hàm orchestrator (gồm lời gọi Feign) | Khi lỗi, DB rollback toàn bộ, kể cả dòng `SagaStates` → không bao giờ thấy `COMPENSATED`. "Bù trừ" thực ra chỉ là rollback của 1 database, không phải Saga | Orchestrator **không** `@Transactional`; mỗi bước là 1 local transaction; nhật ký ghi bằng `REQUIRES_NEW` |
| 3 | Chỉ **đọc** service khác (VD: gọi `/brands/{id}/exists` để kiểm tra) | Không có dữ liệu nào ở service khác cần giữ nhất quán → không có distributed transaction; không đáp ứng *"update other related Microservices"* | MSBrand **ghi** bảng `BrandWatches` qua API nội bộ gán / gỡ watch |
| 4 | Không lưu lại các bước đã chạy | Không chứng minh được Saga đã bù trừ những gì | Bảng `SagaLogs`, API `/api/sagas/{id}`, header `X-Saga-Id`, fault injection `X-Saga-Fail-After-Step` |
| 5 | Compensation không idempotent (VD: `release` cộng kho mỗi lần gọi) | Retry compensation gây sai dữ liệu | Mọi compensation gọi lặp lại đều an toàn |

### 2.7. Lỗi bảo mật & cấu hình cần tránh

| Cách viết sai | Hậu quả | Cách đúng |
|---|---|---|
| Gateway coi `/api/watches` là public bằng `path.startsWith("/api/watches")` | `POST/PUT/DELETE` cũng không cần token; client tự gửi `X-User-Role: 1` là xoá được đồng hồ | Chỉ `GET /api/watches` là public; Gateway **luôn xoá** `X-User-*` do client gửi |
| Để TimeLimiter của Gateway mặc định (1s) | Saga có retry compensation > 1s → Gateway trả 503 trong khi MSWatch vẫn đang chạy | `timeout-duration: 15s` |
| Để naming strategy mặc định | Bảng thành `store_accounts`, cột thành `watch_id`, không đúng tên bảng của đề bài | `PhysicalNamingStrategyStandardImpl` |

---

## 3. Kiến trúc & đặc tả API

### 3.1. Kiến trúc

```
                         ┌──────────────── API Gateway :8080 ────────────────┐
 Client (Postman) ─────► │ JwtAuthFilter (verify JWT, gắn X-User-Id/Role)    │
                         │ Routes + CircuitBreaker + Fallback                │
                         └──────┬───────────────┬────────────────┬───────────┘
                                │               │                │
                        /api/auth/**     /api/brands/**   /api/watches/**, /api/sagas/**
                                ▼               ▼                ▼
                          MSAccount :8081  MSBrand :8082 ◄──── MSWatch :8083
                          (DBAccount)      (DBBrand)   Feign   (DBWatch)
                                           PARTICIPANT /internal/** ORCHESTRATOR
```

| Thành phần | Công nghệ |
|---|---|
| Ngôn ngữ / framework | Java 21, Spring Boot 4.1.1 (Spring Framework 7, Hibernate 7, Jackson 3) |
| Spring Cloud | 2025.1.3 (Oakwood): OpenFeign, Gateway server WebFlux, CircuitBreaker Resilience4j |
| Bảo mật | JWT HMAC-SHA (jjwt 0.13.0), BCrypt |
| Database | SQL Server, mỗi service 1 database |
| Tài liệu API | springdoc-openapi 3.0.2 (Swagger UI) |

### 3.2. Đặc tả API (qua Gateway `http://localhost:8080`)

| Method | URL | Quyền | Kết quả |
|---|---|---|---|
| POST | `/api/auth/login` | Public | 200 token · 401 sai thông tin · 403 inactive · 400 thiếu field |
| POST | `/api/auth/refresh` | Public | 200 token mới · 401 không phải refresh token |
| POST | `/api/auth/logout` | Public | 200 |
| GET | `/api/watches` | **Public** | 200, mới nhất trước, có `categoryName` |
| POST | `/api/watches` | Admin | 201 + header `X-Saga-Id` · 400 validation / brand không tồn tại · 403 · 500/503 Saga lỗi |
| PUT | `/api/watches/{id}` | Admin | 200 + `X-Saga-Id` · 404 không có watch · 400/403/500/503 |
| DELETE | `/api/watches/{id}` | Admin | 200 + `X-Saga-Id` · 404 · 403/500/503 |
| GET | `/api/brands`, `/api/brands/{id}` | Đăng nhập | 200, có `watchCount` |
| GET | `/api/brands/{id}/watches` | Đăng nhập | `{brandId, brandName, watchCount, watchIds[]}` – dùng để kiểm chứng Saga |
| GET | `/api/sagas?limit=20`, `/api/sagas/{sagaId}` | Admin | Trạng thái Saga + danh sách bước |

API **nội bộ** của MSBrand (chỉ MSWatch gọi trực tiếp cổng 8082, Gateway **không** route `/internal/**`):

| Method | URL | Dùng cho | Yêu cầu |
|---|---|---|---|
| PUT | `/internal/brands/{brandId}/watches/{watchId}` | ASSIGN_BRAND, ASSIGN_BRAND_BACK | Upsert, brand không tồn tại → 404, idempotent |
| DELETE | `/internal/brands/watches/{watchId}` | UNASSIGN_BRAND | Không có gì để gỡ → 200, idempotent |

Header đặc biệt:

| Header | Chiều | Ý nghĩa |
|---|---|---|
| `Authorization: Bearer <accessToken>` | Request | Bắt buộc với API không public |
| `X-User-Id`, `X-User-Role` | Gateway → service | **Chỉ Gateway** được đặt (sau khi verify JWT); giá trị client tự gửi phải bị xoá |
| `X-Saga-Id` | Response | Id của Saga vừa chạy (cả khi thành công lẫn thất bại) |
| `X-Saga-Fail-After-Step: N` | Request | **Chỉ dùng khi test**: giả lập lỗi ngay sau khi bước N commit (bật/tắt bằng `saga.fault-injection.enabled`) |

### 3.3. Định dạng response khi Saga thất bại

```json
{
  "success": false,
  "message": "Saga COMPENSATED: MSBrand returned 404: Brand not found with id: 999",
  "data": {
    "sagaId": "3f2b...",
    "sagaStatus": "COMPENSATED",
    "failedStep": "ASSIGN_BRAND",
    "reason": "MSBrand returned 404: Brand not found with id: 999"
  }
}
```

| Nguyên nhân | HTTP |
|---|---|
| Brand không tồn tại (MSBrand 404) | 400 |
| MSBrand tắt / lỗi 5xx | 503 |
| Lỗi giả lập (fault injection) | 500 |
| Validation (name, price, releaseDate, category) | 400, **chưa** tạo Saga |

### 3.4. Hành vi fault injection bắt buộc

| Saga | Header | Kết quả mong đợi |
|---|---|---|
| CREATE | `2` | UNASSIGN_BRAND → DELETE_WATCH, `COMPENSATED` |
| UPDATE | `2` | ASSIGN_BRAND_BACK → RESTORE_WATCH, `COMPENSATED` |
| DELETE | `1` | ASSIGN_BRAND_BACK, watch còn nguyên, `COMPENSATED` |
| DELETE | `2` | **Bị bỏ qua** (đã qua pivot) → `COMPLETED`, log `FAULT SKIPPED` |

---

## 4. Quy ước Git & Commit

### 4.1. Chuẩn Conventional Commits

```
<type>(<scope>): <subject>
                                   ← dòng trống
<body: giải thích VÌ SAO>
                                   ← dòng trống
Refs: TODO-x.y
```

| type | Khi nào dùng | Ví dụ trong bài |
|---|---|---|
| `feat` | Thêm chức năng | `feat(ms-brand): expose idempotent internal assign and unassign API` |
| `fix` | Sửa lỗi | `fix(ms-watch): reject saga when brand service is unreachable` |
| `refactor` | Đổi cấu trúc code, không đổi hành vi | `refactor(ms-watch): extract saga step record` |
| `build` | pom, dependency, Dockerfile, compose | `build: scaffold services on Spring Boot 4.1.1` |
| `test` | Test, Postman | `test(postman): add collection proving saga completion and compensation` |
| `docs` | Tài liệu | `docs: add saga design for watch create, update and delete` |
| `chore` | Cấu hình, việc lặt vặt | `chore: initialize repository with gitignore and env template` |

| scope | Phạm vi |
|---|---|
| `ms-account`, `ms-brand`, `ms-watch`, `gateway` | Từng service |
| `config`, `docker`, `postman` | Cấu hình chung, Docker, Postman |

**Quy tắc bắt buộc:**

1. Subject viết **tiếng Anh**, động từ nguyên mẫu (`add`, `implement`, không phải `added`), chữ thường, **≤ 72 ký tự**, không dấu chấm cuối.
2. **1 commit = 1 thay đổi logic.** Không gộp "entity + orchestrator + gateway" vào 1 commit.
3. Footer `Refs: TODO-x.y` để giảng viên đối chiếu commit với TODO.
4. Thay đổi phá vỡ tương thích (đổi URL API, đổi schema) thì thêm `!` sau type/scope và footer `BREAKING CHANGE:`.
5. **Không commit:** `target/`, `.idea/`, `*.iml`, **`.env`** (chứa mật khẩu DB và JWT secret).
6. Mỗi nhánh feature phải **build pass + đủ checklist** trước khi merge `--no-ff` vào `main`.

**Ví dụ sai → đúng:**

| ❌ Sai | ✅ Đúng |
|---|---|
| `update code` | `feat(ms-watch): implement saga orchestrator with LIFO compensation` |
| `Fixed bug.` | `fix(gateway): strip client supplied user headers` |
| `feat: thêm saga, sửa gateway, thêm docker` | Tách thành 3 commit ở 3 nhánh |

### 4.2. Chiến lược nhánh

```
main ─●────●──────●──────●───────────●───────────●──────────●────────●──── v1.0.0
       \  / \    /  \   /  \        /  \        /  \       /  \     /
       feature/ feature/ docs/  feature/    feature/     feature/   test/    chore/
       scaffold ms-account saga- ms-brand-  ms-watch-    gateway    saga-    docker
                          design participant saga                   proof
```

### 🎯 TODO – Git (Bước 0)

| Mã | Việc cần làm | File / vị trí |
|---|---|---|
| **TODO-0.1** | `git init` tại thư mục `WatchManagement/`, cài commit template | `.gitmessage` |
| **TODO-0.2** | Tạo `.gitignore` (bỏ `target/`, `.idea/`, `.env`) và `.env.example` | `.gitignore`, `.env.example` |
| **TODO-0.3** | Commit khởi tạo trên `main`; mỗi bước sau làm trên nhánh riêng như sơ đồ | — |

### ☑️ Checklist kiểm tra

- [ ] `git status` **không** liệt kê `.env`, `target/`, `.idea/`
- [ ] `git config commit.template` trả về `.gitmessage`
- [ ] `git config user.name` / `user.email` là thông tin của sinh viên
- [ ] `.env.example` có đủ các biến nhưng **không** chứa secret thật
### 📝 Yêu cầu commit

- Commit khởi tạo trên `main`: `chore: ...` — `Refs: TODO-0.1, TODO-0.2, TODO-0.3`.
- Cài template commit: `git config commit.template .gitmessage`.

---

## 5. Các bước thực hiện (TODO + Checklist)

### Bước 1: Tạo 4 project Spring Boot 4.1.1

##### 1.1. Công cụ

| Công cụ | Version | Ghi chú |
|---|---|---|
| JDK | 21 (LTS) | Boot 4 yêu cầu tối thiểu 17 |
| Maven | 3.9+ | |
| IntelliJ IDEA | 2025.2+ | Bật *Annotation Processing* cho Lombok |
| SQL Server | 2019/2022 | Bật SQL Server Authentication, tài khoản `sa` |
| Postman | Latest | Import file `WatchManagement_Saga.postman_collection.json` |
| Docker Desktop | tuỳ chọn | |

```bash
java -version     # openjdk 21...
mvn -version      # Apache Maven 3.9...
```

##### 1.2. Tạo project bằng Spring Initializr

Vào <https://start.spring.io> (hoặc IntelliJ → *New Project → Spring Boot*), chọn **Maven, Java 21, Spring Boot 4.1.1, Group `com.mss301`, Packaging Jar**.

| Project | Artifact | Dependencies |
|---|---|---|
| MSAccount_StudentCode | `ms-account` | Spring Web, Spring Data JPA, Spring Security, Validation, MS SQL Server Driver, Lombok |
| MSBrand_StudentCode | `ms-brand` | Spring Web, Spring Data JPA, Validation, MS SQL Server Driver, Lombok |
| MSWatch_StudentCode | `ms-watch` | Spring Web, Spring Data JPA, Validation, MS SQL Server Driver, **OpenFeign**, Lombok |
| APIGateway_StudentCode | `api-gateway` | **Reactive Gateway**, **Resilience4J (Reactive)**, Lombok |

Thêm thủ công vào pom: `jjwt-api/impl/jackson 0.13.0` (MSAccount, Gateway) và `springdoc-openapi-starter-webmvc-ui 3.0.2` (3 service MVC).

> Spring Initializr với Boot 4 sinh starter `spring-boot-starter-webmvc` (Spring Web) và `spring-cloud-starter-gateway-server-webflux` (Reactive Gateway).

##### 1.3. Cấu trúc thư mục

```
WatchManagement/
├── .gitignore                ← [TODO-0.2] không commit target/, .idea/, .env
├── .env.example              ← [TODO-0.2] mẫu biến môi trường (commit file này, không commit .env)
├── .gitmessage               ← [TODO-0.1] template commit message
├── docs/SAGA_DESIGN.md       ← [TODO-4.1] thiết kế Saga
├── docker-compose.yml
├── WatchManagement_Saga.postman_collection.json   ← script test chứng minh Saga
├── APIGateway_StudentCode/   # 8080 - routing + JWT
├── MSAccount_StudentCode/    # 8081 - login, phát JWT
├── MSBrand_StudentCode/      # 8082 - Saga PARTICIPANT (DBBrand)
└── MSWatch_StudentCode/      # 8083 - Saga ORCHESTRATOR (DBWatch)
```

#### 🎯 TODO

| Mã | Việc cần làm | File / vị trí |
|---|---|---|
| **TODO-1.1** | Tạo 4 project bằng Spring Initializr: Maven, Java 21, Boot **4.1.1**, group `com.mss301` | 4 project |
| **TODO-1.2** | MSAccount, MSBrand, MSWatch: `webmvc`, `data-jpa`, `validation`, `mssql-jdbc` (runtime), Lombok; MSAccount thêm `security` | 3 × `pom.xml` |
| **TODO-1.3** | Import BOM Spring Cloud **2025.1.3**; MSWatch thêm `openfeign`; Gateway dùng `gateway-server-webflux` + `circuitbreaker-reactor-resilience4j` | MSWatch, Gateway `pom.xml` |
| **TODO-1.4** | Khai báo version qua `<properties>`: jjwt **0.13.0** (MSAccount, Gateway), springdoc **3.0.2** (3 service MVC) | `pom.xml` |
| **TODO-1.5** | Lombok trong `maven-compiler-plugin` → `annotationProcessorPaths`; exclude Lombok khỏi fat-jar | 4 × `pom.xml` |

#### ☑️ Checklist kiểm tra

- [ ] `mvn -v` hiển thị Maven 3.9+ và Java 21
- [ ] IntelliJ: *Maven → Reload All Maven Projects* không còn dependency báo đỏ
- [ ] `mvn dependency:tree | grep spring-cloud` ở MSWatch hiển thị version của train 2025.1.3
- [ ] `mvn -q -DskipTests package` thành công ở **cả 4** project
- [ ] Gateway khởi động được ở cổng 8080 (chưa có route)

#### 📝 Yêu cầu commit

- Làm trên nhánh **`feature/scaffold`** (tiếp tục dùng ở bước sau).
- Tách tối thiểu **2 commit** theo nhóm TODO, mỗi commit build được:
  1. `build: ...` — `Refs: TODO-1.1, TODO-1.2, TODO-1.4, TODO-1.5`
  2. `build: ...` — `Refs: TODO-1.1, TODO-1.3, TODO-1.4, TODO-1.5`

### Bước 2: Tạo database & cấu hình datasource

Mỗi microservice sở hữu một database riêng (**Database per Service**): service A không được đọc/ghi trực tiếp database của service B.

```sql
CREATE DATABASE DBAccount;
CREATE DATABASE DBBrand;
CREATE DATABASE DBWatch;
GO
ALTER LOGIN sa ENABLE;
ALTER LOGIN sa WITH PASSWORD = 'YourStrong@Password123';
```

Hibernate tự tạo bảng khi service khởi động (`ddl-auto: update`), giữ nguyên tên trong `@Table`/`@Column` nhờ `PhysicalNamingStrategyStandardImpl`:

| Database | Bảng | Ai sở hữu |
|---|---|---|
| DBAccount | `StoreAccounts` | MSAccount |
| DBBrand | `WatchBrands`, `BrandWatches` | MSBrand |
| DBWatch | `Watches`, `WatchCategories`, `SagaStates`, `SagaLogs` | MSWatch |

> ⚠️ **Reset dữ liệu:** `BrandWatches` được seed theo `WatchID` 1..10. Khi muốn làm lại từ đầu, hãy xoá và tạo lại **cả DBWatch lẫn DBBrand** để ID hai bên khớp nhau.

Cấu hình bắt buộc trong `application.yml`: `ddl-auto: update`, `open-in-view: false`, `spring.jpa.hibernate.naming.physical-strategy: org.hibernate.boot.model.naming.PhysicalNamingStrategyStandardImpl`, URL đọc `${DB_HOST:localhost}` và `${DB_PORT:1433}`, mật khẩu đọc `${DB_PASSWORD}`.

#### 🎯 TODO

| Mã | Việc cần làm | File / vị trí |
|---|---|---|
| **TODO-2.1** | Tạo DBAccount, DBBrand, DBWatch; bật SQL Server Authentication và login `sa` | SSMS |
| **TODO-2.2** | Cấu hình datasource cho 3 service: URL `${DB_HOST}`/`${DB_PORT}`, `ddl-auto: update`, `open-in-view: false`, `physical-strategy: PhysicalNamingStrategyStandardImpl` | 3 × `application.yml` |

#### ☑️ Checklist kiểm tra

- [ ] SSMS thấy đủ 3 database **trống**
- [ ] Khởi động MSAccount / MSBrand / MSWatch không lỗi kết nối (`HikariPool-1 - Start completed`)
- [ ] Bảng được tạo đúng tên **`StoreAccounts`**, **`Watches`**, **`WatchBrands`** (không phải `store_accounts`)
- [ ] Cột đúng tên **`WatchID`**, **`BrandID`** (không phải `watch_id`)
- [ ] Không khai báo `hibernate.dialect` (Hibernate 7 tự nhận SQL Server)

#### 📝 Yêu cầu commit

- Làm trên nhánh **`feature/scaffold`**, merge `--no-ff` vào `main` khi đạt đủ checklist.
- Tách tối thiểu **1 commit** theo nhóm TODO, mỗi commit build được:
  1. `chore(config): ...` — `Refs: TODO-2.1, TODO-2.2`

### Bước 3: MSAccount – JWT Authentication

MSAccount là **identity provider**: xác thực username/password, phát JWT. Việc **verify** JWT do API Gateway đảm nhận.

```
Client ──POST /api/auth/login──► Gateway ──► MSAccount ──► {accessToken (15'), refreshToken (7 ngày)}
Client ──Bearer token──► Gateway [JwtAuthFilter: verify chữ ký + hạn] ──X-User-Id, X-User-Role──► MSWatch / MSBrand
```

Payload của access token: `{"sub":"1","role":1,"type":"access","iat":...,"exp":...}`.

Tài khoản seed (mật khẩu đều là `@1`, lưu dạng BCrypt):

| Username | Role | Active |
|---|---|---|
| adminsys | 1 (Admin) | ✔ |
| staff02 | 2 (Staff) | ✔ |
| member01 | 3 (Member) | ✔ |
| member02 | 3 | ✘ → login trả 403 |
| staff01 | 2 | ✘ |

> Thứ tự kiểm tra khi login: tìm username → kiểm tra `isActive` (403) → kiểm tra mật khẩu BCrypt (401).

#### 🎯 TODO

| Mã | Việc cần làm | File / vị trí |
|---|---|---|
| **TODO-3.1** | Entity `StoreAccount` (bảng `StoreAccounts`, `@Builder.Default isActive = true`), `AccountRepository.findByUsername`, seed 5 tài khoản với BCrypt | `entity/`, `repository/`, `DataInitializer.java` |
| **TODO-3.2** | `JwtService`: access token (claim `role`, `type=access`, 15 phút), refresh token (`type=refresh`, 7 ngày); cấu hình `jwt.*` đọc từ biến môi trường | `service/JwtService.java`, `application.yml` |
| **TODO-3.3** | `AuthService.login` (inactive → 403, sai mật khẩu → 401) và `refresh` (chỉ nhận refresh token) | `service/AuthService.java` |
| **TODO-3.4** | `AuthController` (`/api/auth/login`, `/refresh`, `/logout`), `SecurityConfig` (permitAll + BCrypt), DTO, `GlobalExceptionHandler` | `controller/`, `config/`, `dto/`, `exception/` |
| **TODO-3.5** | Test trực tiếp cổng 8081 bằng Postman | Postman |

#### ☑️ Checklist kiểm tra

- [ ] Log khởi động: `Seeded 5 accounts`; cột `Password` trong DB bắt đầu bằng `$2a$`
- [ ] `POST :8081/api/auth/login` adminsys/@1 → 200, có `accessToken`, `refreshToken`, `role = 1`
- [ ] Dán accessToken vào jwt.io: payload có `sub`, `role`, `type = access`, `exp` sau 15 phút
- [ ] member02 → **403** `Account is inactive`; sai mật khẩu → **401**; thiếu username → **400**
- [ ] `POST /api/auth/refresh` với refreshToken → 200; với accessToken → **401** `Token is not a refresh token`

#### 📝 Yêu cầu commit

- Làm trên nhánh **`feature/ms-account`**, merge `--no-ff` vào `main` khi đạt đủ checklist.
- Tách tối thiểu **3 commit** theo nhóm TODO, mỗi commit build được:
  1. `feat(ms-account): ...` — `Refs: TODO-3.1`
  2. `feat(ms-account): ...` — `Refs: TODO-3.2`
  3. `feat(ms-account): ...` — `Refs: TODO-3.3, TODO-3.4`

### Bước 4: Thiết kế Saga trước khi code

Dựa vào mục 2, hoàn thành tài liệu thiết kế `docs/SAGA_DESIGN.md` (bảng bước, compensation, idempotent, pivot, state machine) và nộp cho giảng viên duyệt **trước** khi code MSBrand/MSWatch.

#### 🎯 TODO

| Mã | Việc cần làm | File / vị trí |
|---|---|---|
| **TODO-4.1** | Viết `docs/SAGA_DESIGN.md`: bảng bước / compensation / idempotent cho 3 Saga, state machine, pivot | `docs/SAGA_DESIGN.md` |
| **TODO-4.2** | Giải thích được vì sao không dùng `@Transactional` / 2PC cho bài này | (vấn đáp) |

#### ☑️ Checklist kiểm tra

- [ ] Mỗi bước (trừ pivot) có **đúng 1** compensation tương ứng
- [ ] Chỉ ra được bước nào là **pivot** và vì sao nó đứng **cuối**
- [ ] Mỗi compensation được đánh dấu idempotent ✔ và có cách hiện thực cụ thể
- [ ] Vẽ được luồng thất bại của CREATE với brand 999 (như mục 4.4)
- [ ] Giảng viên duyệt thiết kế trước khi sinh viên sang Bước 5

#### 📝 Yêu cầu commit

- Làm trên nhánh **`docs/saga-design`**, merge `--no-ff` vào `main` khi đạt đủ checklist.
- Tách tối thiểu **1 commit** theo nhóm TODO, mỗi commit build được:
  1. `docs: ...` — `Refs: TODO-4.1`

### Bước 5: MSBrand – Participant của Saga

MSBrand sở hữu bảng `BrandWatches` (WatchID unique, BrandID). Đây là dữ liệu mà mọi Saga phải giữ nhất quán với `Watches` ở DBWatch.

**Vì sao phải idempotent?** Orchestrator **retry** compensation khi gặp lỗi mạng. Nếu `unassignWatch` không idempotent, retry có thể gây lỗi hoặc tác dụng phụ kép. Ở đây:

- `assignWatch(b, w)` là upsert: gọi 1 lần hay 5 lần đều cho cùng kết quả "watch w thuộc brand b".
- `unassignWatch(w)` khi không có gì để gỡ thì vẫn trả 200 (`NOTHING_TO_DO`).

`DataInitializer` seed 5 brand của đề bài và 10 dòng `BrandWatches` khớp với 10 watch (WatchID → BrandID): 1→1, 2→2, 3→3, 4→4, 5→5, 6→2, 7→3, 8→1, 9→4, 10→4.

Số lượng ban đầu: **Rolex 2, Omega 2, Seiko 2, Casio 3, TAG Heuer 1**.

#### 🎯 TODO

| Mã | Việc cần làm | File / vị trí |
|---|---|---|
| **TODO-5.1** | Entity `WatchBrand` (bảng `WatchBrands`) và `BrandWatch` (bảng `BrandWatches`, `WatchID` unique) + 2 repository | `entity/`, `repository/` |
| **TODO-5.2** | `assignWatch(brandId, watchId)`: upsert, brand không tồn tại → 404, **idempotent** | `service/BrandService.java` |
| **TODO-5.3** | `unassignWatch(watchId)`: không có gì để gỡ → 200 `NOTHING_TO_DO` | `service/BrandService.java` |
| **TODO-5.4** | `InternalBrandController`: `PUT /internal/brands/{b}/watches/{w}`, `DELETE /internal/brands/watches/{w}`; lỗi trả `ApiResponse` | `controller/`, `dto/`, `exception/` |
| **TODO-5.5** | API public: `GET /api/brands` (có `watchCount`), `/api/brands/{id}`, `/api/brands/{id}/watches` | `BrandController`, `BrandService` |
| **TODO-5.6** | Seed 5 brand của đề bài + 10 dòng `BrandWatches` khớp WatchID → BrandID | `DataInitializer.java` |

#### ☑️ Checklist kiểm tra

- [ ] Bảng `BrandWatches` có 10 dòng; `GET :8082/api/brands` → watchCount Rolex 2, Omega 2, Seiko 2, Casio 3, TAG Heuer 1
- [ ] `PUT :8082/internal/brands/1/watches/99` **2 lần** → cả 2 lần 200, bảng chỉ có **1** dòng WatchID 99
- [ ] `PUT :8082/internal/brands/999/watches/99` → **404**, body `{"success":false,"message":"Brand not found with id: 999"}`
- [ ] `DELETE :8082/internal/brands/watches/99` **2 lần** → lần 1 `UNASSIGNED`, lần 2 `NOTHING_TO_DO` (đều 200)
- [ ] Console có log `[SAGA-PARTICIPANT] ASSIGN ...` / `UNASSIGN ...`
- [ ] `mvn -q -DskipTests package` thành công

#### 📝 Yêu cầu commit

- Làm trên nhánh **`feature/ms-brand-participant`**, merge `--no-ff` vào `main` khi đạt đủ checklist.
- Tách tối thiểu **3 commit** theo nhóm TODO, mỗi commit build được:
  1. `feat(ms-brand): ...` — `Refs: TODO-5.1, TODO-5.6`
  2. `feat(ms-brand): ...` — `Refs: TODO-5.2, TODO-5.3, TODO-5.4`
  3. `feat(ms-brand): ...` — `Refs: TODO-5.5`

### Bước 6: MSWatch – Saga Orchestrator

Gợi ý cấu trúc package:

```
com.mss301.watch
├── client/BrandServiceClient.java        ← Feign: gọi /internal/brands/** của MSBrand
├── controller/WatchController.java       ← nhận header X-Saga-Fail-After-Step, trả X-Saga-Id
├── controller/SagaController.java        ← GET /api/sagas, /api/sagas/{sagaId}
├── entity/SagaState.java, SagaLog.java   ← trạng thái + nhật ký Saga
├── service/WatchService.java             ← validate nghiệp vụ rồi gọi orchestrator
├── service/WatchLocalService.java        ← các LOCAL TRANSACTION trên DBWatch
├── service/WatchData.java                ← snapshot dữ liệu (dùng để RESTORE)
└── service/saga/
    ├── WatchSagaOrchestrator.java        ← ⭐ trái tim của Saga
    ├── SagaStep.java                     ← (action, compensation), pivot khi compensation = null
    ├── SagaTracker.java                  ← ghi SagaStates/SagaLogs (REQUIRES_NEW)
    ├── SagaFaultInjector.java            ← giả lập lỗi để test
    └── SagaStatus.java ...
```

**Quy tắc bắt buộc của orchestrator:**

1. **Không** đặt `@Transactional` ở orchestrator; mỗi bước là 1 local transaction riêng.
2. Chỉ bước **đã commit** mới được đưa vào stack; khi lỗi, bù trừ theo thứ tự **ngược** (LIFO).
3. Compensation retry tối đa 3 lần (backoff 1s); vẫn lỗi thì Saga dừng ở `COMPENSATING`, **không** báo `COMPENSATED`.
4. Lỗi từ MSBrand (404, mất kết nối) **không** được "nuốt" bằng fallback lưu dữ liệu.
5. Validate rẻ (name, price, releaseDate, category) chạy **trước** khi Saga bắt đầu → không tạo `SagaStates`.
6. Nhật ký Saga (`SagaStates`, `SagaLogs`) ghi bằng transaction riêng (`REQUIRES_NEW`), mỗi bước một dòng `EXECUTE` / `COMPENSATE` / `FAULT`.

#### 🎯 TODO

| Mã | Việc cần làm | File / vị trí |
|---|---|---|
| **TODO-6.1** | yml: Feign timeout (connect 2s, read 5s), `brand-service.url`, `saga.fault-injection.enabled`, `saga.compensation.*` | `application.yml` |
| **TODO-6.2** | Entity `SagaState` (status kiểu enum) + `SagaLog` và 2 repository | `entity/`, `repository/` |
| **TODO-6.3** | `SagaStatus` đủ 6 trạng thái của Slide 27 | `service/saga/SagaStatus.java` |
| **TODO-6.4** | `SagaTracker`: mọi thao tác ghi dùng `@Transactional(propagation = REQUIRES_NEW)` | `service/saga/SagaTracker.java` |
| **TODO-6.5** | `WatchLocalService`: `insert`, `update`, `delete`, `deleteIfExists` (mỗi method 1 local tx) | `service/WatchLocalService.java` |
| **TODO-6.6** | Record `WatchData` làm snapshot `before` / `after` | `service/WatchData.java` |
| **TODO-6.7** | `@EnableFeignClients` + `BrandServiceClient` gọi `/internal/brands/**` | `MSWatchApplication`, `client/` |
| **TODO-6.8** | Record `SagaStep(action, compensation)`; `pivot()` khi không có compensation | `service/saga/SagaStep.java` |
| **TODO-6.9** | `execute()`: chạy tuần tự, **push** bước đã commit vào stack; **không** `@Transactional` | `WatchSagaOrchestrator` |
| **TODO-6.10** | `compensate()` LIFO + `compensateWithRetry()` 3 lần; lỗi hẳn → dừng ở `COMPENSATING` | `WatchSagaOrchestrator` |
| **TODO-6.11** | 3 Saga: `createWatch` (a), `updateWatch` (b), `deleteWatch` (c, pivot cuối) | `WatchSagaOrchestrator` |
| **TODO-6.12** | `SagaFaultInjector` + header `X-Saga-Fail-After-Step`; bỏ qua lỗi giả sau pivot | `service/saga/` |
| **TODO-6.13** | `WatchRequest` (name > 10 ký tự, price ≥ 100, đủ field); `WatchService` validate releaseDate, category **trước** Saga; list mới nhất trước | `dto/`, `service/WatchService.java` |
| **TODO-6.14** | `WatchController` (Admin only, header `X-Saga-Id`), `SagaController` (`/api/sagas`, `/api/sagas/{id}`) | `controller/`, `dto/` |
| **TODO-6.15** | `SagaExecutionException` → HTTP 400/503/500 kèm `sagaId`, `sagaStatus`, `failedStep` | `exception/`, `describe()` |
| **TODO-6.16** | Entity `Watch` (BrandID chỉ là tham chiếu), `WatchCategory`; seed **đúng nguyên văn** đề bài | `entity/`, `repository/`, `DataInitializer.java` |
| **TODO-6.17** | Bean `feign.Logger.Level.BASIC`; dùng `JsonMapper` (Jackson 3) do Boot cấu hình | `config/AppConfig.java` |

#### ☑️ Checklist kiểm tra

- [ ] `grep -nE "^\s*@Transactional" MSWatch_StudentCode/src/main/java/com/mss301/watch/service/saga/WatchSagaOrchestrator.java` → **không có kết quả**
- [ ] `grep -rn "fallbackMethod" MSWatch_StudentCode/src` → **không có kết quả**
- [ ] Khởi động MSWatch: DBWatch có `Watches` (10 dòng), `WatchCategories` (5 dòng), `SagaStates`, `SagaLogs`
- [ ] Gọi thẳng `POST :8083/api/watches` (header `X-User-Role: 1`) brand 1 → **201**, header `X-Saga-Id` có giá trị
- [ ] Cùng request với `brandId: 999` → **400**, `sagaStatus = COMPENSATED`, `failedStep = ASSIGN_BRAND`
- [ ] `GET :8083/api/sagas/{id}` (header `X-User-Role: 1`) trả đúng thứ tự `EXECUTE ... / COMPENSATE ...`
- [ ] Với header `X-Saga-Fail-After-Step: 2`: log MSBrand có `ASSIGN` rồi `UNASSIGN` cho cùng watch
- [ ] Name ≤ 10 ký tự / price < 100 / releaseDate khác hôm nay → **400** và **không** sinh dòng mới trong `SagaStates`
- [ ] Không có header `X-User-Role: 1` → **403**
- [ ] `mvn -q -DskipTests package` thành công

#### 📝 Yêu cầu commit

- Làm trên nhánh **`feature/ms-watch-saga`**, merge `--no-ff` vào `main` khi đạt đủ checklist.
- Tách tối thiểu **7 commit** theo nhóm TODO, mỗi commit build được:
  1. `feat(ms-watch): ...` — `Refs: TODO-6.16`
  2. `build(ms-watch): ...` — `Refs: TODO-6.1, TODO-6.17`
  3. `feat(ms-watch): ...` — `Refs: TODO-6.2, TODO-6.3, TODO-6.4`
  4. `feat(ms-watch): ...` — `Refs: TODO-6.5, TODO-6.6`
  5. `feat(ms-watch): ...` — `Refs: TODO-6.7`
  6. `feat(ms-watch): ...` — `Refs: TODO-6.8, TODO-6.9, TODO-6.10, TODO-6.11, TODO-6.12`
  7. `feat(ms-watch): ...` — `Refs: TODO-6.13, TODO-6.14, TODO-6.15`

### Bước 7: API Gateway

Yêu cầu: route theo bảng ở mục 3.2 (prefix `spring.cloud.gateway.server.webflux.routes`), mỗi route có CircuitBreaker + fallback, TimeLimiter 15s, **không** route `/internal/**`.

Thử tấn công giả mạo quyền: lệnh dưới phải bị từ chối.

```bash
curl -X DELETE http://localhost:8080/api/watches/1 -H "X-User-Role: 1"
# Kết quả đúng: 401 Unauthorized
```

#### 🎯 TODO

| Mã | Việc cần làm | File / vị trí |
|---|---|---|
| **TODO-7.1** | Khai báo route dưới `spring.cloud.gateway.server.webflux.routes`: `/api/auth/**`, `/api/brands/**`, `/api/watches/**` | `application.yml` |
| **TODO-7.2** | Route watch-service thêm `/api/sagas/**`; **không** route `/internal/**`; CircuitBreaker + `FallbackController` | `application.yml`, `fallback/` |
| **TODO-7.3** | Luôn xoá `X-User-Id`, `X-User-Role` do client gửi lên | `JwtAuthFilter.java` |
| **TODO-7.4** | Public chỉ gồm login, refresh, fallback và **`GET /api/watches`** | `JwtAuthFilter.java` |
| **TODO-7.5** | Verify chữ ký + hạn JWT; từ chối token có `type != access`; gắn `X-User-Id`, `X-User-Role` | `JwtAuthFilter.java` |
| **TODO-7.6** | TimeLimiter `15s` cho accountCB/brandCB/watchCB | `application.yml` |

#### ☑️ Checklist kiểm tra

- [ ] `GET :8080/api/watches` không token → **200**
- [ ] `GET :8080/api/brands` không token → **401**
- [ ] `DELETE :8080/api/watches/1` kèm `X-User-Role: 1`, không token → **401**
- [ ] Token staff02 + header `X-User-Role: 1` → **403** (header giả bị thay bằng role 2 từ JWT)
- [ ] Dùng refreshToken làm Bearer → **401**
- [ ] `PUT :8080/internal/brands/1/watches/1` → **404** (không có route)
- [ ] `GET :8080/api/sagas` với token admin → **200**
- [ ] Tắt MSBrand rồi `GET :8080/api/brands` → **503** từ `FallbackController`

#### 📝 Yêu cầu commit

- Làm trên nhánh **`feature/gateway`**, merge `--no-ff` vào `main` khi đạt đủ checklist.
- Tách tối thiểu **2 commit** theo nhóm TODO, mỗi commit build được:
  1. `feat(gateway): ...` — `Refs: TODO-7.1, TODO-7.2, TODO-7.6`
  2. `feat(gateway): ...` — `Refs: TODO-7.3, TODO-7.4, TODO-7.5`

### Bước 8: Chạy hệ thống

Thứ tự chạy trong IntelliJ: **MSAccount → MSBrand → MSWatch → APIGateway**.

Kiểm tra nhanh:

```http
GET http://localhost:8082/api/brands/1/watches     → watchIds [1, 8]
GET http://localhost:8080/api/watches              → 10 watch, có categoryName
```

Swagger UI: `http://localhost:8081/swagger-ui.html`, `:8082/swagger-ui.html`, `:8083/swagger-ui.html`.

#### 🎯 TODO

| Mã | Việc cần làm | File / vị trí |
|---|---|---|
| **TODO-8.1** | Chạy đúng thứ tự MSAccount → MSBrand → MSWatch → APIGateway | IntelliJ |
| **TODO-8.2** | Smoke test qua Gateway: login, list watches, list brands | Postman |

#### ☑️ Checklist kiểm tra

- [ ] 4 service khởi động không lỗi, đúng cổng 8081/8082/8083/8080
- [ ] `GET :8080/api/watches` trả 10 watch, mỗi watch có `categoryName`
- [ ] `GET :8082/api/brands/1/watches` → `watchIds: [1, 8]`
- [ ] Swagger UI mở được ở cả 3 service

#### 📝 Yêu cầu commit

> Bước này chỉ kiểm tra, **không có commit**.

### Bước 9: Kiểm thử chứng minh Saga

Xem chi tiết các kịch bản và kết quả mong đợi ở **mục 6**.

#### 🎯 TODO

| Mã | Việc cần làm | File / vị trí |
|---|---|---|
| **TODO-9.1** | Import và chạy Postman collection theo thứ tự; tất cả test **PASS** | `WatchManagement_Saga.postman_collection.json` |
| **TODO-9.2** | Chụp màn hình *Run results* + Console của folder 04, 05, 06, 07 | báo cáo |
| **TODO-9.3** | Kịch bản thủ công: tắt MSBrand (mục 6.3) | IntelliJ + Postman |
| **TODO-9.4** | Kịch bản nâng cao: compensation thất bại → `COMPENSATING` (mục 6.4) | Debug mode |
| **TODO-9.5** | Chạy query đối chiếu chéo sau mỗi kịch bản → 0 dòng | SSMS |

#### ☑️ Checklist kiểm tra

- [ ] Collection Runner: **0 failed**
- [ ] Kịch bản B: WatchID bị "nhảy cóc" (bằng chứng watch đã INSERT rồi mới bị xoá)
- [ ] Kịch bản C: trong saga log, `UNASSIGN_BRAND` đứng **trước** `DELETE_WATCH`
- [ ] Kịch bản G: có dòng `FAULT FAULT_INJECTION SKIPPED`, status `COMPLETED`
- [ ] Kịch bản 6.3: HTTP **503**, `reason` chứa `MSBrand is unreachable`
- [ ] Kịch bản 6.4: 3 lần `COMPENSATE UNASSIGN_BRAND FAILED` rồi `COMPENSATION_HALTED`
- [ ] Query đối chiếu 6.5 trả **0 dòng** sau mọi kịch bản

#### 📝 Yêu cầu commit

- Làm trên nhánh **`test/saga-proof`**, merge `--no-ff` vào `main` khi đạt đủ checklist.
- Tách tối thiểu **1 commit** theo nhóm TODO, mỗi commit build được:
  1. `test(postman): ...` — `Refs: TODO-9.1`

### Bước 10: Docker

```bash
cd WatchManagement
docker compose --env-file .env up --build -d
docker compose ps
docker compose logs -f ms-watch
docker compose down          # thêm -v để xoá cả volume dữ liệu (reset DB)
```

- Biến `SAGA_FAULT_INJECTION` mặc định `true` (thêm `SAGA_FAULT_INJECTION=false` vào `.env` để tắt).
- Service `db-init` tạo DBAccount, DBBrand, DBWatch rồi thoát; các service chỉ khởi động sau khi nó chạy xong.
- Trong container, MSWatch gọi MSBrand qua `http://ms-brand:8082` (tên service), không phải `localhost`.
- Muốn reset dữ liệu để chạy lại Postman từ đầu: `docker compose down -v`.

#### 🎯 TODO

| Mã | Việc cần làm | File / vị trí |
|---|---|---|
| **TODO-10.1** | Dockerfile multi-stage (maven build → temurin 21 JRE) cho 4 service; `sqlserver` có healthcheck `mssql-tools18/bin/sqlcmd -C` | 4 × `Dockerfile`, `docker-compose.yml` |
| **TODO-10.2** | Service `db-init` tạo 3 database; các service `depends_on: service_completed_successfully` | `docker-compose.yml` |
| **TODO-10.3** | Truyền biến môi trường: `DB_*`, `JWT_*`, `BRAND_SERVICE_URL`, `SAGA_FAULT_INJECTION` (mặc định `true`) | `docker-compose.yml` |

#### ☑️ Checklist kiểm tra

- [ ] `docker compose ps`: `sqlserver` **healthy**, `db-init` **exited (0)**, 4 service **running**
- [ ] `docker compose logs ms-brand` có `Seeded 10 brand-watch links`
- [ ] Chạy lại Postman collection với `baseUrl = http://localhost:8080` → 0 failed
- [ ] `docker compose down -v && docker compose up -d` → dữ liệu được seed lại từ đầu

#### 📝 Yêu cầu commit

- Làm trên nhánh **`chore/docker`**, merge `--no-ff` vào `main` khi đạt đủ checklist.
- Tách tối thiểu **2 commit** theo nhóm TODO, mỗi commit build được:
  1. `build(docker): ...` — `Refs: TODO-10.1`
  2. `build(docker): ...` — `Refs: TODO-10.1, TODO-10.2, TODO-10.3`

---

## 6. Kiểm thử chứng minh Saga

> **Nguyên tắc chứng minh:** với mỗi kịch bản phải thấy được **3 bằng chứng**:
> 1. **Response**: HTTP status + `sagaStatus`.
> 2. **Nhật ký Saga** (`GET /api/sagas/{sagaId}`): đúng các bước EXECUTE/COMPENSATE và đúng **thứ tự**.
> 3. **Dữ liệu 2 phía khớp nhau**: DBWatch (`GET /api/watches`) và DBBrand (`GET /api/brands/{id}/watches`).

### 6.1. Chạy Postman Collection (tự động)

1. Postman → **Import** → `WatchManagement/WatchManagement_Saga.postman_collection.json`.
2. Đảm bảo DB vừa được tạo mới và 4 service + Gateway đang chạy.
3. Chuột phải collection → **Run collection** → chạy **theo đúng thứ tự** (các request dùng chung biến `newWatchId`, `sagaId`, ...).
4. Kết quả mong đợi: **tất cả test PASS**. Mở tab *Console* để xem chuỗi bước của từng Saga.

| Folder | Nội dung | Chứng minh điều gì |
|---|---|---|
| 00 | Login admin, staff | Lấy token |
| 01 | 401 / 403 / inactive / refresh / giả mạo role | JWT + phân quyền |
| 02 | Name, Price, ReleaseDate sai | Validate **trước** Saga → không tạo SagaState |
| 03 | CREATE thành công | 1 request cập nhật **2 database**; watch mới ở đầu list |
| 04 | CREATE với brand 999 | Bước 1 đã commit bị **DELETE_WATCH** bù trừ |
| 05 | CREATE + lỗi sau bước 2 | MSBrand **đã ghi** rồi được **UNASSIGN_BRAND** hoàn tác; thứ tự **LIFO** |
| 06 | UPDATE thành công / brand 999 / lỗi sau bước 2 | RESTORE từ snapshot; ASSIGN_BRAND_BACK |
| 07 | DELETE + lỗi sau bước 1 / sau bước 2 | Compensation phía MSBrand; **pivot** không thể quay lui |
| 08 | `/api/sagas` | Monitoring, chỉ Admin |

### 6.2. Bảng kết quả mong đợi chi tiết

Các nhật ký dưới đây lấy từ `GET /api/sagas/{sagaId}` → `data.steps` (định dạng `phase stepName result`).

**Kịch bản A – CREATE thành công (brand 1)**

```
EXECUTE CREATE_WATCH SUCCESS
EXECUTE ASSIGN_BRAND SUCCESS
→ status COMPLETED ; brand 1: watchCount 2 → 3
```

**Kịch bản B – CREATE với brandId = 999**

```
EXECUTE CREATE_WATCH  SUCCESS      ← watch đã INSERT (có WatchID)
EXECUTE ASSIGN_BRAND  FAILED       ← MSBrand 404
COMPENSATE DELETE_WATCH SUCCESS    ← xoá watch vừa INSERT
→ HTTP 400 ; status COMPENSATED ; GET /api/watches không có watch đó
```

**Kịch bản C – CREATE + `X-Saga-Fail-After-Step: 2`**

```
EXECUTE CREATE_WATCH   SUCCESS
EXECUTE ASSIGN_BRAND   SUCCESS     ← DBBrand ĐÃ COMMIT
FAULT   FAULT_INJECTION TRIGGERED
COMPENSATE UNASSIGN_BRAND SUCCESS  ← bù trừ bước 2 TRƯỚC
COMPENSATE DELETE_WATCH   SUCCESS  ← rồi mới tới bước 1
→ HTTP 500 ; COMPENSATED ; watchCount của brand 1 KHÔNG đổi
```

**Kịch bản D – UPDATE sang brand 999**

```
EXECUTE UPDATE_WATCH SUCCESS
EXECUTE ASSIGN_BRAND FAILED
COMPENSATE RESTORE_WATCH SUCCESS   ← name, price, brandId... trở về giá trị cũ
```

**Kịch bản E – UPDATE brand 2 → 3 + `X-Saga-Fail-After-Step: 2`**

```
EXECUTE UPDATE_WATCH SUCCESS
EXECUTE ASSIGN_BRAND SUCCESS          ← watch đã chuyển sang brand 3 ở DBBrand
FAULT   FAULT_INJECTION TRIGGERED
COMPENSATE ASSIGN_BRAND_BACK SUCCESS  ← gán lại brand 2
COMPENSATE RESTORE_WATCH SUCCESS
→ brand 2 vẫn chứa watch ; brand 3 không chứa
```

**Kịch bản F – DELETE + `X-Saga-Fail-After-Step: 1`**

```
EXECUTE UNASSIGN_BRAND SUCCESS
FAULT   FAULT_INJECTION TRIGGERED
COMPENSATE ASSIGN_BRAND_BACK SUCCESS
→ watch vẫn còn ; brand vẫn chứa watch
```

**Kịch bản G – DELETE + `X-Saga-Fail-After-Step: 2` (pivot)**

```
EXECUTE UNASSIGN_BRAND SUCCESS
EXECUTE DELETE_WATCH   SUCCESS     ← pivot đã commit
FAULT   FAULT_INJECTION SKIPPED    ← không thể quay lui → Saga phải đi tiếp
→ HTTP 200 ; COMPLETED
```

### 6.3. Kịch bản thủ công: MSBrand bị tắt (network failure)

1. **Stop** MSBrand (IntelliJ: nút Stop).
2. Tạo watch mới với brand 1 (qua Gateway, token admin).
3. Kết quả: **HTTP 503**, `reason: "MSBrand is unreachable: Connection refused ..."`, `sagaStatus: COMPENSATED`.
4. Saga log: `EXECUTE CREATE_WATCH SUCCESS` → `EXECUTE ASSIGN_BRAND FAILED` → `COMPENSATE DELETE_WATCH SUCCESS`.
5. Thử **DELETE** watch 3 khi MSBrand vẫn tắt: HTTP 503, saga log chỉ có `EXECUTE UNASSIGN_BRAND FAILED`, không có gì cần bù trừ, watch 3 **vẫn còn**.
6. Bật lại MSBrand, chạy query đối chiếu ở mục 6.5 → 0 dòng lệch.


### 6.4. Kịch bản nâng cao: compensation cũng thất bại

Kịch bản này dùng để giải thích trạng thái `COMPENSATING` "kẹt".

1. Chạy MSWatch ở chế độ **Debug**, đặt breakpoint ngay **trước** chỗ orchestrator bắt đầu chạy compensation (sau khi đã ghi `FAILED`).
2. Gửi `POST /api/watches` (brand 1) kèm header `X-Saga-Fail-After-Step: 2`.
3. Khi dừng ở breakpoint: **stop MSBrand**, rồi *Resume*.
4. Kết quả: 3 dòng `COMPENSATE UNASSIGN_BRAND FAILED` (Attempt 1/3, 2/3, 3/3) → `COMPENSATION_HALTED`; response 500 với `sagaStatus: COMPENSATING`.
5. Lúc này watch **vẫn còn** ở DBWatch và link **vẫn còn** ở DBBrand: Saga dừng lại thay vì xoá watch rồi để link "mồ côi" bên MSBrand.
6. **Xử lý thủ công** (sau khi bật lại MSBrand): gọi `DELETE http://localhost:8082/internal/brands/watches/{watchId}`, rồi xoá watch. Trong hệ thống thật, việc này do một job *saga recovery* đảm nhận (xem câu hỏi vấn đáp số 8).

### 6.5. Bằng chứng ở mức database

Saga log và trạng thái:

```sql
USE DBWatch;
SELECT TOP 10 SagaId, SagaType, WatchID, Status, CurrentStep, FailureReason, CreatedAt
FROM SagaStates ORDER BY id DESC;

SELECT StepNo, StepName, Phase, Result, Message, CreatedAt
FROM SagaLogs WHERE SagaId = '<sagaId>' ORDER BY id;
```

**Query đối chiếu chéo 2 database** (chỉ dùng để kiểm chứng; các service **không bao giờ** truy cập DB của nhau). Kết quả phải là **0 dòng**:

```sql
SELECT w.WatchID  AS WatchInDBWatch,  w.BrandID  AS BrandInDBWatch,
       bw.WatchID AS WatchInDBBrand,  bw.BrandID AS BrandInDBBrand
FROM DBWatch.dbo.Watches w
FULL OUTER JOIN DBBrand.dbo.BrandWatches bw ON w.WatchID = bw.WatchID
WHERE w.WatchID IS NULL            -- MSBrand còn link tới watch đã bị xoá
   OR bw.WatchID IS NULL           -- watch tồn tại nhưng MSBrand không biết
   OR w.BrandID <> bw.BrandID;     -- hai bên lệch brand
```

Chạy query này sau mỗi kịch bản (A → G, và cả 6.3). Ngoại lệ duy nhất là kịch bản 6.4: Saga đang `COMPENSATING`, query vẫn ra 0 dòng vì Saga dừng lại khi cả hai phía còn khớp nhau.

### 6.6. Bằng chứng ở log console

MSWatch (Feign BASIC log + log orchestrator):

```
[SAGA 3f2b...] step 1 CREATE_WATCH -> SUCCESS
---> PUT http://localhost:8082/internal/brands/999/watches/11 HTTP/1.1
<--- HTTP/1.1 404 (12ms)
[SAGA 3f2b...] FAILED at ASSIGN_BRAND: MSBrand returned 404: Brand not found with id: 999
[SAGA 3f2b...] compensate step 1 DELETE_WATCH -> SUCCESS
[SAGA 3f2b...] finished with status COMPENSATED
```

MSBrand:

```
[SAGA-PARTICIPANT] ASSIGN watch=12 -> brand=1 (previous brand=null)
[SAGA-PARTICIPANT] UNASSIGN watch=12 from brand=1
```

---

## 7. Definition of Done

**Chức năng (theo đề bài)**
- [ ] (1) `GET /api/watches` không cần quyền, có `categoryName`, watch mới nhất ở đầu
- [ ] (2) Admin xoá watch → MSBrand gỡ watch tương ứng (Saga DELETE)
- [ ] (3) Admin thêm watch: đủ field, price ≥ 100, name > 10 ký tự, releaseDate = hôm nay → MSBrand gán watch (Saga CREATE)
- [ ] (4) Admin sửa watch với cùng ràng buộc → MSBrand chuyển brand (Saga UPDATE)
- [ ] (5) Postman script: Gateway + 3 service, **0 failed**

**Saga**
- [ ] Orchestrator không có `@Transactional`; mỗi bước là 1 local transaction
- [ ] Compensation chạy LIFO, idempotent, có retry; lỗi hẳn thì dừng ở `COMPENSATING`
- [ ] `SagaStates` + `SagaLogs` ghi đủ các bước; `/api/sagas/{id}` xem được
- [ ] Chứng minh được 7 kịch bản A–G + 6.3; query đối chiếu 6.5 trả 0 dòng

**Kỹ thuật**
- [ ] Spring Boot 4.1.1, Spring Cloud 2025.1.3; cả 4 service `mvn package` thành công
- [ ] Gateway chặn giả mạo `X-User-Role`; `/internal/**` không lộ ra ngoài
- [ ] Mỗi TODO về code (Bước 0–3, 5–7, 10) được đánh dấu bằng comment `// [TODO-x.y]` tại chỗ giải quyết; `grep -rn "\[TODO-" .` liệt kê đủ

**Git**
- [ ] Mọi commit đúng Conventional Commits, có `Refs: TODO-x.y`
- [ ] Không có commit chứa `.env`, `target/`, `.idea/`
- [ ] Mỗi nhánh feature được merge `--no-ff`; gắn tag `v1.0.0` cho bản nộp

---

## 8. Câu hỏi vấn đáp

1. Nếu đặt `@Transactional` lên `WatchSagaOrchestrator.createWatch()`, khi `ASSIGN_BRAND` lỗi thì điều gì xảy ra với DBWatch, DBBrand và bảng `SagaLogs`? *(Gợi ý: SagaTracker dùng `REQUIRES_NEW`.)*
2. Vì sao compensation phải chạy theo thứ tự **ngược**? Cho ví dụ cụ thể với kịch bản C.
3. Trong kịch bản B, vì sao không gọi `UNASSIGN_BRAND`?
4. Vì sao `DELETE_WATCH` là pivot và được đặt **cuối** saga xoá? Nếu đảo thứ tự (xoá watch trước, gỡ brand sau) thì compensation sẽ khó ở chỗ nào?
5. Vì sao `assignWatch` / `unassignWatch` phải idempotent? Điều gì xảy ra khi retry nếu chúng không idempotent?
6. Saga đảm bảo thuộc tính nào của ACID và đánh đổi thuộc tính nào? *(Gợi ý: trong lúc Saga đang chạy, `GET /api/watches` có thể thấy watch chưa được gán brand, tức là thiếu Isolation.)*
7. Nếu `ASSIGN_BRAND` bị **read timeout** nhưng thực ra MSBrand đã commit thì orchestrator xử lý thế nào? Có cách nào an toàn hơn? *(Gợi ý: vì compensation idempotent, có thể push compensation vào stack **trước** khi gọi.)*
8. Saga dừng ở `COMPENSATING` thì ai xử lý? Thiết kế một job `@Scheduled` để tự khôi phục dựa vào `SagaStates.Payload`.
9. So sánh Orchestration (bài này) với Choreography (Kafka event). Khi nào nên chọn cái nào?
10. Vì sao MSWatch không dùng fallback của Circuit Breaker nhưng Gateway vẫn dùng Circuit Breaker?

---
