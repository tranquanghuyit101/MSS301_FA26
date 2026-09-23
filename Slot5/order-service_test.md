# Testing Order Service bằng Postman

> Dựa trên `order-service.md`. Áp dụng cho service `order-service` (package `com.fudn.orderservice`).
> **Base URL:** `http://localhost:8081` | **Endpoint:** `POST /api/order`

---

## 0. Checklist chuẩn bị trước khi test

- [x] Docker container `mysql` đang chạy (`docker ps` thấy container `mysql` status `Up`)
- [x] Database `order_service` đã tồn tại (kiểm tra qua DBeaver/Adminer/CLI)
- [x] `order-service` đã chạy thành công (`mvn spring-boot:run`), log không có lỗi Flyway
- [x] Log xác nhận Flyway đã áp dụng `V1__init.sql` (dòng `Successfully applied 1 migration`)
- [x] Bảng `t_orders` đã tồn tại (rỗng, chưa có dữ liệu)
- [x] Postman đã cài đặt, đã mở ứng dụng

---

## 1. Cấu hình Postman

### 1.1. Tạo Environment

Tạo 1 Environment tên `order-service-local` với biến:

| Variable | Initial Value | Current Value |
|---|---|---|
| `order_base_url` | `http://localhost:8081` | `http://localhost:8081` |

### TODO
- [x] Tạo Environment `order-service-local`
- [x] Thêm biến `order_base_url`
- [x] Chọn Environment này trước khi gửi request

### 1.2. Tạo Collection

Tạo 1 Collection tên `Order Service` để chứa các request bên dưới (đã export sẵn ra file `Order_Service.postman_collection.json`).

### TODO
- [x] Tạo Collection `Order Service`

---

## 2. Test Case 1 – Đặt hàng thành công (Happy path)

**Request:**
```
POST {{order_base_url}}/api/order
Content-Type: application/json

{
  "skuCode": "iphone_15",
  "price": 1000,
  "quantity": 1
}
```

**Kết quả kỳ vọng:**
| Tiêu chí | Giá trị mong đợi |
|---|---|
| Status Code | `201 Created` |
| Body | `"Order Placed Successfully"` (raw text, không phải JSON) |
| Header `Content-Type` | `text/plain` |

**Postman Test Script (tab Tests):**
```javascript
pm.test("Status code is 201", function () {
    pm.response.to.have.status(201);
});

pm.test("Response body is correct message", function () {
    pm.expect(pm.response.text()).to.eql("Order Placed Successfully");
});
```

### TODO
- [x] Tạo request `POST Create Order - Success` trong Collection
- [x] Gửi request, xác nhận status 201
- [x] Xác nhận body đúng message
- [x] Kiểm tra dữ liệu đã lưu vào bảng `t_orders` (qua DBeaver/Adminer): có `order_number` dạng UUID tự sinh

---

## 3. Test Case 2 – Đặt hàng với số lượng lớn

**Request:**
```
POST {{order_base_url}}/api/order
Content-Type: application/json

{
  "skuCode": "pixel_8",
  "price": 899.99,
  "quantity": 5
}
```

**Kết quả kỳ vọng:** `201 Created`, body `"Order Placed Successfully"`

### TODO
- [x] Gửi request, xác nhận 201
- [x] Kiểm tra `price` lưu đúng dạng decimal (899.99) trong DB, không bị làm tròn

---

## 4. Test Case 3 – Thiếu field bắt buộc (thiếu `skuCode`)

**Request:**
```
POST {{order_base_url}}/api/order
Content-Type: application/json

{
  "price": 1000,
  "quantity": 1
}
```

**Kết quả thực tế (theo code hiện tại):** Vì `OrderController`/`OrderService` **chưa có validation** (`@Valid`, `@NotNull`...), request này vẫn trả về `201 Created` nhưng `sku_code` sẽ được lưu là `null` trong DB.

> ⚠️ **Đây là lỗ hổng cần ghi nhận:** Part 1 của tutorial chưa xử lý validate input. Đây là điểm có thể cải tiến (thêm `@Valid` + `@NotBlank` vào `OrderRequest`, và `@ExceptionHandler` để trả về `400 Bad Request` khi thiếu field).

### TODO
- [x] Gửi request thiếu `skuCode`, ghi nhận kết quả thực tế
- [x] Kiểm tra trong DB xem `sku_code` có bị lưu `null` không
- [ ] (Tùy chọn – nâng cao) Đề xuất thêm validation, viết lại test case kỳ vọng `400 Bad Request`

---

## 5. Test Case 4 – Sai kiểu dữ liệu (`quantity` là chuỗi thay vì số)

**Request:**
```
POST {{order_base_url}}/api/order
Content-Type: application/json

{
  "skuCode": "galaxy_24",
  "price": 1000,
  "quantity": "abc"
}
```

**Kết quả kỳ vọng:** `400 Bad Request` (Spring tự trả lỗi vì không parse được `"abc"` thành `Integer` khi deserialize JSON — lỗi này xảy ra ở tầng Jackson, trước khi vào Controller).

**Postman Test Script:**
```javascript
pm.test("Status code is 400 for invalid quantity type", function () {
    pm.response.to.have.status(400);
});
```

### TODO
- [x] Gửi request với `quantity` sai kiểu
- [x] Xác nhận status 400
- [x] Đọc response body để hiểu message lỗi Jackson trả về

---

## 6. Test Case 5 – Thiếu `Content-Type` header

**Request:** giống Test Case 1 nhưng **không** set header `Content-Type: application/json`.

**Kết quả kỳ vọng:** `415 Unsupported Media Type` hoặc Postman tự động set Content-Type khi chọn body type là `raw` + `JSON` (nên cần chủ động bỏ/đổi header để test đúng).

### TODO
- [x] Trong tab Headers, xóa dòng `Content-Type`
- [x] Gửi lại request, quan sát status code (415)

---

## 7. Test Case 6 – Body rỗng

**Request:**
```
POST {{order_base_url}}/api/order
Content-Type: application/json

{}
```

**Kết quả kỳ vọng:** `201 Created` (do chưa có validation) nhưng toàn bộ field `sku_code`, `price`, `quantity` đều `null` trong DB.

### TODO
- [x] Gửi request body rỗng `{}`
- [x] Ghi nhận kết quả thực tế, so sánh với kỳ vọng "nên có validation"

---

## 8. Test Case 7 – Endpoint sai method (GET thay vì POST)

**Request:**
```
GET {{order_base_url}}/api/order
```

**Kết quả kỳ vọng:** `405 Method Not Allowed` (vì Controller chỉ định nghĩa `@PostMapping`, không có `@GetMapping`)

### TODO
- [x] Đổi method sang GET, gửi request
- [x] Xác nhận status 405

---

## 9. Test Case 8 – Sai đường dẫn URL

**Request:**
```
POST {{order_base_url}}/api/orders
```
*(cố tình gõ sai, thêm `s`)*

**Kết quả kỳ vọng:** `404 Not Found`

### TODO
- [x] Gửi request với path sai
- [x] Xác nhận status 404

---

## ✅ Checklist tổng hợp kết quả test Order Service

| # | Test case | Method | Status kỳ vọng | Đạt? |
|---|---|---|---|---|
| 1 | Đặt hàng hợp lệ | POST | 201 | [x] Đạt |
| 2 | Đặt hàng số lượng lớn, giá thập phân | POST | 201 | [x] Đạt |
| 3 | Thiếu `skuCode` | POST | 201 (hiện tại) / nên là 400 | [x] Đạt (đã lưu null) |
| 4 | Sai kiểu `quantity` | POST | 400 | [x] Đạt |
| 5 | Thiếu `Content-Type` | POST | 415 | [x] Đạt |
| 6 | Body rỗng | POST | 201 (hiện tại) / nên là 400 | [x] Đạt (đã lưu null) |
| 7 | Sai method (GET) | GET | 405 | [x] Đạt |
| 8 | Sai path | POST | 404 | [x] Đạt |

- [x] Export Postman Collection ra file `.json` để lưu lại (`Order_Service.postman_collection.json`)
- [x] Ghi lại kết quả thực tế của từng test case (chụp màn hình hoặc note) để nộp bài/báo cáo
- [x] Đối chiếu dữ liệu cuối cùng trong bảng `t_orders` qua DBeaver/Adminer khớp với các request đã gửi thành công

---

## Ghi chú

- Vì `Order` chưa có validation ở Part 1, các test case 3 và 6 chỉ mang tính **ghi nhận hành vi hiện tại**, không phải lỗi của bạn khi code theo đúng hướng dẫn — đây là điểm sẽ được cải thiện ở các Part sau hoặc khi bạn tự nâng cấp thêm `@Valid`.
- Muốn test tự động hóa: có thể dùng **Postman Collection Runner** để chạy toàn bộ Test Case 1–8 liên tiếp, hoặc export Collection sang **Newman** (CLI runner của Postman) để chạy trong CI/CD.
