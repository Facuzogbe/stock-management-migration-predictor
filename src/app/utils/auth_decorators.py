from functools import wraps
from flask import abort
from flask import session, redirect, url_for

def role_required(allowed_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if "role" not in session or session["role"] not in allowed_roles:
                # return redirect(url_for("main.home"))  # o a una página tipo 403.html
                return abort(403)  # Error 403: Forbidden
            return func(*args, **kwargs)
        return wrapper
    return decorator
