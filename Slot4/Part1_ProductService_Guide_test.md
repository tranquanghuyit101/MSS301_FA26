# Part 1 — Product Service: Hướng dẫn test Postman theo từng TODO

> Dựa trên `README.md` và `Result_ProductService.md` của bài `product-service` (MSS301).
> Mục tiêu: dùng Postman để kiểm tra 5 TODO (UPDATE, DELETE, và xử lý 404) đã đúng theo tiêu chí chấm điểm.

---

## 0. Tổng quan bài tập

| # | Chức năng | Endpoint | TODO liên quan |
|---|-----------|----------|-----------------|
| Có sẵn | Tạo sản phẩm | `POST /api/products` | — |
| Có sẵn | Liệt kê sản phẩm | `GET /api/products` | — |
| Cần làm | Update sản phẩm | `PUT /api/products/{id}` | TODO 1, TODO 3 |
| Cần làm | Delete sản phẩm | `DELETE /api/products/{id}` | TODO 2, TODO 4 |
| Cần làm | Trả 404 khi không tìm thấy | (cross-cutting) | TODO 5 |

DTO dùng cho request body (`ProductRequest`): `id` (bỏ qua khi gửi), `name` (String), `description` (String), `price` (số, kiểu `BigDecimal`).

Response (`ProductResponse`): `id`, `name`, `description`, `price`.

Base URL mặc định: `http://localhost:8080` (cổng cấu hình trong `application.properties`: `server.port=8080`).

---

## 1. Chuẩn bị môi trường trước khi mở Postman

### Bước 1 — Bật MongoDB bằng Docker
```bash
cd product-service
docker compose up -d
```
Kiểm tra 2 container đã chạy: `mongodb` (cổng 27017) và `mongo-express` (cổng 8081, xem DB bằng UI tại `http://localhost:8081`).

```bash
docker ps
```
Phải thấy cả `mongodb` và `mongo-express` ở trạng thái `Up`.

### Bước 2 — Chạy ứng dụng Spring Boot
```bash
# Windows
mvn spring-boot:run
# macOS/Linux
./mvnw spring-boot:run
```
Đợi log hiện dòng kiểu `Started ProductServiceApplication in ... seconds` và `Tomcat started on port 8080`. Nếu không thấy dòng này mà log dừng lại với lỗi kết nối Mongo → quay lại Bước 1 kiểm tra container `mongodb` đã `Up` chưa.

### Bước 3 — Kiểm tra nhanh server đã sống (tuỳ chọn, không cần Postman)
```bash
curl http://localhost:8080/api/products
```
Nếu trả về `[]` (mảng rỗng) hoặc danh sách JSON → server đã sẵn sàng để test bằng Postman.

---

## 2. Thiết lập Postman ban đầu

### Bước 1 — Tạo Collection
1. Mở Postman → **New** → **Collection**.
2. Đặt tên: `MSS301 - Product Service`.

### Bước 2 — Tạo Environment (biến môi trường)
1. Góc trên phải → **Environments** → **+**.
2. Đặt tên: `Product Service Local`.
3. Thêm 2 biến:

| Variable | Initial value | Current value |
|---|---|---|
| `baseUrl` | `http://localhost:8080` | `http://localhost:8080` |
| `productId` | *(để trống)* | *(để trống)* |

4. **Save**, sau đó ở góc trên phải chọn environment `Product Service Local` để kích hoạt (dropdown "No Environment" → chọn nó).

Dùng biến `{{baseUrl}}` và `{{productId}}` trong toàn bộ các request bên dưới thay vì gõ tay URL/id — vừa nhanh, vừa tránh test sai vì quên đổi id.

---

## 3. Chuẩn bị dữ liệu test — dùng 2 API đã có sẵn

Vì `PUT`/`DELETE` cần một `id` có thật trong DB, ta tạo sản phẩm trước để lấy `id`, và để test script tự động lưu `id` đó vào biến `productId`.

### Request 01 — Create Product
1. Trong Collection, **Add request** → đặt tên `01 - Create Product`.
2. Method: `POST`. URL: `{{baseUrl}}/api/products`.
3. Tab **Headers**: `Content-Type: application/json`.
4. Tab **Body** → chọn `raw` → `JSON`:
```json
{
  "name": "iPhone 15",
  "description": "Apple phone",
  "price": 999.99
}
```
5. Tab **Tests**, dán script sau (tự động kiểm tra và lưu id vào biến môi trường):
```javascript
pm.test("Status is 201 Created", function () {
    pm.response.to.have.status(201);
});

const json = pm.response.json();

pm.test("Response has id, name, description, price", function () {
    pm.expect(json.id).to.be.a("string");
    pm.expect(json.name).to.eql("iPhone 15");
    pm.expect(json.price).to.eql(999.99);
});

pm.environment.set("productId", json.id);
pm.environment.set("productCountBeforeUpdate", null); // reset cho các test sau
```
6. Bấm **Send**.

**Kỳ vọng:** Status `201 Created` (do controller có sẵn `@ResponseStatus(HttpStatus.CREATED)`), body chứa `id`, `name`, `description`, `price`. Tab Test Results (Postman) hiện toàn bộ pass.

> Nếu bước này lỗi (không kết nối được, 500...), dừng lại kiểm tra Mục 1 trước khi tiếp tục — các TODO 1-5 chưa test được nếu API tạo sản phẩm còn lỗi.

### Request 02 — Get All Products (baseline)
1. **Add request** → `02 - Get All Products`.
2. Method: `GET`. URL: `{{baseUrl}}/api/products`.
3. Tab **Tests**:
```javascript
pm.test("Status is 200 OK", function () {
    pm.response.to.have.status(200);
});

const json = pm.response.json();

pm.test("List contains the created product", function () {
    const found = json.find(p => p.id === pm.environment.get("productId"));
    pm.expect(found).to.not.be.undefined;
});

pm.environment.set("productCountBeforeUpdate", json.length);
```
4. **Send**. Kỳ vọng: `200 OK`, sản phẩm vừa tạo có mặt trong danh sách. Ghi nhớ số lượng phần tử hiện tại (script đã lưu vào `productCountBeforeUpdate`) — dùng để kiểm tra TODO 1 không tạo thêm bản ghi mới.

---

## 4. Test TODO 1 + TODO 3 — `PUT /api/products/{id}` (Update)

### 4.1. Test Case A — Update thành công (happy path)

**Request 03 — Update Product (Success)**
1. Method: `PUT`. URL: `{{baseUrl}}/api/products/{{productId}}`.
2. Headers: `Content-Type: application/json`.
3. Body (raw/JSON):
```json
{
  "name": "iPhone 15 Pro",
  "description": "Updated",
  "price": 1199.99
}
```
4. Tab **Tests**:
```javascript
pm.test("Status is 200 OK", function () {
    pm.response.to.have.status(200);
});

const json = pm.response.json();

pm.test("Id stays the same (not a new record)", function () {
    pm.expect(json.id).to.eql(pm.environment.get("productId"));
});

pm.test("Fields are updated", function () {
    pm.expect(json.name).to.eql("iPhone 15 Pro");
    pm.expect(json.description).to.eql("Updated");
    pm.expect(json.price).to.eql(1199.99);
});
```
5. **Send**. Kỳ vọng: `200 OK`, body trả về đúng dữ liệu mới, `id` không đổi.

**Xác nhận dữ liệu thật sự được lưu (chạy lại Request `02 - Get All Products`):**
- Tổng số phần tử trong danh sách phải **bằng** `productCountBeforeUpdate` (không tăng lên) → chứng tỏ code không `new Product()` tạo bản ghi mới (đúng lưu ý trong README/Result).
- Phần tử có `id = productId` phải có `name = "iPhone 15 Pro"` — chứng tỏ update ghi thật vào MongoDB, không chỉ trả JSON giả.
- Có thể xem trực tiếp trong Mongo Express (`http://localhost:8081` → database `product-service` → collection `products`) để đối chiếu bằng mắt.

Thêm script kiểm tra count không đổi vào Request 02 (tuỳ chọn nhưng nên làm), thêm đoạn sau vào cuối tab Tests của `02 - Get All Products` (chạy lại sau update):
```javascript
const before = pm.environment.get("productCountBeforeUpdate");
if (before !== null) {
    pm.test("Product count unchanged after update (no duplicate created)", function () {
        pm.expect(pm.response.json().length).to.eql(Number(before));
    });
}
```

### 4.2. Test Case B — Update với id không tồn tại → phải trả 404 (kiểm tra TODO 5)

**Request 04 — Update Product (Not Found)**
1. Method: `PUT`. URL: `{{baseUrl}}/api/products/id-khong-ton-tai-999`.
2. Headers: `Content-Type: application/json`.
3. Body: bất kỳ JSON hợp lệ, ví dụ:
```json
{
  "name": "Ghost",
  "description": "Should not exist",
  "price": 1.0
}
```
4. Tab **Tests**:
```javascript
pm.test("Status is 404 Not Found", function () {
    pm.response.to.have.status(404);
});

pm.test("Body contains not-found message", function () {
    pm.expect(pm.response.text()).to.include("id-khong-ton-tai-999");
});
```
5. **Send**. Kỳ vọng: `404 Not Found`, message `Khong tim thay san pham voi id: id-khong-ton-tai-999`.

**Nếu thấy `500 Internal Server Error` thay vì `404`:** TODO 5 (`GlobalExceptionHandler`) chưa được tạo hoặc chưa được Spring quét thấy (kiểm tra đúng package `com.fudn.product_service.exception`, có `@RestControllerAdvice`, và đã restart lại app sau khi thêm file).

---

## 5. Test TODO 2 + TODO 4 — `DELETE /api/products/{id}`

### 5.1. Test Case A — Delete thành công

**Request 05 — Delete Product (Success)**
1. Method: `DELETE`. URL: `{{baseUrl}}/api/products/{{productId}}`.
2. Không cần body.
3. Tab **Tests**:
```javascript
pm.test("Status is 204 No Content", function () {
    pm.response.to.have.status(204);
});

pm.test("Body is empty", function () {
    pm.expect(pm.response.text()).to.eql("");
});
```
4. **Send**. Kỳ vọng: `204 No Content`, body rỗng (không phải `200`, trừ khi bài cho phép cả hai — nhưng theo README/Result thì đúng chuẩn là `204`).

**Xác nhận đã xoá thật khỏi DB (chạy lại Request `02 - Get All Products`):**
- `productId` không còn xuất hiện trong danh sách.
- Tổng số phần tử giảm đúng 1 so với trước khi xoá.

Thêm test sau vào tab Tests của Request 02 để tự động kiểm tra sau khi chạy Request 05:
```javascript
pm.test("Deleted product no longer in list", function () {
    const json = pm.response.json();
    const stillThere = json.find(p => p.id === pm.environment.get("productId"));
    pm.expect(stillThere).to.be.undefined;
});
```

### 5.2. Test Case B — Delete id không tồn tại (hoặc id vừa xoá xong) → phải trả 404

**Request 06 — Delete Product (Not Found)**
1. Method: `DELETE`. URL: `{{baseUrl}}/api/products/{{productId}}` (chạy request này **sau** Request 05, id lúc này đã bị xoá nên không còn tồn tại) — hoặc dùng thẳng `id-khong-ton-tai-999`.
2. Tab **Tests**:
```javascript
pm.test("Status is 404 Not Found", function () {
    pm.response.to.have.status(404);
});
```
3. **Send**. Kỳ vọng: `404 Not Found`.

**Lỗi thường gặp:** nếu trả về `204` dù id không tồn tại → code đang gọi thẳng `productRepository.deleteById(id)` mà **không** `existsById` check trước (đúng cảnh báo trong README: "Spring Data `deleteById` không throw nếu id không tồn tại"). Cần sửa lại TODO 2 theo `Result_ProductService.md`.

---

## 6. Kiểm tra riêng TODO 5 — `GlobalExceptionHandler`

TODO 5 không có endpoint riêng, nó chỉ lộ diện qua 2 test case 404 ở trên (4.2 và 5.2). Bảng phân biệt kết quả:

| Hiện tượng khi gọi PUT/DELETE với id sai | Nguyên nhân | Cách sửa |
|---|---|---|
| `500 Internal Server Error` | Chưa tạo `GlobalExceptionHandler`, hoặc file sai package/vị trí | Tạo đúng file tại `exception/GlobalExceptionHandler.java`, package `com.fudn.product_service.exception`, có `@RestControllerAdvice` + `@ExceptionHandler(ProductNotFoundException.class)` + `@ResponseStatus(HttpStatus.NOT_FOUND)` |
| `404 Not Found` | Đúng | — |
| `400 Bad Request` | Thường do body JSON sai định dạng hoặc thiếu header `Content-Type: application/json`, không liên quan TODO 5 | Kiểm tra lại Headers/Body của request |

Sau khi sửa code Java, **phải restart lại ứng dụng** (`Ctrl+C` rồi chạy lại `mvnw spring-boot:run`) trước khi test lại trong Postman — Spring Boot không tự hot-reload theo mặc định.

---

## 7. Quy trình test đầy đủ (đề xuất thứ tự chạy)

Có thể chạy tuần tự từng request, hoặc dùng **Collection Runner** của Postman để chạy tự động cả bộ:

1. Chọn Collection `MSS301 - Product Service` → nút **Run** (hoặc icon "▶" cạnh tên collection).
2. Trong cửa sổ Collection Runner, kéo thứ tự request đúng như dưới đây (Postman chạy theo thứ tự hiển thị trong collection):
   1. `01 - Create Product`
   2. `02 - Get All Products` *(baseline)*
   3. `03 - Update Product (Success)`
   4. `02 - Get All Products` *(chạy lại để xác nhận đã update, không tăng số lượng)* — có thể nhân bản request 02 thành `02b - Get All Products (after update)` để không bị Postman gộp trùng tên trong Runner.
   5. `04 - Update Product (Not Found)`
   6. `05 - Delete Product (Success)`
   7. `02c - Get All Products (after delete)` *(bản sao của 02, xác nhận đã xoá)*
   8. `06 - Delete Product (Not Found)`
3. Chọn Environment `Product Service Local` ở dropdown trong Runner.
4. Bấm **Run MSS301 - Product Service**.
5. Xem kết quả: tất cả các `pm.test(...)` phải hiện dấu ✔ màu xanh. Bất kỳ dấu ✘ nào → đọc tên test bị fail để biết đúng TODO nào còn lỗi.

---

## 8. Đối chiếu với tiêu chí chấm điểm (10 điểm)

| # | Tiêu chí | Điểm | Request Postman kiểm tra | TODO |
|---|---|---|---|---|
| 1 | UPDATE trả về 200 và body chứa dữ liệu mới | 2.0 | `03 - Update Product (Success)` | TODO 1, 3 |
| 2 | UPDATE lưu thật vào DB, không tạo bản ghi mới | 2.0 | `03` + chạy lại `02 - Get All Products` (kiểm tra count không đổi + field đã đổi) | TODO 1 |
| 3 | UPDATE trả 404 khi id không tồn tại | 1.0 | `04 - Update Product (Not Found)` | TODO 1, 5 |
| 4 | DELETE trả 204 khi xoá thành công | 2.0 | `05 - Delete Product (Success)` | TODO 2, 4 |
| 5 | DELETE thật sự xoá khỏi DB | 2.0 | `05` + chạy lại `02 - Get All Products` (kiểm tra id biến mất, count -1) | TODO 2, 4 |
| 6 | DELETE trả 404 khi id không tồn tại | 1.0 | `06 - Delete Product (Not Found)` | TODO 2, 5 |

Nếu cả 6 dòng đều pass trong Postman → cả 5 TODO đã cài đặt đúng.

---

## 9. Lỗi thường gặp khi test bằng Postman (Troubleshooting)

| Triệu chứng | Nguyên nhân khả dĩ | Cách xử lý |
|---|---|---|
| `Could not send request` / `ECONNREFUSED` | App Spring Boot chưa chạy, hoặc sai cổng | Kiểm tra lại Mục 1 Bước 2, đảm bảo log hiện "Tomcat started on port 8080" |
| `500` khi gọi PUT/DELETE với id sai | Thiếu `GlobalExceptionHandler` (TODO 5) | Xem Mục 6 |
| `200` thay vì `204` khi xoá thành công | Thiếu `@ResponseStatus(HttpStatus.NO_CONTENT)` trên method `deleteProduct` (TODO 4) | Thêm annotation, restart app |
| `204` dù id không tồn tại (đáng lẽ phải `404`) | `deleteProduct` gọi thẳng `deleteById` không `existsById` check trước (TODO 2) | Sửa theo `Result_ProductService.md` mục TODO 2 |
| Update xong, `GET /api/products` thấy **2 sản phẩm** thay vì 1 sản phẩm đã đổi tên | `updateProduct` dùng `new Product()` rồi `save` thay vì `findById` rồi sửa field (TODO 1) | Sửa theo `Result_ProductService.md` mục TODO 1 |
| `400 Bad Request` | Thiếu header `Content-Type: application/json`, hoặc JSON body sai cú pháp (thiếu dấu phẩy/ngoặc) | Kiểm tra tab Headers và Body trong Postman |
| Mongo Express (`localhost:8081`) không mở được / không thấy dữ liệu | Container `mongo-express` hoặc `mongodb` chưa `Up` | `docker ps` kiểm tra lại, `docker compose up -d` lại nếu cần |
| `productId` trong Postman bị rỗng ở các request PUT/DELETE | Chưa chạy `01 - Create Product` trước, hoặc environment `Product Service Local` chưa được chọn (Active) | Chạy lại Request 01, kiểm tra dropdown environment góc trên phải Postman |

---

## 10. Phụ lục — Postman Collection JSON (import nhanh, tuỳ chọn)

Có thể bỏ qua Mục 2–3 (tạo tay từng request) bằng cách import file JSON dưới đây thẳng vào Postman: **Import** → **Raw text** → dán → **Continue** → **Import**. Sau đó tạo Environment như Mục 2 Bước 2 và chọn nó trước khi chạy.

```json
{
  "info": {
    "name": "MSS301 - Product Service",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "01 - Create Product",
      "request": {
        "method": "POST",
        "header": [{ "key": "Content-Type", "value": "application/json" }],
        "url": "{{baseUrl}}/api/products",
        "body": {
          "mode": "raw",
          "raw": "{\n  \"name\": \"iPhone 15\",\n  \"description\": \"Apple phone\",\n  \"price\": 999.99\n}"
        }
      },
      "event": [
        {
          "listen": "test",
          "script": {
            "exec": [
              "pm.test(\"Status is 201 Created\", function () { pm.response.to.have.status(201); });",
              "const json = pm.response.json();",
              "pm.test(\"Response has correct fields\", function () { pm.expect(json.id).to.be.a(\"string\"); pm.expect(json.name).to.eql(\"iPhone 15\"); });",
              "pm.environment.set(\"productId\", json.id);"
            ]
          }
        }
      ]
    },
    {
      "name": "02 - Get All Products",
      "request": { "method": "GET", "url": "{{baseUrl}}/api/products" },
      "event": [
        {
          "listen": "test",
          "script": {
            "exec": [
              "pm.test(\"Status is 200 OK\", function () { pm.response.to.have.status(200); });",
              "const json = pm.response.json();",
              "pm.test(\"List contains created product\", function () { pm.expect(json.find(p => p.id === pm.environment.get(\"productId\"))).to.not.be.undefined; });",
              "pm.environment.set(\"productCountBeforeUpdate\", json.length);"
            ]
          }
        }
      ]
    },
    {
      "name": "03 - Update Product (Success)",
      "request": {
        "method": "PUT",
        "header": [{ "key": "Content-Type", "value": "application/json" }],
        "url": "{{baseUrl}}/api/products/{{productId}}",
        "body": {
          "mode": "raw",
          "raw": "{\n  \"name\": \"iPhone 15 Pro\",\n  \"description\": \"Updated\",\n  \"price\": 1199.99\n}"
        }
      },
      "event": [
        {
          "listen": "test",
          "script": {
            "exec": [
              "pm.test(\"Status is 200 OK\", function () { pm.response.to.have.status(200); });",
              "const json = pm.response.json();",
              "pm.test(\"Id unchanged\", function () { pm.expect(json.id).to.eql(pm.environment.get(\"productId\")); });",
              "pm.test(\"Fields updated\", function () { pm.expect(json.name).to.eql(\"iPhone 15 Pro\"); pm.expect(json.price).to.eql(1199.99); });"
            ]
          }
        }
      ]
    },
    {
      "name": "04 - Update Product (Not Found)",
      "request": {
        "method": "PUT",
        "header": [{ "key": "Content-Type", "value": "application/json" }],
        "url": "{{baseUrl}}/api/products/id-khong-ton-tai-999",
        "body": {
          "mode": "raw",
          "raw": "{\n  \"name\": \"Ghost\",\n  \"description\": \"Should not exist\",\n  \"price\": 1.0\n}"
        }
      },
      "event": [
        {
          "listen": "test",
          "script": {
            "exec": [
              "pm.test(\"Status is 404 Not Found\", function () { pm.response.to.have.status(404); });"
            ]
          }
        }
      ]
    },
    {
      "name": "05 - Delete Product (Success)",
      "request": { "method": "DELETE", "url": "{{baseUrl}}/api/products/{{productId}}" },
      "event": [
        {
          "listen": "test",
          "script": {
            "exec": [
              "pm.test(\"Status is 204 No Content\", function () { pm.response.to.have.status(204); });",
              "pm.test(\"Body is empty\", function () { pm.expect(pm.response.text()).to.eql(\"\"); });"
            ]
          }
        }
      ]
    },
    {
      "name": "06 - Delete Product (Not Found)",
      "request": { "method": "DELETE", "url": "{{baseUrl}}/api/products/{{productId}}" },
      "event": [
        {
          "listen": "test",
          "script": {
            "exec": [
              "pm.test(\"Status is 404 Not Found\", function () { pm.response.to.have.status(404); });"
            ]
          }
        }
      ]
    }
  ]
}
```

---

## 11. Tóm tắt checklist trước khi nộp bài

1. `docker compose up -d` chạy được, `mongodb` + `mongo-express` đều `Up`.
2. App chạy ở `localhost:8080` không lỗi.
3. Request `01 - Create Product` → `201`, có `id`.
4. Request `03 - Update Product (Success)` → `200`, đúng dữ liệu mới, `id` không đổi, `GET` lại thấy count không tăng.
5. Request `04 - Update Product (Not Found)` → `404` (không phải `500`).
6. Request `05 - Delete Product (Success)` → `204`, `GET` lại thấy sản phẩm biến mất, count giảm 1.
7. Request `06 - Delete Product (Not Found)` → `404` (không phải `204` hay `500`).
8. Toàn bộ `pm.test` trong Collection Runner đều pass (dấu ✔ xanh).

Khi cả 8 mục trên đều đạt, cả 5 TODO trong `README.md` đã được implement đúng theo `Result_ProductService.md` và đáp ứng đủ 10 điểm tiêu chí chấm.
