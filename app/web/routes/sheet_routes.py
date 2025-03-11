from . import routes
from flask import jsonify, stream_with_context, Response, request
from app.services.google_sheets import add_task, get_tasks, get_sheet_names, GoogleSheets
import json
from app.models.watch_path import WatchPathDB
from time import sleep
from config.settings import settings


@routes.route("/api/sheets/<sheet_name>", methods=["GET"])
def get_sheet_data(sheet_name):
    data = get_tasks(sheet_name)
    return jsonify(data)

@routes.route("/api/sheets", methods=["GET"]) 
def api_get_name():
    gg_sheet = GoogleSheets()
    sheet_names = gg_sheet.get_sheet_names(settings.GOOGLE_SHEET_MAIN_LINK)
    return jsonify(sheet_names)

@routes.route("/api/sheets/watch", methods=["GET", "POST"]) 
def get_watch_sheet():
    db = WatchPathDB()
    if request.method == 'GET':
        try:
            paths = db.get_all_paths()
            return jsonify({
                "success": True,
                "data": paths
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    elif request.method == 'POST': 
        gg_sheet = GoogleSheets()
        try:
            data = request.json
            if not data or not data.get('link'):
                return jsonify({
                    "success": False,
                    "error": "Link là bắt buộc"
                }), 400
            is_valid, sheet_id, message = gg_sheet.validate_sheet_url(data.get('link'))
            if is_valid == False:
                return jsonify({
                    "success": False,
                    "message": message,
                    f"error": f"Không thể truy cập sheet, hãy cấp quyền cho : {gg_sheet.get_service_account_email()}"
                }), 400

            result = db.add_path(
                name=data.get('name', ''),  # name có thể để trống
                status="active",
                link=data.get('link'),      # link bắt buộc phải có
            )

            if result:
                return jsonify({
                    "success": True,
                    "message": "Thêm đường dẫn thành công"
                }), 201
            else:
                return jsonify({
                    "success": False,
                    "error": "Link này đã tồn tại"
                }), 400

        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

@routes.route("/api/sheets/watch/<int:id>", methods=["GET","DELETE"]) 
def delete_watch_sheet(id):
    db = WatchPathDB()
    if request.method == 'DELETE':
        try:
            if db.delete_path(id):
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
            sheet = db.get_path_by_id(id)
            if not sheet:
                return jsonify({
                    "success": False,
                    "error": "Sheet not found"
                }), 404
            
            if 'name' in params: 
                sheet_names = gg_sheet.get_sheet_names(sheet["link"])
                return jsonify(sheet_names)
            
            if 'sheet' in params: 
                data = gg_sheet.get_data_from_link(sheet["link"], params.get('sheet'))
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