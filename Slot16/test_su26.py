import requests
import json
import sys
import time

BASE_ROOM = "http://localhost:8081"
BASE_RES = "http://localhost:8082"
BASE_GW = "http://localhost:8080"

passed = 0
failed = 0

def test(name, cond, details=""):
    global passed, failed
    if cond:
        print(f"[PASS] {name}")
        passed += 1
    else:
        print(f"[FAIL] {name}: {details}")
        failed += 1

print("--- Testing DE190353RoomService (8081) ---")

# 1. OpenAPI docs
try:
    r = requests.get(f"{BASE_ROOM}/v3/api-docs")
    test("RoomService OpenAPI docs", r.status_code == 200, f"Status: {r.status_code}")
except Exception as e:
    test("RoomService OpenAPI docs", False, str(e))

# 2. POST /api/rooms - Success (status 201, custom status 1)
unique_suffix = str(int(time.time()))[-4:]
new_room = {
    "roomNumber": f"R-{unique_suffix}",
    "roomType": "DELUXE",
    "pricePerNight": 250.0,
    "capacity": 3,
    "floor": 4,
    "status": "AVAILABLE"
}
created_room_id = None
try:
    r = requests.post(f"{BASE_ROOM}/api/rooms", json=new_room)
    data = r.json()
    test("POST /api/rooms - Created 201", r.status_code == 201 and data.get("status") == 1 and data.get("data", {}).get("status") == "AVAILABLE", f"{r.status_code} - {r.text}")
    created_room_id = data.get("data", {}).get("roomId")
except Exception as e:
    test("POST /api/rooms - Created 201", False, str(e))

# 3. POST /api/rooms - Duplicate roomNumber (status 226, custom status 3)
try:
    r = requests.post(f"{BASE_ROOM}/api/rooms", json=new_room)
    data = r.json()
    test("POST /api/rooms - Duplicate 226", r.status_code == 226 and data.get("status") == 3, f"{r.status_code} - {r.text}")
except Exception as e:
    test("POST /api/rooms - Duplicate 226", False, str(e))

# 4. POST /api/rooms - Validation error capacity > 10 (status 406, custom status 2)
invalid_room = {
    "roomNumber": f"E-{unique_suffix}",
    "roomType": "DELUXE",
    "pricePerNight": 250.0,
    "capacity": 20,
    "floor": 4
}
try:
    r = requests.post(f"{BASE_ROOM}/api/rooms", json=invalid_room)
    data = r.json()
    test("POST /api/rooms - Validation 406", r.status_code == 406 and data.get("status") == 2, f"{r.status_code} - {r.text}")
except Exception as e:
    test("POST /api/rooms - Validation 406", False, str(e))

# 5. GET /api/rooms/{id} - Success (status 200, custom status 1)
try:
    r = requests.get(f"{BASE_ROOM}/api/rooms/1")
    data = r.json()
    test("GET /api/rooms/1 - Found 200", r.status_code == 200 and data.get("status") == 1 and data.get("data", {}).get("roomNumber") == "A-101", f"{r.status_code} - {r.text}")
except Exception as e:
    test("GET /api/rooms/1 - Found 200", False, str(e))

# 6. GET /api/rooms/{id} - Not found (status 404, custom status 4)
try:
    r = requests.get(f"{BASE_ROOM}/api/rooms/9999")
    data = r.json()
    test("GET /api/rooms/9999 - Not Found 404", r.status_code == 404 and data.get("status") == 4, f"{r.status_code} - {r.text}")
except Exception as e:
    test("GET /api/rooms/9999 - Not Found 404", False, str(e))

# 7. PUT /api/rooms/{id} - Success (status 200, custom status 1)
try:
    r = requests.put(f"{BASE_ROOM}/api/rooms/1", json={"pricePerNight": 110.0})
    data = r.json()
    test("PUT /api/rooms/1 - Updated 200", r.status_code == 200 and data.get("status") == 1 and data.get("data", {}).get("pricePerNight") == 110.0, f"{r.status_code} - {r.text}")
except Exception as e:
    test("PUT /api/rooms/1 - Updated 200", False, str(e))

# 8. DELETE /api/rooms/{id} - Success set to MAINTENANCE (status 200, custom status 1)
try:
    r = requests.delete(f"{BASE_ROOM}/api/rooms/2")
    data = r.json()
    test("DELETE /api/rooms/2 - Set MAINTENANCE 200", r.status_code == 200 and data.get("status") == 1, f"{r.status_code} - {r.text}")
    # Verify room 2 status
    r2 = requests.get(f"{BASE_ROOM}/api/rooms/2")
    test("Room 2 status is MAINTENANCE", r2.json().get("data", {}).get("status") == "MAINTENANCE", f"{r2.text}")
except Exception as e:
    test("DELETE /api/rooms/2", False, str(e))

# 9. GET /api/rooms - Search pagination (status 200, custom status 1)
try:
    r = requests.get(f"{BASE_ROOM}/api/rooms?page=1&size=2")
    data = r.json()
    test("GET /api/rooms pagination - 200", r.status_code == 200 and data.get("status") == 1 and len(data.get("data", {}).get("items", [])) <= 2, f"{r.status_code} - {r.text}")
except Exception as e:
    test("GET /api/rooms pagination", False, str(e))

# 10. GET /api/rooms - Invalid pagination size > 100 (status 406, custom status 2)
try:
    r = requests.get(f"{BASE_ROOM}/api/rooms?size=150")
    data = r.json()
    test("GET /api/rooms size=150 - 406", r.status_code == 406 and data.get("status") == 2, f"{r.status_code} - {r.text}")
except Exception as e:
    test("GET /api/rooms size=150 - 406", False, str(e))

print("\n--- Testing DE190353ReservationService (8082) ---")

# 11. ReservationService OpenAPI docs
try:
    r = requests.get(f"{BASE_RES}/v3/api-docs")
    test("ReservationService OpenAPI docs", r.status_code == 200, f"Status: {r.status_code}")
except Exception as e:
    test("ReservationService OpenAPI docs", False, str(e))

# 12. POST /api/reservations - Room 1 is AVAILABLE (price 110/night, capacity 2). 2 nights = 220
new_res = {
    "roomId": 1,
    "guestName": "Nguyen Van A",
    "guestEmail": "nguyenvana@gmail.com",
    "guestPhone": "0912345678",
    "checkInDate": "10/11/2026",
    "checkOutDate": "12/11/2026",
    "numberOfGuests": 2
}
created_res_id = None
try:
    r = requests.post(f"{BASE_RES}/api/reservations", json=new_res)
    data = r.json()
    test("POST /api/reservations - Created 201", r.status_code == 201 and data.get("status") == 1 and data.get("data", {}).get("status") == "CONFIRMED" and data.get("data", {}).get("totalAmount") == 220.0, f"{r.status_code} - {r.text}")
    created_res_id = data.get("data", {}).get("reservationId")
except Exception as e:
    test("POST /api/reservations - Created 201", False, str(e))

# 13. POST /api/reservations - Non-existent room (status 404, custom status 4)
invalid_room_res = dict(new_res)
invalid_room_res["roomId"] = 9999
try:
    r = requests.post(f"{BASE_RES}/api/reservations", json=invalid_room_res)
    data = r.json()
    test("POST /api/reservations non-existent room - 404", r.status_code == 404 and data.get("status") == 4, f"{r.status_code} - {r.text}")
except Exception as e:
    test("POST /api/reservations non-existent room - 404", False, str(e))

# 14. POST /api/reservations - Room not AVAILABLE (room 3 is OCCUPIED) (status 400, custom status 5)
occupied_room_res = dict(new_res)
occupied_room_res["roomId"] = 3
try:
    r = requests.post(f"{BASE_RES}/api/reservations", json=occupied_room_res)
    data = r.json()
    test("POST /api/reservations room not AVAILABLE - 400", r.status_code == 400 and data.get("status") == 5, f"{r.status_code} - {r.text}")
except Exception as e:
    test("POST /api/reservations room not AVAILABLE - 400", False, str(e))

# 15. POST /api/reservations - checkOutDate <= checkInDate (status 406, custom status 2)
invalid_date_res = dict(new_res)
invalid_date_res["checkOutDate"] = "09/11/2026"
try:
    r = requests.post(f"{BASE_RES}/api/reservations", json=invalid_date_res)
    data = r.json()
    test("POST /api/reservations checkOut <= checkIn - 406", r.status_code == 406 and data.get("status") == 2, f"{r.status_code} - {r.text}")
except Exception as e:
    test("POST /api/reservations checkOut <= checkIn - 406", False, str(e))

# 16. POST /api/reservations - numberOfGuests > capacity (room 1 capacity 2, guests 5) (status 406, custom status 2)
over_guest_res = dict(new_res)
over_guest_res["numberOfGuests"] = 5
try:
    r = requests.post(f"{BASE_RES}/api/reservations", json=over_guest_res)
    data = r.json()
    test("POST /api/reservations guests > capacity - 406", r.status_code == 406 and data.get("status") == 2, f"{r.status_code} - {r.text}")
except Exception as e:
    test("POST /api/reservations guests > capacity - 406", False, str(e))

# 17. GET /api/reservations/{id} - Success with room info populated (status 200, custom status 1)
if created_res_id:
    try:
        r = requests.get(f"{BASE_RES}/api/reservations/{created_res_id}")
        data = r.json()
        room_obj = data.get("data", {}).get("room")
        test("GET /api/reservations/{id} with room info - 200", r.status_code == 200 and data.get("status") == 1 and room_obj is not None and room_obj.get("roomNumber") == "A-101", f"{r.status_code} - {r.text}")
    except Exception as e:
        test("GET /api/reservations/{id} with room info - 200", False, str(e))

# 18. PUT /api/reservations/{id} - Success (update dates -> recompute totalAmount: 3 nights = 330)
if created_res_id:
    try:
        r = requests.put(f"{BASE_RES}/api/reservations/{created_res_id}", json={"checkOutDate": "13/11/2026"})
        data = r.json()
        test("PUT /api/reservations/{id} recompute amount - 200", r.status_code == 200 and data.get("status") == 1 and data.get("data", {}).get("totalAmount") == 330.0, f"{r.status_code} - {r.text}")
    except Exception as e:
        test("PUT /api/reservations/{id}", False, str(e))

# 19. DELETE /api/reservations/{id} - Success sets CANCELLED (status 200, custom status 1)
if created_res_id:
    try:
        r = requests.delete(f"{BASE_RES}/api/reservations/{created_res_id}")
        data = r.json()
        test("DELETE /api/reservations/{id} - 200", r.status_code == 200 and data.get("status") == 1, f"{r.status_code} - {r.text}")
        r2 = requests.get(f"{BASE_RES}/api/reservations/{created_res_id}")
        test("Reservation status is CANCELLED", r2.json().get("data", {}).get("status") == "CANCELLED", f"{r2.text}")
    except Exception as e:
        test("DELETE /api/reservations/{id}", False, str(e))

# 20. GET /api/reservations pagination (status 200, custom status 1)
try:
    r = requests.get(f"{BASE_RES}/api/reservations?page=1&size=5")
    data = r.json()
    test("GET /api/reservations pagination - 200", r.status_code == 200 and data.get("status") == 1, f"{r.status_code} - {r.text}")
except Exception as e:
    test("GET /api/reservations pagination", False, str(e))

print("\n--- Testing DE190353HotelGateway (8080) ---")

# 21. Gateway Swagger UI / Swagger Config
try:
    r = requests.get(f"{BASE_GW}/v3/api-docs/swagger-config")
    test("Gateway Swagger Config - 200", r.status_code == 200, f"Status: {r.status_code}")
except Exception as e:
    test("Gateway Swagger Config", False, str(e))

# 22. Gateway Route to RoomService
try:
    r = requests.get(f"{BASE_GW}/api/rooms/1")
    data = r.json()
    test("Gateway routing -> /api/rooms/1 - 200", r.status_code == 200 and data.get("status") == 1 and data.get("data", {}).get("roomNumber") == "A-101", f"{r.status_code} - {r.text}")
except Exception as e:
    test("Gateway routing -> /api/rooms/1", False, str(e))

# 23. Gateway Route to ReservationService
try:
    r = requests.get(f"{BASE_GW}/api/reservations?page=1&size=5")
    data = r.json()
    test("Gateway routing -> /api/reservations - 200", r.status_code == 200 and data.get("status") == 1, f"{r.status_code} - {r.text}")
except Exception as e:
    test("Gateway routing -> /api/reservations", False, str(e))

print("\n==============================")
print(f"SUMMARY: {passed} PASSED, {failed} FAILED")
print("==============================")

if failed > 0:
    sys.exit(1)
