import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "devkey"
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:melnyk2006@localhost/calendar_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
