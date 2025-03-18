from flask import session, redirect, url_for, request
from functools import wraps
from app.models.users import User
from datetime import datetime
import pytz
import json
from config import settings
vntz = pytz.timezone('Asia/Ho_Chi_Minh')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:  
            return redirect(url_for("guests.login", next=request.url)) 
        else:
            is_admin = False
            userLocal = session.get('user')
            user = User.find(userLocal.get('id'))
            if not user or user.status == False:
                return redirect(url_for("guests.login", next=request.url)) 
            else:
                user.last_login = datetime.now(vntz)
                user.save()
            print(json.dumps({
                'user_id': user.id ,
                'admin_id': settings.ADMIN_ID,
                'bool': user.id == int(settings.ADMIN_ID)
            }))
            if user.id == int(settings.ADMIN_ID):
                is_admin = True
            session['is_admin'] = is_admin
        return f(*args, **kwargs)
    return decorated_function
