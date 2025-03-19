from flask import session, redirect, url_for, request
from functools import wraps
from app.models.users import User
from datetime import datetime
import pytz
import jwt
from config import settings
vntz = pytz.timezone('Asia/Ho_Chi_Minh')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get("token")
        print(f"TOken: {token}")
        if "user" not in session:  
            if token:
                try:
                    decoded_token = jwt.decode(token, settings.APP_KEY, algorithms=["HS256"])
                    user_id = decoded_token.get("user_id")

                    # Kiểm tra hạn token
                    exp_time = datetime.fromtimestamp(decoded_token.get("exp"))
                    if exp_time < datetime.now():
                        return redirect(url_for("guests.login", next=request.url))

                    # Tìm user trong database
                    user = User.find(user_id)
                    if not user or user.status == False:
                        return redirect(url_for("guests.login", next=request.url))

                    session["user"] = user.to_dict()
                except jwt.ExpiredSignatureError:
                    return redirect(url_for("guests.login", next=request.url))
                except jwt.InvalidTokenError:
                    return redirect(url_for("guests.login", next=request.url))
            else:
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
            # print(json.dumps({
            #     'user_id': user.id ,
            #     'admin_id': settings.ADMIN_ID,
            #     'bool': user.id == int(settings.ADMIN_ID)
            # }))
            if user.id == int(settings.ADMIN_ID):
                is_admin = True
            session['is_admin'] = is_admin
        return f(*args, **kwargs)
    return decorated_function
