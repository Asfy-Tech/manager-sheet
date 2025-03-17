from flask import request, jsonify
from . import routes
from config import settings

# API lấy nội dung template
@routes.route("/api/template", methods=["GET"])
def get_template():
    try:
        with open(settings.TEMPLATE_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        return jsonify({"success": True, "content": content})
    except Exception as e:
        with open(settings.TEMPLATE_DEFAULT_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        return jsonify({"success": True, "content": content})
    
@routes.route("/api/template/refresh", methods=["POST"])
def refresh_template():
    try:
        with open(settings.TEMPLATE_DEFAULT_FILE, "r", encoding="utf-8") as f:
            default_content = f.read()
        with open(settings.TEMPLATE_FILE, "w", encoding="utf-8") as f:
            f.write(default_content)
        return jsonify({"success": True, "content": default_content})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# API cập nhật template
@routes.route("/api/template", methods=["POST"])
def update_template():
    try:
        data = request.json
        new_content = data.get("content", "")

        with open(settings.TEMPLATE_FILE, "w", encoding="utf-8") as f:
            f.write(new_content)

        return jsonify({"success": True, "message": "Template updated successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
