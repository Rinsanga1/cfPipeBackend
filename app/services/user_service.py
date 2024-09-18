from app.models.user import User
from app.core.db import db

def create_user(data):
    email = data.get('email')
    password = data.get('password')
    if User.query.filter_by(email=email).first():
        return {'message': 'User already exists'}, 400
    new_user = User(email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return {'message': 'User created successfully'}, 201

def authenticate_user(data):
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        return {'message': 'Login successful'}, 200
    return {'message': 'Invalid credentials'}, 401
