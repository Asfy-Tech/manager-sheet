from . import routes
from flask import jsonify, Response, request
from app.models.notifications import Notification

@routes.route("/api/notifications", methods=["GET"])
def get_notifications():
    try:
    #  Lấy danh sách thông báo
        notifications = Notification.get()

        # Đếm số lượng thông báo chưa đọc
        unread_count = len([n for n in notifications if not n.is_read])

        return jsonify({
            "success": True,
            "data": [n.to_dict() for n in notifications],
            "unread_count": unread_count
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@routes.route("/api/notifications", methods=["POST"])
def create_notification():
    try:
        data = request.json
        if not data or not data.get('title') or not data.get('content'):
            return jsonify({
                "success": False,
                "error": "Title and content are required"
            }), 400

        db = Notification()
        success = db.add_notification(
            title=data['title'],
            content=data['content']
        )

        return jsonify({
            "success": success,
            "message": "Notification created successfully" if success else "Failed to create notification"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500