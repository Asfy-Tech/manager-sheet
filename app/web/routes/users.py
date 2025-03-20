from . import routes
from flask import current_app as app, session
from flask import jsonify, stream_with_context, Response, request
from config import settings
from werkzeug.exceptions import NotFound, BadRequest
from app.models.telegram_users import TelegramUser
from app.models.users import User
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import hash_password

@routes.route("/api/users", methods=["GET", "POST"]) 
def get_users():
    try:
        db = User()
        user_id = int(settings.ADMIN_ID)
        if request.method == 'GET':
            users = db.get()
            users = [{
                **n.to_dict(),
                'last_login': n.last_login.strftime('%Y-%m-%d %H:%M:%S') if n.last_login else None
            } for n in users if n.id != user_id]
            return jsonify({
                "success": True,
                "data": users
            })
        
        # POST method
        data = request.get_json()

        result = db.create(
            name=data.get('name', ''),
            email=data.get('email', ''),
            password=hash_password(data.get('password', '')),
            role=data.get('role'),
            avatar='/static/avatar-default.png',
            last_login=datetime.now()
        )
        
        return jsonify({
            "success": True,
            "data": result.to_dict()
        })
            
    except BadRequest as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        app.logger.error(f"Error in watch sheet: {str(e)}")
        return jsonify({
            "success": False, 
            "error": "Internal server error"
        }), 500

@routes.route("/api/users/<int:id>", methods=["GET","DELETE","PUT"]) 
def info_get_users(id):
    db = User()
    if request.method == 'DELETE':
        try:
            if db.delete_by_id(id):
                return jsonify({
                    "success": True,
                    "message": "Xóa thành công"
                })
            return jsonify({
                "success": False,
                "error": "Không tìm thấy đường dẫn"
            }), 404
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    elif request.method == 'GET':
        params = request.args
        try:
            sheet = db.find(id).to_dict()
            if not sheet:
                return jsonify({
                    "success": False,
                    "error": "Sheet not found"
                }), 404
            
            return jsonify({
                "success": True,
                "data": sheet
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    elif request.method == 'PUT':
        try:
            # Collect the data to update from the request body
            data = request.get_json()
            
            # Attempt to find the user by ID
            sheet = db.find(id)
            if not sheet:
                return jsonify({
                    "success": False,
                    "error": "Sheet not found"
                }), 404

            status_value = data.get('status')
            if isinstance(status_value, str):  
                status_value = status_value.lower() in ['true', '1']  # Chuyển 'true' hoặc '1' thành True, còn lại là False

            sheet.name = data.get('name')
            sheet.email = data.get('email')
            sheet.status = status_value  # Bây giờ status là kiểu bool

            print(f"Status received: {data.get('status')} -> Converted: {status_value}")
            sheet.save()
            return jsonify({
                "success": True,
                "message": "Cập nhật thành công",
                "data": sheet.to_dict()  # Assuming the user object has a to_dict method
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

import os
from werkzeug.utils import secure_filename
# Hàm kiểm tra định dạng file hợp lệ
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {"png", "jpg", "jpeg", "gif"}

@routes.route("/api/users/update", methods=["POST"])
def update_profile_api():
    if "user" not in session:
        return jsonify({"error": "User not authenticated"}), 401

    user_id = session["user"].get('id')
    user = User.find(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    name = request.form.get("name", "").strip()
    if not name:
        return jsonify({"error": "Tên không được để trống"}), 400

    avatar_path = user.avatar

    if "avatar" in request.files:
        avatar = request.files["avatar"]
        if avatar and allowed_file(avatar.filename):
            filename = secure_filename(avatar.filename)
            new_avatar_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

            upload_folder = os.path.dirname(new_avatar_path)
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            # Xóa ảnh cũ nếu không phải ảnh mặc định
            if user.avatar and user.avatar != "/static/avatar-default.png":
                old_avatar_path = os.path.join(os.getcwd(), user.avatar.lstrip("/"))
                if os.path.exists(old_avatar_path):
                    os.remove(old_avatar_path)

            # Lưu ảnh mới
            avatar.save(new_avatar_path)
            avatar_path = "/" + new_avatar_path.replace("\\", "/")  # Chuẩn hóa đường dẫn

    # Cập nhật vào database
    user.name = name
    new_path = avatar_path.split("/static/", 1)[-1]
    user.avatar = '/static/' + new_path
    user.save()
    session["user"] = user.to_dict()

    return jsonify({"message": "Cập nhật thành công", "user": {"id": user_id, "name": name, "avatar": avatar_path}}), 200