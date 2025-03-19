from . import routes, guests
from flask import render_template, abort, redirect, url_for, session, make_response, jsonify
from app.models.companies import Companies

@routes.route("/", methods=["GET"])
def main():
    return render_template('index.html')

@routes.route("/tasks", methods=["GET"]) 
def list_tasks():
    return render_template('sheets/tasks.html')


@routes.route("/watch-sheets", methods=["GET"]) 
def watch_sheets():
    return render_template('sheets/watch.html')

@routes.route("/telegrams/template", methods=["GET"]) 
def telegram_template():
    return render_template('telegrams/template.html')

@routes.route("/settings", methods=["GET"]) 
def settings():
    return render_template('settings.html')

@routes.route("/telegrams/users", methods=["GET"]) 
def telegrams_users():
    return render_template('telegrams/users.html')

@routes.route("/users", methods=["GET"]) 
def users():
    return render_template('users.html')

@routes.route("/telegrams/notification", methods=["GET"]) 
def telegrams_notification():
    return render_template('telegrams/notification.html')

@routes.route("/sheets/<int:id>", methods=["GET"]) 
def watch_sheet_detail(id):
    try:
        db = Companies()
        sheet = db.find(id).to_dict()
        if not sheet:
            abort(404)
        return render_template('sheets/details.html', sheet_id=id, sheetInfo=sheet)
    except Exception as e:
        abort(500)

@routes.route("/api/logout", methods=["POST"])
def logout():
    response = make_response(jsonify({"success": True, "message": "Đăng xuất thành công"}))
    response.set_cookie("token", "", expires=0)
    session.clear()
    return response
