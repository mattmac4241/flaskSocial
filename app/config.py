# project/_config.py
import os
import psycopg2
import urlparse

# grab the folder where this script lives
basedir = os.path.abspath(os.path.dirname(__file__))

DATABASE = 'social.db'
CSRF_ENABLED = True
SECRET_KEY = '\xff\xdcUf\xdd\x9a\x9c\x16\x86\xaf\t\x8c\xc0\xce\x1b\xc4\x90*N\t\x04\x87z\x83'
SECURITY_PASSWORD_SALT = '6a6918f650bb2dbd3c855b1e66166b2bc09649d161317610'
DEBUG = True

MAIL_SERVER = 'smtp.googlemail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True

# gmail authentication
MAIL_USERNAME = os.environ['APP_MAIL_USERNAME']
MAIL_PASSWORD = os.environ['APP_MAIL_PASSWORD']

# mail accounts
MAIL_DEFAULT_SENDER = 'flaskGroup@gmail.com'

# define the full path for the database
DATABASE_PATH = os.path.join(basedir, DATABASE)

urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse(os.environ["DATABASE_URL"])

# the database uri
#SQLALCHEMY_DATABASE_URI = "postgresql://matt:Password@localhost/social"
