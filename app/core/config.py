import os

class Config:
    # sqlal0.0.0.0CHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://admin:admin@localhost:5432/comfyui_database')
    #SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    DB_USER = os.environ.get("DB_USER", "dev")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "dev")
    DB_HOST = os.environ.get("DB_HOST", "10.80.108.116")
    DB_PORT = os.environ.get("DB_PORT", "5432")
    DB_NAME = os.environ.get("DB_NAME", "comfydb2")

    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
