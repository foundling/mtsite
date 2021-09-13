import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db/mt.db')
    SQLALCHEMY_TRACK_MODIFICATIONS  = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'DEVKEY'
