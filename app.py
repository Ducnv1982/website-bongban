from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

import re  # Thư viện để kiểm tra định dạng email

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None  # Biến để lưu thông báo lỗi
    if request.method == "POST":
        # Lấy dữ liệu từ form
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        phone = request.form["phone"].strip()

        # Kiểm tra dữ liệu nhập
        if not name:
            error = "Họ và tên không được để trống."
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):  # Kiểm tra định dạng email
            error = "Email không hợp lệ. Vui lòng nhập đúng định dạng email."
        elif not phone.isdigit():  # Kiểm tra số điện thoại chỉ chứa số
            error = "Số điện thoại chỉ được chứa các chữ số."
        else:
            # Lưu vào cơ sở dữ liệu
            try:
                conn = sqlite3.connect("users.db")  # Kết nối đến cơ sở dữ liệu
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO users (name, email, phone)
                    VALUES (?, ?, ?)
                """, (name, email, phone))  # Thêm dữ liệu vào bảng
                conn.commit()
                conn.close()

                # Trả về thông báo đăng ký thành công
                return f"<h1>Đăng ký thành công!</h1><p>Họ và tên: {name}</p><p>Email: {email}</p><p>Số điện thoại: {phone}</p>"

            except sqlite3.IntegrityError:
                # Thông báo lỗi nếu email đã tồn tại
                error = "Email đã tồn tại. Vui lòng sử dụng email khác."

    # Nếu có lỗi, hiển thị thông báo lỗi
    return render_template("register.html", error=error)


import sqlite3
# Kết nối với cơ sở dữ liệu và tạo bảng nếu chưa tồn tại
def init_db():
    conn = sqlite3.connect("users.db")  # Kết nối đến file users.db
    cursor = conn.cursor()

    # Tạo bảng users nếu chưa tồn tại
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT NOT NULL
    )
    """)
    conn.commit()  # Lưu thay đổi vào cơ sở dữ liệu
    conn.close()   # Đóng kết nối

# Gọi hàm tạo cơ sở dữ liệu khi khởi động ứng dụng
init_db()

@app.route("/users")
def users():
    # Kết nối cơ sở dữ liệu SQLite
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Lấy tất cả dữ liệu từ bảng users với các trường từ Table 2
    cursor.execute("""
        SELECT name, email, phone, join_date, elo, matches_played, win_rate, last_match, rank
        FROM users
    """)
    # Chuyển dữ liệu thành danh sách từ điển để dễ xử lý trong template
    users = [
        {
            "name": row[0],
            "email": row[1],
            "phone": row[2],
            "join_date": row[3],
            "elo": row[4],
            "matches_played": row[5],
            "win_rate": row[6],
            "last_match": row[7],
            "rank": row[8],
        }
        for row in cursor.fetchall()
    ]

    conn.close()

    # Truyền dữ liệu người dùng vào template
    return render_template("users.html", users=users)


if __name__ == "__main__":
    app.run(debug=True)
