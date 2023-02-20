from flask import request, redirect, url_for
from functools import wraps


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.cookies.get("user_id") is None:
            return redirect(url_for('accounts.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function
