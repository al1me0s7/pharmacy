import os

# Конфігураційний клас
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_secret_key_pharmacy'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres:al1niaml@localhost/pharmacy'
    SQLALCHEMY_TRACK_MODIFICATIONS = False