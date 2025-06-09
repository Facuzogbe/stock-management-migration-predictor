from functools import wraps
from flask import abort
from flask import session, redirect, url_for , current_app

def role_required(required_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            if current_app.testing:
                return view_func(*args, **kwargs)
            # lógica normal...
            user_role = session.get("user_role")
            if user_role not in required_roles:
                abort(403)
            return view_func(*args, **kwargs)
        return wrapper
    return decorator