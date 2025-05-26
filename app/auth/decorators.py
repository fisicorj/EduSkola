from flask import redirect, url_for, flash
from flask_login import current_user
from functools import wraps

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Você precisa estar logado para acessar esta página.', 'warning')
                return redirect(url_for('auth.login'))
            if current_user.role not in roles:
                flash('Você não tem permissão para acessar esta página.', 'danger')
                return redirect(url_for('painel.painel'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

