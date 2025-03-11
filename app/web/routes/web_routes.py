from . import routes
from flask import render_template, abort
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

@routes.route("/settings", methods=["GET"]) 
def settings():
    return render_template('settings.html')

@routes.route("/sheets/<int:id>", methods=["GET"]) 
def watch_sheet_detail(id):
    try:
        db = Companies()
        sheet = db.find(id).to_dict()
        if not sheet:
            abort(404)
        return render_template('sheets/details.html', sheet_id=id, sheetInfo=sheet)
    except Exception as e:
        print(e)
        abort(500)

