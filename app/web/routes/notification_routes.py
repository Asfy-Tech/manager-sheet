from . import routes
from flask import jsonify, Response, request
from app.models.notification import NotificationDB

@routes.route("/api/notifications", methods=["GET"])
def get_notifications():
    try:
        db = NotificationDB()
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        notifications = db.get_notifications(limit, offset)
        return jsonify({
            "success": True,
            "data": notifications
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

        db = NotificationDB()
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