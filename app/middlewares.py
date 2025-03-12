from flask import session, redirect, url_for, request
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:  
            return redirect(url_for("guests.login", next=request.url)) 
        return f(*args, **kwargs)
    return decorated_function
