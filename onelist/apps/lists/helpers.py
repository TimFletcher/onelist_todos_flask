import hashlib
from flask import current_app

def generate_hash(email, method='sha1'):
    hash_func = getattr(hashlib, method, None)
    if hash_func:
        return hash_func(email + current_app.config.get('SECRET_KEY', '')).hexdigest()