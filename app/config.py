# project/_config.py
import os


# grab the folder where this script lives
basedir = os.path.abspath(os.path.dirname(__file__))

DATABASE = 'social.db'
CSRF_ENABLED = True
SECRET_KEY = '\xff\xdcUf\xdd\x9a\x9c\x16\x86\xaf\t\x8c\xc0\xce\x1b\xc4\x90*N\t\x04\x87z\x83'
DEBUG = False

# define the full path for the database
DATABASE_PATH = os.path.join(basedir, DATABASE)

# the database uri
SQLALCHEMY_DATABASE_URI = "postgresql://matt:Password@localhost/social"
