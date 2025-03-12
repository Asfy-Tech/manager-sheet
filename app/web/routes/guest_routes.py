from . import guests
from flask import render_template, abort
from flask import request, session, redirect, url_for, jsonify
from app.models.companies import Companies
from config import check_password, hash_password
from app.models.users import User
from config import settings
import jwt
import datetime

@guests.route("/login", methods=["GET"])
def login():
    if request.method == "POST":
        # Xử lý đăng nhập tại đây (giả sử user hợp lệ)
        session["user"] = {"id": 1, "name": "Hùng"}  # Lưu user vào session

        # Lấy giá trị `next` từ request.args
        next_url = request.args.get("next")

        # Kiểm tra nếu `next_url` hợp lệ (tránh Open Redirect)
        if not next_url or next_url.startswith("/"):
            return redirect(next_url or url_for("routes.main"))
        return redirect(url_for("routes.main"))

    return render_template("auth/login.html")

@guests.route("/api/login", methods=["POST"])
def login_api():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 415

    data = request.get_json()
    user = data.get("user")
    pwd = data.get("pass")
    errors = {}
    if not user:
        errors['user'] = 'Tài khoản là trường bắt buộc'
    if not pwd:
        errors['pass'] = 'Mật khẩu là trường bắt buộc'

    if errors:
        errors['message'] = 'Đăng nhập thất bại'
        return jsonify(errors), 422

    user = User.first(email=user)

    if not user:
        return jsonify({"message": "Tài khoản không tồn tại"}), 404
    
    if not check_password(pwd, user.password):
        return jsonify({"message": "Mật khẩu không chính xác"}), 401
    
    import pytz

    vn_tz = pytz.timezone("Asia/Ho_Chi_Minh")

    token_payload = {
        "user_id": user.id,
        "exp": datetime.datetime.now(vn_tz) + datetime.timedelta(hours=24)
    }
    token = jwt.encode(token_payload, settings.APP_KEY, algorithm="HS256")

    session["user"] = user.to_dict()

    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": user.to_dict()
    })
