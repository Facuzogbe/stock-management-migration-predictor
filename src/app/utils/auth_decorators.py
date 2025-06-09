from functools import wraps
from flask import abort, session, current_app

def role_required(required_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            # Modo testing - bypass de autenticación
            if current_app.config.get('TESTING'):
                return view_func(*args, **kwargs)
                
            # Verificación normal de roles
            user_role = session.get("user_role") or session.get("role")
            if user_role not in required_roles:
                abort(403)
            return view_func(*args, **kwargs)
        return wrapper
    return decorator