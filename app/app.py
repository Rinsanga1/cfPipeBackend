from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api
from app.core.db import db
from app.api.admin import api as admin_ns
from app.core.config import Config
from app.api import api 
from flask_jwt_extended import JWTManager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    app.config['JWT_SECRET_KEY'] = 'your_secret_key'  
    jwt = JWTManager(app)
    
    db.init_app(app)
    api.init_app(app)

    return app
