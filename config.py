import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):

    # App
    SECRET_KEY = os.environ.get('SECRET_KEY') or \
    'no-secret-key-exists'

    # SQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['jwdepetro@gmail.com']

    # Last.fm API
    LAST_API_URL = os.environ.get('LAST_API_URL')
    LAST_API_KEY = os.environ.get('LAST_API_KEY')
    LAST_API_SECRET = os.environ.get('LAST_API_SECRET')