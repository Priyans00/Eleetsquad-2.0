import os
import jwt
from flask import request, jsonify
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

SUPABASE_JWT_SECRET = os.environ.get('SUPABASE_JWT_SECRET')  # Set this in your environment from Supabase project settings


def supabase_jwt_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization', None)
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'msg': 'Missing or invalid Authorization header'}), 401
        token = auth_header.split(' ')[1]
        print(SUPABASE_JWT_SECRET)
        print(token)  
        print(type(token))
        try:
            payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=['HS256'],options={"verify_aud": False})
            request.supabase_user = payload
            print(payload)
            print(type(payload))
        except Exception as e:
            return jsonify({'msg': f'Invalid Supabase JWT: {str(e)}'}), 401
        return fn(*args, **kwargs)
    return wrapper