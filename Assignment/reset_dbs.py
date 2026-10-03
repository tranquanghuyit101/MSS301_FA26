import subprocess
import os

print("--- Resetting SQL Server ---")
sql_cmd = """
UPDATE customer SET password = '$2a$10$dmoDdVpWYdqLarqBfkYQteoq1YORLC5LLMd55bpomZ3EarS/vtjtW', customer_name = N'Nguyễn Văn An' WHERE email = 'an@gmail.com';
DELETE FROM customer WHERE email NOT IN ('an@gmail.com', 'binh@gmail.com', 'chi@gmail.com');
"""
with open("temp_reset.sql", "w", encoding="utf-8") as f:
    f.write(sql_cmd)

res = subprocess.run(["sqlcmd", "-S", "localhost,1433", "-U", "sa", "-P", "Fucinema@2026", "-d", "cinema_customer", "-C", "-i", "temp_reset.sql"], capture_output=True, text=True)
print("SQL Server:", res.stdout, res.stderr)
if os.path.exists("temp_reset.sql"):
    os.remove("temp_reset.sql")

print("--- Resetting MySQL ---")
mysql_script = """
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE booking_detail;
TRUNCATE TABLE booking;
SET FOREIGN_KEY_CHECKS = 1;
"""
res_mysql = subprocess.run(["docker", "exec", "-i", "cinema-mysql", "mysql", "-uroot", "-pmysql", "cinema_booking", "-e", mysql_script], capture_output=True, text=True)
print("MySQL:", res_mysql.stdout, res_mysql.stderr)

print("--- Checking Mongo Data ---")
res_mongo = subprocess.run(["docker", "exec", "cinema-mongo", "mongosh", "cinema_movie", "-u", "root", "-p", "password", "--authenticationDatabase", "admin", "--eval", "db.movies.deleteMany({title: {$nin: ['Galaxy Rangers', 'Ngôi Nhà Ma Ám', 'Robot Nhỏ Phiêu Lưu Ký', 'Mùa Hè Năm Ấy']}}); db.genres.updateOne({_id: ObjectId('66f000000000000000000001')}, {$set: {genreName: 'Hành động', description: 'Phim hành động, võ thuật', _class: 'com.fudn.movieservice.model.Genre'}}, {upsert: true});"], capture_output=True, text=True)
print("Mongo:", res_mongo.stdout)
print("All DBs ready for pristine test run!")
