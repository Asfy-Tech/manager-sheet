from . import routes
from flask import render_template, abort, request, jsonify,session
import json
import os
import bcrypt
from app.models.users import User
CONFIG_FILE_PATH = "credentials.json"

# Hàm kiểm tra mật khẩu
def check_password(hashed_password, plain_password):
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

# Hàm hash mật khẩu mới
def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

@routes.route("/api/settings/", methods=["GET"])
def get_settings():
    try:
        if os.path.exists(CONFIG_FILE_PATH):
            with open(CONFIG_FILE_PATH, 'r') as file:
                config = json.load(file)
                return jsonify(config)
        return jsonify({
            "status": "error",
            "message": "File cấu hình google api chưa tồn tại"
        }), 404
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@routes.route("/api/settings/upload", methods=["POST"])
def upload_settings():
    try:
        if 'config' not in request.files:
            return jsonify({
                "status": "error",
                "message": "Vui lòng chọn file"
            }), 400

        file = request.files['config']
        if file.filename == '':
            return jsonify({
                "status": "error",
                "message": "Chưa chọn file"
            }), 400

        if not file.filename.endswith('.json'):
            return jsonify({
                "status": "error",
                "message": "File không hợp lệ. Vui lòng tải lên file JSON"
            }), 400

        # Check if file exists
        file_exists = os.path.exists(CONFIG_FILE_PATH)
        
        # Save the uploaded file (this will overwrite if exists)
        file.save(CONFIG_FILE_PATH)

        message = "Cập nhật file cấu hình thành công" if file_exists else "Tạo file cấu hình mới thành công"
        
        return jsonify({
            "status": "success",
            "message": message
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Lỗi: {str(e)}"
        }), 500

@routes.route("/api/settings/change-password", methods=["POST"])
def change_password():
    try:
        data = request.get_json()
        current_password = data.get("currentPassword")
        new_password = data.get("newPassword")

        print("DEBUG - Received data:", data)

        user = User.find(session.get("user").get('id'))

        # Kiểm tra mật khẩu hiện tại có đúng không
        if not check_password(user.password, current_password):
            return jsonify({
                "status": "error",
                "message": "Mật khẩu hiện tại không đúng"
            }), 400

        # Hash mật khẩu mới
        new_password_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()

        # Cập nhật mật khẩu mới
        user.password = new_password_hash
        user.save()

        return jsonify({
            "status": "success",
            "message": "Đổi mật khẩu thành công"
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Lỗi: {str(e)}"
        }), 500