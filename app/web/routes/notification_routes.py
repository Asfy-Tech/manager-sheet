from . import routes
from flask import jsonify, Response, request
from app.models.notifications import Notification

@routes.route("/api/notifications", methods=["GET", "DELETE"])
def get_notifications():
    try:
        if request.method == 'GET':
            #  Lấy danh sách thông báo
            notifications = Notification.get_sorted_by_created_at()

            # Đếm số lượng thông báo chưa đọc
            unread_count = len([n for n in notifications if not n.is_read])

            notifications = [
                {
                    **n.to_dict(),  
                    "created_at": n.created_at.strftime('%Y-%m-%d %H:%M:%S') if n.created_at else None
                } 
                for n in notifications
            ]

            return jsonify({
                "success": True,
                "data": notifications,
                "unread_count": unread_count
            })
        elif request.method == 'DELETE':
            Notification.delete_all()
            return jsonify({
                "success": True,
                "message": "Xoá dữ liệu thành công"
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