from . import routes
from flask import current_app as app
from flask import jsonify, request, render_template
from werkzeug.exceptions import NotFound, BadRequest
from app.models.notificationw import Notifications
import datetime

@routes.route("/api/telegrams/notifications", methods=["GET"]) 
def web_get_notifications():  # Đổi tên hàm này
    """Get all notifications"""
    try:
        db = Notifications()
        notifications = db.get()
        notifications_data = [
            {
                **n.to_dict(),  
                "created_at": n.created_at.strftime('%Y-%m-%d %H:%M:%S') if n.created_at else None
            } 
            for n in notifications
        ]
        return jsonify({
            "success": True,
            "data": notifications_data
        })
    except Exception as e:
        app.logger.error(f"Error fetching notifications: {str(e)}")
        return jsonify({
            "success": False, 
            "error": "Internal server error"
        }), 500

@routes.route("/api/telegrams/notifications", methods=["POST"])
def web_create_notification():  # Đổi tên hàm này
    """Create a new notification"""
    try:
        data = request.get_json()
        if not data:
            raise BadRequest("No data provided")
            
        if not data.get('title'):
            raise BadRequest("Title is required")
            
        if not data.get('content'):
            raise BadRequest("Content is required")
        
        # Sử dụng status=1 thay vì 'active'
        status = data.get('status', 1)
        
        db = Notifications()
        notification = db.create(
            title=data['title'],
            content=data['content'],
            status=status
        )
        
        return jsonify({
            "success": True,
            "data": notification.to_dict(),
            "message": "Notification created successfully"
        }), 201
            
    except BadRequest as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        app.logger.error(f"Error creating notification: {str(e)}")
        return jsonify({
            "success": False, 
            "error": "Internal server error"
        }), 500

@routes.route("/api/telegrams/notifications/<int:id>", methods=["GET"])
def web_get_notification(id):  # Đổi tên hàm này
    """Get a specific notification by ID"""
    try:
        db = Notifications()
        notification = db.find(id)
        
        if not notification:
            return jsonify({
                "success": False,
                "error": "Notification not found"
            }), 404
            
        return jsonify({
            "success": True,
            "data": {
                **notification.to_dict(),
                "created_at": notification.created_at.strftime('%Y-%m-%d %H:%M:%S') if notification.created_at else None
            }
        })
    except Exception as e:
        app.logger.error(f"Error fetching notification: {str(e)}")
        return jsonify({
            "success": False, 
            "error": "Internal server error"
        }), 500

@routes.route("/api/telegrams/notifications/<int:id>", methods=["PUT"])
def web_update_notification(id):  # Đổi tên hàm này
    """Update an existing notification"""
    try:
        data = request.get_json()
        if not data:
            raise BadRequest("No data provided")
            
        db = Notifications()
        notification = db.find(id)
        
        if not notification:
            return jsonify({
                "success": False,
                "error": "Notification not found"
            }), 404
            
        update_fields = {}
        if 'title' in data:
            update_fields['title'] = data['title']
        if 'content' in data:
            update_fields['content'] = data['content']
        if 'status' in data:
            update_fields['status'] = int(data['status'])  # Đảm bảo status là số
        
        notification = notification.update(**update_fields)
        
        return jsonify({
            "success": True,
            "data": notification.to_dict(),
            "message": "Notification updated successfully"
        })
            
    except BadRequest as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        app.logger.error(f"Error updating notification: {str(e)}")
        return jsonify({
            "success": False, 
            "error": "Internal server error"
        }), 500

@routes.route("/api/telegrams/notifications/<int:id>", methods=["DELETE"])
def web_delete_notification(id):  # Đổi tên hàm này
    """Delete a notification by ID"""
    try:
        db = Notifications()
        if db.delete_by_id(id):
            return jsonify({
                "success": True,
                "message": "Notification deleted successfully"
            })
        return jsonify({
            "success": False,
            "error": "Notification not found"
        }), 404
    except Exception as e:
        app.logger.error(f"Error deleting notification: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500

# Route để hiển thị trang quản lý thông báo
@routes.route("/telegrams/notifications", methods=["GET"])
def web_notification_page():  # Đổi tên hàm này
    """Hiển thị trang quản lý thông báo"""
    return render_template("telegrams/notification.html")