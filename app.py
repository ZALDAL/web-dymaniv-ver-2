from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()  # chỉ gọi 1 lần

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")

db_url = os.getenv("DATABASE_URL")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://")
app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user"] = username
            return redirect(url_for("home"))
        else:
            return "❌ Sai tài khoản hoặc mật khẩu"
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if User.query.filter_by(username=username).first():
            return "⚠️ Username đã tồn tại!"
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/home")
def home():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("home.html", username=session["user"])

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/dbtest")
def dbtest():
    try:
        users = User.query.all()
        return f"Database kết nối thành công! Hiện có {len(users)} user trong bảng."
    except Exception as e:
        return f"Lỗi kết nối database: {e}"

if __name__ == "__main__":
    print("DATABASE_URL =", os.getenv("DATABASE_URL"))
    print("SECRET_KEY =", os.getenv("SECRET_KEY"))
    app.run(debug=True)
