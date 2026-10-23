# BÁO CÁO HƯỚNG DẪN KIỂM THỬ VÀ KẾT QUẢ CHẠY SAGA PATTERN (ORCHESTRATION)

> **Môn học:** MSS301 – Microservices Architecture (Slot 13)
> **Stack:** Spring Boot 4.1.1 · Java 21 · Docker Compose · MySQL 8.4 · SQL Server 2022 · MongoDB 8.0

## 1. Bảng tổng hợp các kịch bản kiểm thử (Mục 6.3)

| Kịch bản | Mô tả nghiệp vụ | Bước lỗi | Trạng thái Order/Saga | Failure Reason | Kho & Ví sau KB | Kết quả |
|---|---|---|---|---|---|---|
| KB1 | Happy Path: C1 mua 2 P1 (2000$) | – | CONFIRMED / COMPLETED | null | P1=8, C1=3000 | Passed |
| KB2 | Thanh toán lỗi: C2 mua 1 P1 (1000$) | Payment (402) | CANCELLED / COMPENSATED | 402 - Số dư không đủ... | P1=8, C2=100 | Passed |
| KB3 | Hết hàng: C1 mua 100 P2 (2000$) | Inventory (409) | CANCELLED / COMPENSATED | 409 - Không đủ hàng... | P2=5, C1=3000 | Passed |
| KB4 | Sản phẩm không tồn tại: C1 mua P9 | Inventory (404) | CANCELLED / COMPENSATED | 404 - Không tìm thấy... | P1=8, P2=5, C1=3000 | Passed |
| KB5 | Ví không tồn tại: C9 mua P2 (20$) | Payment (404) | CANCELLED / COMPENSATED | 404 - Không tìm thấy ví... | P2=5, C1=3000 | Passed |
| KB6 | payment-service bị tắt (network down) | Network (I/O) | CANCELLED / COMPENSATED | Service không phản hồi... | P2=5 (trừ rồi trả lại) | Passed |
| KB7 | Kiểm tra tính Idempotent (gọi lặp lại) | – | RELEASED, RESERVED, PAID | – | Kho & ví giữ nguyên | Passed |
| KB8 | Compensation cũng bị lỗi (network down) | Comp. Lỗi | PENDING / COMPENSATING | Service không phản hồi... | P2=4 (treo, chờ khôi phục) | Passed |

---

## 2. Hướng dẫn kiểm thử Step-by-Step và Kết quả thực tế

### 2.1. Kịch bản KB1 – Happy Path (Đặt hàng thành công)

**Mục tiêu:** Khách hàng `C1` mua 2 sản phẩm `P1` (Laptop, 1000$/chiếc, tổng 2000$). Kho P1 bị trừ 2 còn 8, ví C1 bị trừ 2000$ còn 3000$.

**Request:**
```http
POST http://localhost:8081/api/orders
Content-Type: application/json

{
  "customerId": "C1",
  "productId": "P1",
  "quantity": 2,
  "amount": 2000.0
}
```

**Response thực tế (HTTP 200):**
```json
{
  "amount": 2000.0,
  "customerId": "C1",
  "failureReason": null,
  "id": 1,
  "productId": "P1",
  "quantity": 2,
  "sagaStatus": "COMPLETED",
  "status": "CONFIRMED"
}
```

**Saga Logs (orderdb.saga_log):**

| ID | Step | Result | Message | Time |
|---|---|---|---|---|
| 1 | CREATE_ORDER | SUCCESS | Order PENDING | 2026-10-23T09:21:27.278146 |
| 2 | RESERVE_INVENTORY | SUCCESS | Đã giữ 2 P1 | 2026-10-23T09:21:27.579643 |
| 3 | PROCESS_PAYMENT | SUCCESS | Đã thu 2000.0 | 2026-10-23T09:21:27.798795 |
| 4 | CONFIRM_ORDER | SUCCESS | Saga COMPLETED | 2026-10-23T09:21:27.834081 |

> **Kết quả:** Tồn kho P1 = 8 (giảm 2), Ví C1 = 3000.0 (giảm 2000$). Saga `COMPLETED`.

### 2.2. Kịch bản KB2 – Thanh toán thất bại (402) → Hoàn tác kho (Compensate Inventory)

**Mục tiêu:** Khách hàng `C2` (chỉ có 100$) mua 1 Laptop `P1` (1000$). Giữ hàng MongoDB thành công, nhưng thanh toán SQL Server trả về `402 PAYMENT_REQUIRED`. Orchestrator chạy hoàn tác (release) trả lại hàng vào kho và CANCEL order.

**Request:**
```http
POST http://localhost:8081/api/orders
Content-Type: application/json

{
  "customerId": "C2",
  "productId": "P1",
  "quantity": 1,
  "amount": 1000.0
}
```

**Response thực tế:**
```json
{
  "amount": 1000.0,
  "customerId": "C2",
  "failureReason": "402 - Số dư không đủ: còn 100.0, cần 1000.0",
  "id": 2,
  "productId": "P1",
  "quantity": 1,
  "sagaStatus": "COMPENSATED",
  "status": "CANCELLED"
}
```

**Saga Logs:**

| ID | Step | Result | Message | Time |
|---|---|---|---|---|
| 5 | CREATE_ORDER | SUCCESS | Order PENDING | 2026-10-23T09:21:28.949325 |
| 6 | RESERVE_INVENTORY | SUCCESS | Đã giữ 1 P1 | 2026-10-23T09:21:29.009741 |
| 7 | SAGA | FAILED | 402 - Số dư không đủ: còn 100.0, cần 1000.0 | 2026-10-23T09:21:29.089897 |
| 8 | COMPENSATION | SUCCESS | Lần thử 1 | 2026-10-23T09:21:29.189482 |
| 9 | CANCEL_ORDER | SUCCESS | Saga COMPENSATED | 2026-10-23T09:21:29.221207 |

> **Kết quả:** Tồn kho P1 giữ nguyên = 8 (trừ tạm rồi cộng lại). Reservation có status = `RELEASED`.

### 2.3. Kịch bản KB3 – Hết hàng (409 CONFLICT)

**Mục tiêu:** Mua 100 chuột `P2` nhưng kho chỉ còn 5. Lỗi ngay tại inventory-service. Không có bước nào cần hoàn tác, Orchestrator hủy order ngay lập tức.

**Response thực tế:**
```json
{
  "amount": 2000.0,
  "customerId": "C1",
  "failureReason": "409 - Không đủ hàng: còn 5, cần 100",
  "id": 3,
  "productId": "P2",
  "quantity": 100,
  "sagaStatus": "COMPENSATED",
  "status": "CANCELLED"
}
```

**Saga Logs:**

| ID | Step | Result | Message | Time |
|---|---|---|---|---|
| 10 | CREATE_ORDER | SUCCESS | Order PENDING | 2026-10-23T09:21:29.836368 |
| 11 | SAGA | FAILED | 409 - Không đủ hàng: còn 5, cần 100 | 2026-10-23T09:21:29.883327 |
| 12 | CANCEL_ORDER | SUCCESS | Saga COMPENSATED | 2026-10-23T09:21:29.937711 |


### 2.4. Kịch bản KB4 – Sản phẩm không tồn tại (404 NOT_FOUND)

**Response thực tế:**
```json
{
  "amount": 10.0,
  "customerId": "C1",
  "failureReason": "404 - Không tìm thấy sản phẩm P9",
  "id": 4,
  "productId": "P9",
  "quantity": 1,
  "sagaStatus": "COMPENSATED",
  "status": "CANCELLED"
}
```

### 2.5. Kịch bản KB5 – Ví không tồn tại (404 NOT_FOUND)

**Response thực tế:**
```json
{
  "amount": 20.0,
  "customerId": "C9",
  "failureReason": "404 - Không tìm thấy ví của C9",
  "id": 5,
  "productId": "P2",
  "quantity": 1,
  "sagaStatus": "COMPENSATED",
  "status": "CANCELLED"
}
```

### 2.6. Kịch bản KB6 – payment-service bị tắt (Lỗi mạng / Network Failure)

**Thao tác:** `docker compose stop payment-service` rồi gửi request.

**Response thực tế:**
```json
{
  "amount": 20.0,
  "customerId": "C1",
  "failureReason": "Service không phản hồi: I/O error on POST request for \"http://payment-service:8083/api/payments/pay\": HTTP connect timed out",
  "id": 6,
  "productId": "P2",
  "quantity": 1,
  "sagaStatus": "COMPENSATED",
  "status": "CANCELLED"
}
```

**Saga Logs:**

| ID | Step | Result | Message | Time |
|---|---|---|---|---|
| 21 | CREATE_ORDER | SUCCESS | Order PENDING | 2026-10-23T09:21:34.764754 |
| 22 | RESERVE_INVENTORY | SUCCESS | Đã giữ 1 P2 | 2026-10-23T09:21:34.80913 |
| 23 | SAGA | FAILED | Service không phản hồi: I/O error on POST request for "http://payment-service:8083/api/payments/pay": HTTP connect timed out | 2026-10-23T09:21:36.834932 |
| 24 | COMPENSATION | SUCCESS | Lần thử 1 | 2026-10-23T09:21:36.976349 |
| 25 | CANCEL_ORDER | SUCCESS | Saga COMPENSATED | 2026-10-23T09:21:37.035109 |


### 2.7. Kịch bản KB7 – Kiểm tra tính Idempotent (Chống trừ/hoàn trùng lặp)

- Gọi lại `release` order 2 (lần 1): `RELEASED`
- Gọi lại `release` order 2 (lần 2): `RELEASED` (kho không cộng thêm)
- Gọi lại `reserve` order 1: status = `RESERVED` (kho không trừ thêm)
- Gọi lại `pay` order 1: status = `PAID` (ví không trừ thêm)
- Gọi `refund` order 2: `REFUNDED` (ví không cộng tiền)

### 2.8. Kịch bản KB8 – Khi bản thân Compensation cũng bị lỗi (Hanging Saga)

**Mục tiêu:** Mô phỏng sự cố khi Payment lỗi nhưng lúc hoàn tác thì Inventory cũng bị sập.

**Cách thực hiện:**
1. Đặt độ trễ 15s: `$env:PAYMENT_DELAY_MS=15000; docker compose up -d order-service`
2. Gửi request đặt hàng: `POST /api/orders` với body `{"customerId": "C1", "productId": "P2", "quantity": 1, "amount": 20.0}`
3. Trong 15s đó, tắt cả 2 service: `docker compose stop payment-service inventory-service`
4. Kết quả nhận được: Order giữ `status: PENDING`, `sagaStatus: COMPENSATING`.
5. Trong saga-logs xuất hiện 3 lần `COMPENSATION FAILED` do RetryTemplate thử lại tối đa 3 lần theo nguyên tắc *Reliable*.

## 3. Kết luận và Đối chiếu Lý thuyết

| Thuộc tính lý thuyết | Thực tế cài đặt trong Source Code & Docker |
|---|---|
| Database-per-service | order (MySQL), inventory (MongoDB), payment (SQL Server) nằm trên 3 container và network độc lập. |
| Chuỗi Local Transactions | Mỗi service thực hiện transaction ACID cục bộ trên database riêng, không phụ thuộc transaction xuyên dịch vụ. |
| Saga Orchestrator | OrderSagaOrchestrator đóng vai trò nhạc trưởng điều phối tuần tự, không gắn @Transactional để tránh lock tài nguyên. |
| Compensating Transactions | Áp dụng ngăn xếp LIFO (ngược thứ tự thực thi). Các hàm release, refund đáp ứng đủ 3 tiêu chí: Idempotent, Reversible, Reliable. |
| Reliable Compensation | Áp dụng RetryTemplate (Spring Framework 7) thử lại tối đa 3 lần. Nếu lỗi, dừng ở trạng thái COMPENSATING để tránh mất mát dữ liệu. |
| State Tracking & Audit Log | Lưu vết từng bước thực thi vào bảng saga_log và enum SagaStatus giúp theo dõi toàn diện tiến trình nghiệp vụ. |
