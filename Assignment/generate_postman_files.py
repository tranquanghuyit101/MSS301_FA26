import json
import os

POSTMAN_DIR = r"d:\FA26\MSS301\Code\Assignment\postman"
os.makedirs(POSTMAN_DIR, exist_ok=True)

# 1. Environment
env_data = {
    "id": "fu-cinema-local-env",
    "name": "FUCinema-Local",
    "values": [
        {"key": "gateway", "value": "http://localhost:9000", "type": "default", "enabled": True},
        {"key": "adminToken", "value": "", "type": "default", "enabled": True},
        {"key": "customerToken", "value": "", "type": "default", "enabled": True},
        {"key": "customer2Token", "value": "", "type": "default", "enabled": True},
        {"key": "newEmail", "value": "testuser_" + str(os.getpid()) + "@gmail.com", "type": "default", "enabled": True},
        {"key": "newCustomerId", "value": "", "type": "default", "enabled": True},
        {"key": "adminCreatedId", "value": "", "type": "default", "enabled": True},
        {"key": "genreId", "value": "", "type": "default", "enabled": True},
        {"key": "roomId", "value": "", "type": "default", "enabled": True},
        {"key": "movieId", "value": "", "type": "default", "enabled": True},
        {"key": "showtimeId", "value": "", "type": "default", "enabled": True},
        {"key": "showtime2Id", "value": "", "type": "default", "enabled": True},
        {"key": "bookingId", "value": "", "type": "default", "enabled": True},
        {"key": "booking2Id", "value": "", "type": "default", "enabled": True},
        {"key": "today", "value": "2026-10-02", "type": "default", "enabled": True},
        {"key": "notFoundId", "value": "66f9ffffffffffffffffffff", "type": "default", "enabled": True},
        {"key": "seedGenreActionId", "value": "66f000000000000000000001", "type": "default", "enabled": True},
        {"key": "seedGenreScifiId", "value": "66f000000000000000000005", "type": "default", "enabled": True},
        {"key": "seedRoom2Id", "value": "66f100000000000000000002", "type": "default", "enabled": True},
        {"key": "seedRoomMaintenanceId", "value": "66f100000000000000000004", "type": "default", "enabled": True},
        {"key": "seedMovieEndedId", "value": "66f200000000000000000004", "type": "default", "enabled": True}
    ]
}

with open(os.path.join(POSTMAN_DIR, "FUCinema-Local.postman_environment.json"), "w", encoding="utf-8") as f:
    json.dump(env_data, f, indent=2, ensure_ascii=False)
print("Saved Environment JSON")

# 2. Collection Builder Helper
def make_req(name, method, url_path, auth_type=None, auth_token="{{adminToken}}", body=None, tests=None, prerequest=None):
    req = {
        "name": name,
        "request": {
            "method": method,
            "header": [
                {"key": "Content-Type", "value": "application/json", "type": "text"}
            ],
            "url": {
                "raw": "{{gateway}}" + url_path,
                "host": ["{{gateway}}"],
                "path": [p for p in url_path.split("/") if p]
            }
        }
    }
    if auth_type == "bearer":
        req["request"]["auth"] = {
            "type": "bearer",
            "bearer": [{"key": "token", "value": auth_token, "type": "string"}]
        }
    if body:
        req["request"]["body"] = {
            "mode": "raw",
            "raw": json.dumps(body) if isinstance(body, (dict, list)) else body,
            "options": {"raw": {"language": "json"}}
        }
    events = []
    if prerequest:
        events.append({
            "listen": "prerequest",
            "script": {"type": "text/javascript", "exec": prerequest.split("\n")}
        })
    if tests:
        events.append({
            "listen": "test",
            "script": {"type": "text/javascript", "exec": tests.split("\n")}
        })
    if events:
        req["event"] = events
    return req

collection = {
    "info": {
        "name": "FUCinemaBookingSystem",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "item": []
}

# Folder 01-Auth
f01 = {
    "name": "01-Auth",
    "item": [
        make_req("1.1 Login Admin", "POST", "/api/auth/login", body={"email":"admin@fucinema.com","password":"@@abc123@@"},
                 tests="""pm.test("Status 200", () => pm.response.to.have.status(200));
const json = pm.response.json();
pm.test("Role is ADMIN", () => pm.expect(json.role).to.eql("ADMIN"));
pm.test("Has Bearer token", () => {
    pm.expect(json.tokenType).to.eql("Bearer");
    pm.expect(json.accessToken.split(".")).to.have.lengthOf(3);
});
pm.environment.set("adminToken", json.accessToken);"""),
        make_req("1.2 Login Customer", "POST", "/api/auth/login", body={"email":"an@gmail.com","password":"123456"},
                 tests="""pm.test("Status 200", () => pm.response.to.have.status(200));
const json = pm.response.json();
pm.test("Role is CUSTOMER", () => pm.expect(json.role).to.eql("CUSTOMER"));
pm.test("userId = 1", () => pm.expect(json.userId).to.eql(1));
pm.environment.set("customerToken", json.accessToken);"""),
        make_req("1.3 Login Wrong Password", "POST", "/api/auth/login", body={"email":"an@gmail.com","password":"wrongpassword"},
                 tests="""pm.test("Status 401", () => pm.response.to.have.status(401));"""),
        make_req("1.4 Login Inactive Customer", "POST", "/api/auth/login", body={"email":"chi@gmail.com","password":"123456"},
                 tests="""pm.test("Status 403", () => pm.response.to.have.status(403));"""),
        make_req("1.5 Login Validation Error", "POST", "/api/auth/login", body={"email":"abc","password":""},
                 tests="""pm.test("Status 400", () => pm.response.to.have.status(400));"""),
        make_req("1.6 Get Profile No Token", "GET", "/api/customers/me",
                 tests="""pm.test("Status 401", () => pm.response.to.have.status(401));"""),
        make_req("1.7 Get Profile Invalid Token", "GET", "/api/customers/me", auth_type="bearer", auth_token="invalid.bearer.token",
                 tests="""pm.test("Status 401", () => pm.response.to.have.status(401));""")
    ]
}
collection["item"].append(f01)

# Folder 02-Customer
f02 = {
    "name": "02-Customer",
    "item": [
        make_req("2.1 Register Customer", "POST", "/api/customers/register",
                 prerequest="""const rand = Math.floor(Math.random() * 100000);
pm.environment.set("newEmail", "test_" + rand + "@gmail.com");""",
                 body={"customerName":"Trần Quang Huy","telephone":"0905111222","email":"{{newEmail}}","customerBirthday":"2002-05-10","password":"password123"},
                 tests="""pm.test("Status 201", () => pm.response.to.have.status(201));
const json = pm.response.json();
pm.test("Response does NOT contain password", () => pm.expect(json.password).to.be.undefined);
pm.environment.set("newCustomerId", json.customerId);"""),
        make_req("2.2 Register Duplicate Email", "POST", "/api/customers/register",
                 body={"customerName":"Trùng Email","telephone":"0905111333","email":"an@gmail.com","customerBirthday":"2002-05-10","password":"password123"},
                 tests="""pm.test("Status 409 Conflict", () => pm.response.to.have.status(409));"""),
        make_req("2.3 Register Validation Error", "POST", "/api/customers/register",
                 body={"customerName":"","telephone":"123","email":"invalid-email","customerBirthday":"2099-01-01","password":"123"},
                 tests="""pm.test("Status 400", () => pm.response.to.have.status(400));"""),
        make_req("2.4 Login Newly Registered", "POST", "/api/auth/login",
                 body={"email":"{{newEmail}}","password":"password123"},
                 tests="""pm.test("Status 200", () => pm.response.to.have.status(200));
pm.environment.set("customer2Token", pm.response.json().accessToken);"""),
        make_req("2.5 Get Profile", "GET", "/api/customers/me", auth_type="bearer", auth_token="{{customerToken}}",
                 tests="""pm.test("Status 200", () => pm.response.to.have.status(200));
pm.test("Email is an@gmail.com", () => pm.expect(pm.response.json().email).to.eql("an@gmail.com"));"""),
        make_req("2.6 Update Profile (Unicode)", "PUT", "/api/customers/me", auth_type="bearer", auth_token="{{customerToken}}",
                 body={"customerName":"Nguyễn Văn An (Cập Nhật)","telephone":"0905999888","customerBirthday":"2002-05-10"},
                 tests="""pm.test("Status 200", () => pm.response.to.have.status(200));
pm.test("Customer name updated", () => pm.expect(pm.response.json().customerName).to.eql("Nguyễn Văn An (Cập Nhật)"));"""),
        make_req("2.7 Get Profile After Update", "GET", "/api/customers/me", auth_type="bearer", auth_token="{{customerToken}}",
                 tests="""pm.test("Status 200", () => pm.response.to.have.status(200));
pm.test("Verified Unicode name", () => pm.expect(pm.response.json().customerName).to.eql("Nguyễn Văn An (Cập Nhật)"));"""),
        make_req("2.8 Change Password Wrong Old", "PUT", "/api/customers/me/password", auth_type="bearer", auth_token="{{customerToken}}",
                 body={"oldPassword":"wrong-password","newPassword":"newpassword123"},
                 tests="""pm.test("Status 400", () => pm.response.to.have.status(400));"""),
        make_req("2.9 Change Password Success", "PUT", "/api/customers/me/password", auth_type="bearer", auth_token="{{customerToken}}",
                 body={"oldPassword":"123456","newPassword":"newpassword123"},
                 tests="""pm.test("Status 204", () => pm.response.to.have.status(204));"""),
        make_req("2.10 Login With Old Password Fails", "POST", "/api/auth/login",
                 body={"email":"an@gmail.com","password":"123456"},
                 tests="""pm.test("Status 401", () => pm.response.to.have.status(401));"""),
        make_req("2.11 Login With New Password", "POST", "/api/auth/login",
                 body={"email":"an@gmail.com","password":"newpassword123"},
                 tests="""pm.test("Status 200", () => pm.response.to.have.status(200));
pm.environment.set("customerToken", pm.response.json().accessToken);"""),
        make_req("2.12 Admin Search All Customers", "GET", "/api/customers", auth_type="bearer", auth_token="{{adminToken}}",
                 tests="""pm.test("Status 200", () => pm.response.to.have.status(200));
pm.test("Has at least 3 customers", () => pm.expect(pm.response.json().length).to.be.at.least(3));"""),
        make_req("2.13 Admin Search Keyword", "GET", "/api/customers?keyword=Bình", auth_type="bearer", auth_token="{{adminToken}}",
                 tests="""pm.test("Status 200", () => pm.response.to.have.status(200));
pm.test("Found Trần Thị Bình", () => pm.expect(pm.response.json()[0].customerName).to.include("Bình"));"""),
        make_req("2.14 Admin Get Customer 1", "GET", "/api/customers/1", auth_type="bearer", auth_token="{{adminToken}}",
                 tests="""pm.test("Status 200", () => pm.response.to.have.status(200));"""),
        make_req("2.15 Admin Get Customer Not Found", "GET", "/api/customers/99999", auth_type="bearer", auth_token="{{adminToken}}",
                 tests="""pm.test("Status 404", () => pm.response.to.have.status(404));"""),
        make_req("2.16 Admin Create Customer", "POST", "/api/customers", auth_type="bearer", auth_token="{{adminToken}}",
                 prerequest="""const rand = Math.floor(Math.random() * 100000);
pm.environment.set("adminEmail", "admin_created_" + rand + "@gmail.com");""",
                 body={"customerName":"Khách Hàng Tạo Bởi Admin","telephone":"0905333444","email":"{{adminEmail}}","customerBirthday":"2000-01-01","customerStatus":"ACTIVE","password":"admincreate123"},
                 tests="""pm.test("Status 201", () => pm.response.to.have.status(201));
pm.environment.set("adminCreatedId", pm.response.json().customerId);"""),
        make_req("2.17 Admin Update Customer", "PUT", "/api/customers/{{adminCreatedId}}", auth_type="bearer", auth_token="{{adminToken}}",
                 body={"customerName":"Khách Hàng Đã Cập Nhật","telephone":"0905333999","email":"{{adminEmail}}","customerBirthday":"2000-01-01","customerStatus":"ACTIVE","password":"adminupdate123"},
                 tests="""pm.test("Status 200", () => pm.response.to.have.status(200));"""),
        make_req("2.18 Admin Soft Delete Customer", "DELETE", "/api/customers/{{adminCreatedId}}", auth_type="bearer", auth_token="{{adminToken}}",
                 tests="""pm.test("Status 204", () => pm.response.to.have.status(204));"""),
        make_req("2.19 Verify Soft Deleted Customer Status", "GET", "/api/customers/{{adminCreatedId}}", auth_type="bearer", auth_token="{{adminToken}}",
                 tests="""pm.test("Status 200", () => pm.response.to.have.status(200));
pm.test("Status is INACTIVE", () => pm.expect(pm.response.json().customerStatus).to.eql("INACTIVE"));""")
    ]
}
collection["item"].append(f02)

# Folder 03-Genre-Room
f03 = {
    "name": "03-Genre-Room",
    "item": [
        make_req("3.1 Public Get Genres", "GET", "/api/genres",
                 tests="""pm.test("Status 200", () => pm.response.to.have.status(200));
pm.test("Has at least 5 genres", () => pm.expect(pm.response.json().length).to.be.at.least(5));"""),
        make_req("3.2 Public Get Genre By Id", "GET", "/api/genres/{{seedGenreActionId}}",
                 tests="""pm.test("Status 200", () => pm.response.to.have.status(200));
pm.test("Genre is Hành động", () => pm.expect(pm.response.json().genreName).to.eql("Hành động"));"""),
        make_req("3.3 Admin Create Genre", "POST", "/api/genres", auth_type="bearer", auth_token="{{adminToken}}",
                 prerequest="""pm.environment.set("tempGenreName", "Tâm Lý " + Math.floor(Math.random() * 10000));""",
                 body={"genreName":"{{tempGenreName}}","description":"Phim tâm lý xã hội"},
                 tests="""pm.test("Status 201", () => pm.response.to.have.status(201));
pm.environment.set("genreId", pm.response.json().genreId);"""),
        make_req("3.4 Create Duplicate Genre Conflict", "POST", "/api/genres", auth_type="bearer", auth_token="{{adminToken}}",
                 body={"genreName":"Hành động","description":"Trùng"},
                 tests="""pm.test("Status 409", () => pm.response.to.have.status(409));"""),
        make_req("3.5 Admin Update Genre", "PUT", "/api/genres/{{genreId}}", auth_type="bearer", auth_token="{{adminToken}}",
                 body={"genreName":"{{tempGenreName}} (Đã sửa)","description":"Mô tả mới"},
                 tests="""pm.test("Status 200", () => pm.response.to.have.status(200));"""),
        make_req("3.6 Delete Genre With Movies Fails (BR03)", "DELETE", "/api/genres/{{seedGenreScifiId}}", auth_type="bearer", auth_token="{{adminToken}}",
                 tests="""pm.test("Status 409 Conflict", () => pm.response.to.have.status(409));"""),
        make_req("3.7 Delete Empty Genre Success", "DELETE", "/api/genres/{{genreId}}", auth_type="bearer", auth_token="{{adminToken}}",
                 tests="""pm.test("Status 204", () => pm.response.to.have.status(204));"""),
        make_req("3.8 Admin Get Rooms", "GET", "/api/rooms", auth_type="bearer", auth_token="{{adminToken}}",
                 tests="""pm.test("Status 200", () => pm.response.to.have.status(200));
pm.test("Has at least 4 rooms", () => pm.expect(pm.response.json().length).to.be.at.least(4));"""),
        make_req("3.9 Admin Create Room", "POST", "/api/rooms", auth_type="bearer", auth_token="{{adminToken}}",
                 prerequest="""pm.environment.set("tempRoomName", "VIP Room " + Math.floor(Math.random() * 10000));""",
                 body={"roomName":"{{tempRoomName}}","roomType":"STANDARD","seatRows":5,"seatsPerRow":6,"roomStatus":"ACTIVE"},
                 tests="""pm.test("Status 201", () => pm.response.to.have.status(201));
const json = pm.response.json();
pm.test("totalSeats = 30", () => pm.expect(json.totalSeats).to.eql(30));
pm.environment.set("roomId", json.roomId);"""),
        make_req("3.10 Admin Update Room", "PUT", "/api/rooms/{{roomId}}", auth_type="bearer", auth_token="{{adminToken}}",
                 body={"roomName":"{{tempRoomName}} Updated","roomType":"THREE_D","seatRows":6,"seatsPerRow":8,"roomStatus":"ACTIVE"},
                 tests="""pm.test("Status 200", () => pm.response.to.have.status(200));
pm.test("totalSeats = 48", () => pm.expect(pm.response.json().totalSeats).to.eql(48));"""),
        make_req("3.11 Delete Room With Showtimes Fails (BR03)", "DELETE", "/api/rooms/66f100000000000000000001", auth_type="bearer", auth_token="{{adminToken}}",
                 tests="""pm.test("Status 409 Conflict", () => pm.response.to.have.status(409));"""),
        make_req("3.12 Delete Empty Room Success", "DELETE", "/api/rooms/{{roomId}}", auth_type="bearer", auth_token="{{adminToken}}",
                 tests="""pm.test("Status 204", () => pm.response.to.have.status(204));""")
    ]
}
collection["item"].append(f03)

# Folder 04-Movie
f04 = {
    "name": "04-Movie",
    "item": [
        make_req("4.1 Public Search All Movies", "GET", "/api/movies",
                 tests="""pm.test("Status 200", () => pm.response.to.have.status(200));
pm.test("Has movies", () => pm.expect(pm.response.json().length).to.be.at.least(4));"""),
        make_req("4.2 Public Search By Keyword", "GET", "/api/movies?keyword=galaxy",
                 tests="""pm.test("Status 200", () => pm.response.to.have.status(200));
pm.test("Title contains Galaxy", () => pm.expect(pm.response.json()[0].title).to.include("Galaxy"));"""),
        make_req("4.3 Public Filter By Genre", "GET", "/api/movies?genreId={{seedGenreScifiId}}",
                 tests="""pm.test("Status 200", () => pm.response.to.have.status(200));
pm.test("Genre is Khoa học viễn tưởng", () => pm.expect(pm.response.json()[0].genreName).to.eql("Khoa học viễn tưởng"));"""),
        make_req("4.4 Public Filter By Status", "GET", "/api/movies?status=NOW_SHOWING",
                 tests="""pm.test("Status 200", () => pm.response.to.have.status(200));
pm.test("Status is NOW_SHOWING", () => pm.expect(pm.response.json()[0].movieStatus).to.eql("NOW_SHOWING"));"""),
        make_req("4.5 Public Get Movie By Id", "GET", "/api/movies/66f200000000000000000001",
                 tests="""pm.test("Status 200", () => pm.response.to.have.status(200));
pm.test("Movie title matches", () => pm.expect(pm.response.json().title).to.eql("Galaxy Rangers"));"""),
        make_req("4.6 Get Movie Not Found", "GET", "/api/movies/{{notFoundId}}",
                 tests="""pm.test("Status 404", () => pm.response.to.have.status(404));"""),
        make_req("4.7 Admin Create Movie", "POST", "/api/movies", auth_type="bearer", auth_token="{{adminToken}}",
                 body={"title":"Siêu Điệp Viên","description":"Phim điệp viên kịch tính","director":"Christopher Nolan","durationMinutes":120,"language":"English","ageRating":"T16","releaseDate":"2026-11-20","genreId":"{{seedGenreActionId}}","movieStatus":"COMING_SOON"},
                 tests="""pm.test("Status 201", () => pm.response.to.have.status(201));
pm.environment.set("movieId", pm.response.json().movieId);"""),
        make_req("4.8 Create Movie Invalid Genre (BR15)", "POST", "/api/movies", auth_type="bearer", auth_token="{{adminToken}}",
                 body={"title":"Lỗi Genre","description":"Test","director":"Test","durationMinutes":90,"language":"VN","ageRating":"P","releaseDate":"2026-11-20","genreId":"{{notFoundId}}","movieStatus":"COMING_SOON"},
                 tests="""pm.test("Status 404 Not Found", () => pm.response.to.have.status(404));"""),
        make_req("4.9 Admin Update Movie", "PUT", "/api/movies/{{movieId}}", auth_type="bearer", auth_token="{{adminToken}}",
                 body={"title":"Siêu Điệp Viên (Bản Chiếu Rạp)","description":"Cập nhật","director":"Christopher Nolan","durationMinutes":130,"language":"English","ageRating":"T18","releaseDate":"2026-11-25","genreId":"{{seedGenreActionId}}","movieStatus":"NOW_SHOWING"},
                 tests="""pm.test("Status 200", () => pm.response.to.have.status(200));
pm.test("Duration updated", () => pm.expect(pm.response.json().durationMinutes).to.eql(130));"""),
        make_req("4.10 Delete Movie With Showtimes Fails (BR03)", "DELETE", "/api/movies/66f200000000000000000001", auth_type="bearer", auth_token="{{adminToken}}",
                 tests="""pm.test("Status 409 Conflict", () => pm.response.to.have.status(409));"""),
        make_req("4.11 Delete Empty Movie Success", "DELETE", "/api/movies/{{movieId}}", auth_type="bearer", auth_token="{{adminToken}}",
                 tests="""pm.test("Status 204", () => pm.response.to.have.status(204));"""),
        make_req("4.12 Customer Create Movie Forbidden", "POST", "/api/movies", auth_type="bearer", auth_token="{{customerToken}}",
                 body={"title":"Hacker Movie","description":"Hack","director":"Hacker","durationMinutes":90,"language":"VN","ageRating":"P","releaseDate":"2026-11-20","genreId":"{{seedGenreActionId}}","movieStatus":"COMING_SOON"},
                 tests="""pm.test("Status 403 Forbidden", () => pm.response.to.have.status(403));""")
    ]
}
collection["item"].append(f04)

# Folder 05-Showtime
f05 = {
    "name": "05-Showtime",
    "item": [
        make_req("5.1 Public Search All Showtimes", "GET", "/api/showtimes",
                 tests="""pm.test("Status 200", () => pm.response.to.have.status(200));
pm.test("Has at least 5 showtimes", () => pm.expect(pm.response.json().length).to.be.at.least(5));"""),
        make_req("5.2 Public Filter Showtimes", "GET", "/api/showtimes?movieId=66f200000000000000000001&date=2026-12-20",
                 tests="""pm.test("Status 200", () => pm.response.to.have.status(200));
pm.test("Returns 2 showtimes", () => pm.expect(pm.response.json().length).to.eql(2));"""),
        make_req("5.3 Public Get Showtime Detail", "GET", "/api/showtimes/66f300000000000000000001",
                 tests="""pm.test("Status 200", () => pm.response.to.have.status(200));
const json = pm.response.json();
pm.test("Contains room and movie snapshot", () => {
    pm.expect(json.movieTitle).to.eql("Galaxy Rangers");
    pm.expect(json.roomName).to.eql("Room 01");
});"""),
        make_req("5.4 Admin Create Showtime", "POST", "/api/showtimes", auth_type="bearer", auth_token="{{adminToken}}",
                 body={"movieId":"66f200000000000000000001","roomId":"66f100000000000000000002","startTime":"2026-12-25T14:00:00","ticketPrice":85000},
                 tests="""pm.test("Status 201", () => pm.response.to.have.status(201));
const json = pm.response.json();
pm.test("EndTime calculated automatically (125 mins)", () => {
    pm.expect(json.endTime).to.eql("2026-12-25T16:05:00");
});
pm.environment.set("showtimeId", json.showtimeId);"""),
        make_req("5.5 Create Overlapping Showtime Conflict (BR05)", "POST", "/api/showtimes", auth_type="bearer", auth_token="{{adminToken}}",
                 body={"movieId":"66f200000000000000000001","roomId":"66f100000000000000000002","startTime":"2026-12-25T15:00:00","ticketPrice":85000},
                 tests="""pm.test("Status 409 Conflict", () => pm.response.to.have.status(409));"""),
        make_req("5.6 Create Showtime In Past Fails (BR04)", "POST", "/api/showtimes", auth_type="bearer", auth_token="{{adminToken}}",
                 body={"movieId":"66f200000000000000000001","roomId":"66f100000000000000000002","startTime":"2020-01-01T10:00:00","ticketPrice":85000},
                 tests="""pm.test("Status 400 Bad Request", () => pm.response.to.have.status(400));"""),
        make_req("5.7 Create Showtime With ENDED Movie Fails (BR04)", "POST", "/api/showtimes", auth_type="bearer", auth_token="{{adminToken}}",
                 body={"movieId":"{{seedMovieEndedId}}","roomId":"66f100000000000000000002","startTime":"2026-12-26T10:00:00","ticketPrice":85000},
                 tests="""pm.test("Status 400 Bad Request", () => pm.response.to.have.status(400));"""),
        make_req("5.8 Create Showtime With MAINTENANCE Room Fails (BR04)", "POST", "/api/showtimes", auth_type="bearer", auth_token="{{adminToken}}",
                 body={"movieId":"66f200000000000000000001","roomId":"{{seedRoomMaintenanceId}}","startTime":"2026-12-26T10:00:00","ticketPrice":85000},
                 tests="""pm.test("Status 400 Bad Request", () => pm.response.to.have.status(400));"""),
        make_req("5.9 Create Showtime Invalid Movie Id (BR15)", "POST", "/api/showtimes", auth_type="bearer", auth_token="{{adminToken}}",
                 body={"movieId":"{{notFoundId}}","roomId":"66f100000000000000000002","startTime":"2026-12-26T10:00:00","ticketPrice":85000},
                 tests="""pm.test("Status 404 Not Found", () => pm.response.to.have.status(404));"""),
        make_req("5.10 Admin Update Showtime", "PUT", "/api/showtimes/{{showtimeId}}", auth_type="bearer", auth_token="{{adminToken}}",
                 body={"movieId":"66f200000000000000000001","roomId":"66f100000000000000000002","startTime":"2026-12-25T14:30:00","ticketPrice":90000},
                 tests="""pm.test("Status 200", () => pm.response.to.have.status(200));
pm.test("Ticket price updated", () => pm.expect(pm.response.json().ticketPrice).to.eql(90000));"""),
        make_req("5.11 Admin Soft Delete Showtime (BR06)", "DELETE", "/api/showtimes/{{showtimeId}}", auth_type="bearer", auth_token="{{adminToken}}",
                 tests="""pm.test("Status 204", () => pm.response.to.have.status(204));"""),
        make_req("5.12 Verify Soft Deleted Showtime Status", "GET", "/api/showtimes/{{showtimeId}}",
                 tests="""pm.test("Status 200", () => pm.response.to.have.status(200));
pm.test("Status is CANCELLED", () => pm.expect(pm.response.json().showtimeStatus).to.eql("CANCELLED"));""")
    ]
}
collection["item"].append(f05)

# Folder 06-Booking
f06 = {
    "name": "06-Booking",
    "item": [
        make_req("6.1 Public Get Seat Map", "GET", "/api/bookings/showtimes/66f300000000000000000001/seats",
                 tests="""pm.test("Status 200", () => pm.response.to.have.status(200));
const json = pm.response.json();
pm.test("Total seats = 80", () => pm.expect(json.totalSeats).to.eql(80));"""),
        make_req("6.2 Customer Book 2 Tickets", "POST", "/api/bookings", auth_type="bearer", auth_token="{{customerToken}}",
                 body={"items":[{"showtimeId":"66f300000000000000000001","seatCode":"E5"},{"showtimeId":"66f300000000000000000001","seatCode":"E6"}]},
                 tests="""pm.test("Status 201 Created", () => pm.response.to.have.status(201));
const json = pm.response.json();
pm.test("Total price = 190,000 (95,000 x 2)", () => pm.expect(json.totalPrice).to.eql(190000));
pm.test("Has 2 details", () => pm.expect(json.details.length).to.eql(2));
pm.environment.set("bookingId", json.bookingId);"""),
        make_req("6.3 Book Already Booked Seat Fails (BR09)", "POST", "/api/bookings", auth_type="bearer", auth_token="{{customer2Token}}",
                 body={"items":[{"showtimeId":"66f300000000000000000001","seatCode":"E5"}]},
                 tests="""pm.test("Status 409 Conflict", () => pm.response.to.have.status(409));"""),
        make_req("6.4 Book Non-existent Seat In Room Fails (BR08)", "POST", "/api/bookings", auth_type="bearer", auth_token="{{customerToken}}",
                 body={"items":[{"showtimeId":"66f300000000000000000001","seatCode":"Z99"}]},
                 tests="""pm.test("Status 400 Bad Request", () => pm.response.to.have.status(400));"""),
        make_req("6.5 Duplicate Seat In Same Request Fails (BR07)", "POST", "/api/bookings", auth_type="bearer", auth_token="{{customerToken}}",
                 body={"items":[{"showtimeId":"66f300000000000000000001","seatCode":"B1"},{"showtimeId":"66f300000000000000000001","seatCode":"B1"}]},
                 tests="""pm.test("Status 400 Bad Request", () => pm.response.to.have.status(400));"""),
        make_req("6.6 More Than 8 Tickets Fails (BR07)", "POST", "/api/bookings", auth_type="bearer", auth_token="{{customerToken}}",
                 body={"items":[{"showtimeId":"66f300000000000000000001","seatCode":"A1"},{"showtimeId":"66f300000000000000000001","seatCode":"A2"},{"showtimeId":"66f300000000000000000001","seatCode":"A3"},{"showtimeId":"66f300000000000000000001","seatCode":"A4"},{"showtimeId":"66f300000000000000000001","seatCode":"A5"},{"showtimeId":"66f300000000000000000001","seatCode":"A6"},{"showtimeId":"66f300000000000000000001","seatCode":"A7"},{"showtimeId":"66f300000000000000000001","seatCode":"A8"},{"showtimeId":"66f300000000000000000001","seatCode":"A9"}]},
                 tests="""pm.test("Status 400 Bad Request", () => pm.response.to.have.status(400));"""),
        make_req("6.7 Book Non-existent Showtime Fails", "POST", "/api/bookings", auth_type="bearer", auth_token="{{customerToken}}",
                 body={"items":[{"showtimeId":"{{notFoundId}}","seatCode":"A1"}]},
                 tests="""pm.test("Status 404 Not Found", () => pm.response.to.have.status(404));"""),
        make_req("6.8 Book CANCELLED Showtime Fails (BR08)", "POST", "/api/bookings", auth_type="bearer", auth_token="{{customerToken}}",
                 body={"items":[{"showtimeId":"66f300000000000000000005","seatCode":"A1"}]},
                 tests="""pm.test("Status 400 Bad Request", () => pm.response.to.have.status(400));"""),
        make_req("6.9 Customer 2 Book Another Showtime", "POST", "/api/bookings", auth_type="bearer", auth_token="{{customer2Token}}",
                 body={"items":[{"showtimeId":"66f300000000000000000003","seatCode":"C3"}]},
                 tests="""pm.test("Status 201 Created", () => pm.response.to.have.status(201));
pm.environment.set("booking2Id", pm.response.json().bookingId);""")
    ]
}
collection["item"].append(f06)

# Folder 07-History-Cancel
f07 = {
    "name": "07-History-Cancel",
    "item": [
        make_req("7.1 Customer View My Bookings", "GET", "/api/bookings/my", auth_type="bearer", auth_token="{{customerToken}}",
                 tests="""pm.test("Status 200", () => pm.response.to.have.status(200));
pm.test("Has at least 1 booking", () => pm.expect(pm.response.json().length).to.be.at.least(1));"""),
        make_req("7.2 Customer View Own Booking Detail", "GET", "/api/bookings/{{bookingId}}", auth_type="bearer", auth_token="{{customerToken}}",
                 tests="""pm.test("Status 200", () => pm.response.to.have.status(200));
pm.test("Booking ID matches", () => pm.expect(pm.response.json().bookingId).to.eql(Number(pm.environment.get("bookingId"))));"""),
        make_req("7.3 Customer 2 View Customer 1 Booking Forbidden (BR11)", "GET", "/api/bookings/{{bookingId}}", auth_type="bearer", auth_token="{{customer2Token}}",
                 tests="""pm.test("Status 403 Forbidden", () => pm.response.to.have.status(403));"""),
        make_req("7.4 Admin View Any Booking Detail", "GET", "/api/bookings/{{bookingId}}", auth_type="bearer", auth_token="{{adminToken}}",
                 tests="""pm.test("Status 200", () => pm.response.to.have.status(200));"""),
        make_req("7.5 Admin View All Bookings", "GET", "/api/bookings", auth_type="bearer", auth_token="{{adminToken}}",
                 tests="""pm.test("Status 200", () => pm.response.to.have.status(200));
pm.test("Has at least 2 bookings", () => pm.expect(pm.response.json().length).to.be.at.least(2));"""),
        make_req("7.6 Customer View All Bookings Forbidden", "GET", "/api/bookings", auth_type="bearer", auth_token="{{customerToken}}",
                 tests="""pm.test("Status 403 Forbidden", () => pm.response.to.have.status(403));"""),
        make_req("7.7 Customer Cancel Booking (BR12)", "PUT", "/api/bookings/{{bookingId}}/cancel", auth_type="bearer", auth_token="{{customerToken}}",
                 tests="""pm.test("Status 200", () => pm.response.to.have.status(200));
pm.test("Status is CANCELLED", () => pm.expect(pm.response.json().bookingStatus).to.eql("CANCELLED"));"""),
        make_req("7.8 Cancel Already Cancelled Booking Fails (BR12)", "PUT", "/api/bookings/{{bookingId}}/cancel", auth_type="bearer", auth_token="{{customerToken}}",
                 tests="""pm.test("Status 400 Bad Request", () => pm.response.to.have.status(400));"""),
        make_req("7.9 Verify Seat Released After Cancel", "GET", "/api/bookings/showtimes/66f300000000000000000001/seats",
                 tests="""pm.test("Status 200", () => pm.response.to.have.status(200));
pm.test("Seat E5 and E6 are released", () => {
    pm.expect(pm.response.json().bookedSeats).to.not.include("E5");
    pm.expect(pm.response.json().bookedSeats).to.not.include("E6");
});""")
    ]
}
collection["item"].append(f07)

# Folder 08-Report
f08 = {
    "name": "08-Report",
    "item": [
        make_req("8.1 Admin View Revenue Report", "GET", "/api/bookings/report?startDate=2026-10-01&endDate=2026-12-31", auth_type="bearer", auth_token="{{adminToken}}",
                 tests="""pm.test("Status 200", () => pm.response.to.have.status(200));
const json = pm.response.json();
pm.test("Report contains totalRevenue and revenueByMovie", () => {
    pm.expect(json.totalRevenue).to.be.at.least(0);
    pm.expect(json.revenueByMovie).to.be.an("array");
});"""),
        make_req("8.2 Report StartDate Greater Than EndDate Fails (BR13)", "GET", "/api/bookings/report?startDate=2026-12-31&endDate=2026-10-01", auth_type="bearer", auth_token="{{adminToken}}",
                 tests="""pm.test("Status 400 Bad Request", () => pm.response.to.have.status(400));"""),
        make_req("8.3 Customer View Revenue Report Forbidden", "GET", "/api/bookings/report?startDate=2026-10-01&endDate=2026-12-31", auth_type="bearer", auth_token="{{customerToken}}",
                 tests="""pm.test("Status 403 Forbidden", () => pm.response.to.have.status(403));""")
    ]
}
collection["item"].append(f08)

with open(os.path.join(POSTMAN_DIR, "FUCinema-Booking-System.postman_collection.json"), "w", encoding="utf-8") as f:
    json.dump(collection, f, indent=2, ensure_ascii=False)
print("Saved Collection JSON")
