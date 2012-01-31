from flask import session, redirect, url_for, request, g
from functools import wraps

def login_required(func):
    """
    Decorator to check the session for a user's email. If it exists, they can 
    access the view. If not they are redirected to the login page with the
    current URL as the next parameter.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'email' not in session:
            return redirect(url_for('accounts.login', next=request.url))
        return func(*args, **kwargs)
    return wrapper
