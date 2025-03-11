from . import routes
from flask import current_app as app
from flask import jsonify, stream_with_context, Response, request
from app.services.google_sheets import add_task, get_tasks, get_sheet_names, GoogleSheets
import json
from werkzeug.exceptions import NotFound, BadRequest
from app.models.companies import Companies
from time import sleep
from config.settings import settings


@routes.route("/api/sheets/<sheet_name>", methods=["GET"])
def get_sheet_data(sheet_name):
    try:
        data = get_tasks(sheet_name)
        if not data:
            raise NotFound(f"Sheet '{sheet_name}' not found")
        return jsonify(data)
    except Exception as e:
        app.logger.error(f"Error getting sheet data: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@routes.route("/api/sheets", methods=["GET"]) 
def api_get_name():
    gg_sheet = GoogleSheets()
    sheet_names = gg_sheet.get_sheet_names(settings.GOOGLE_SHEET_MAIN_LINK)
    return jsonify(sheet_names)

@routes.route("/api/sheets/watch", methods=["GET", "POST"]) 
def get_watch_sheet():
    try:
        db = Companies()
        if request.method == 'GET':
            paths = db.get()
            paths = [n.to_dict() for n in paths]
            return jsonify({
                "success": True,
                "data": paths
            })
        
        # POST method
        data = request.get_json()
        if not data or not data.get('link'):
            raise BadRequest("Link là bắt buộc")
            
        gg_sheet = GoogleSheets()
        is_valid, sheet_id, message, sheet_ids = gg_sheet.validate_sheet_url(data['link'])
        
        if not is_valid:
            raise BadRequest(f"Không thể truy cập sheet, hãy cấp quyền cho: {gg_sheet.get_service_account_email()}")
            
        result = db.create(
            name=data.get('name', ''),
            sheet_link=data['link'],
            status='active',
            comment='',
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

@routes.route("/api/sheets/watch/<int:id>", methods=["GET","DELETE"]) 
def delete_watch_sheet(id):
    db = Companies()
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
        gg_sheet = GoogleSheets()
        params = request.args
        try:
            sheet = db.find(id).to_dict()
            if not sheet:
                return jsonify({
                    "success": False,
                    "error": "Sheet not found"
                }), 404
            
            if 'name' in params: 
                sheet_names = gg_sheet.get_sheet_names(sheet["sheet_link"])
                return jsonify(sheet_names)
            
            if 'sheet' in params: 
                data = gg_sheet.get_data_from_link(sheet["sheet_link"], params.get('sheet'))
                return jsonify(data)
            
            
            return jsonify({
                "success": True,
                "data": data
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

@routes.route("/api/sheets/<sheet_name>", methods=["POST"])
def api_add_task(sheet_name):
    data = request.json
    result = add_task(sheet_name, data)
    return jsonify({"success": result})

@routes.route('/stream/<sheet_name>')
def stream(sheet_name):
    def event_stream(sheet_name):
        last_data = None
        while True:
            try:
                current_data = get_tasks(sheet_name)
                if current_data != last_data:
                    last_data = current_data
                    yield f"data: {json.dumps(current_data)}\n\n"
            except Exception as e:
                print(f"Error: {e}")
            sleep(20)

    return Response(
        stream_with_context(event_stream(sheet_name)), 
        mimetype='text/event-stream'
    )