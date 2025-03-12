from . import routes
from flask import current_app as app
from flask import jsonify, stream_with_context, Response, request
import json
from werkzeug.exceptions import NotFound, BadRequest
from app.models.telegram_users import TelegramUser
from app.models.telegram_message import TelegramMessage
from time import sleep
from sqlalchemy import func
from config.settings import settings
import pytz
from sqlalchemy.orm import sessionmaker
from app.models.base import engine
from datetime import datetime

@routes.route("/api/telegrams/messages") 
def get_tele_message():
    Session = sessionmaker(bind=engine)
    db_session = Session()
    try:
        params = request.args
        vietname_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        today = datetime.now(vietname_tz).date()
        query = db_session.query(TelegramMessage).filter(
            func.date(TelegramMessage.created_at) == today
        )
        if 'type' in params:
            if params.get('type'):
                query = query.filter(TelegramMessage.type == params["type"])

        tasks = query.all()

        tasks = [
            {
                **n.to_dict(),  
                "deadline": n.deadline.strftime('%d-%m-%Y') if n.deadline else None
            } 
            for n in tasks
        ]
        return jsonify({
            "success": True,
            "data": tasks
        })
    except Exception as e:
        app.logger.error(f"Error in watch sheet: {str(e)}")
        return jsonify({
            "success": False, 
            "error": "Internal server error"
        }), 500


@routes.route("/api/telegrams/users", methods=["GET", "POST"]) 
def get_tele_users():
    try:
        db = TelegramUser()
        if request.method == 'GET':
            users = db.get()
            users = [n.to_dict() for n in users]
            return jsonify({
                "success": True,
                "data": users
            })
        
        # POST method
        data = request.get_json()

        result = db.create(
            name=data.get('name', ''),
            chat_id=data.get('chat_id', ''),
            role=data.get('role', '2'),
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

@routes.route("/api/telegrams/users/<int:id>", methods=["GET","DELETE","PUT"]) 
def info_get_tele_users(id):
    db = TelegramUser()
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

            # Update the user's info (you can customize this as per your fields)
            sheet.update(name=data.get('name'),chat_id=data.get('chat_id'),role=data.get('role'))  # Assuming you have an update method
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

