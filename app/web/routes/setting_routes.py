from . import routes
from flask import render_template, abort, request, jsonify
import json
import os

CONFIG_FILE_PATH = "credentials.json"

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

