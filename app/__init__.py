import datetime
from flask import Flask 
from flask_mail import Mail

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bcrypt import Bcrypt
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from sqlalchemy_searchable import make_searchable
import os

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

migrate = Migrate(app, db)

bcrypt = Bcrypt(app)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

make_searchable()
db.configure_mappers()

from users.views import users_blueprint
from posts.views import posts_blueprint
from messages.views import message_blueprint 
from groups.views import groups_blueprint 
from comments.views import comments_blueprint 
from search.views import search_blueprint
from admin.views import admin_blueprint

app.register_blueprint(users_blueprint)
app.register_blueprint(posts_blueprint)
app.register_blueprint(message_blueprint)
app.register_blueprint(groups_blueprint)
app.register_blueprint(comments_blueprint)
app.register_blueprint(search_blueprint)
app.register_blueprint(admin_blueprint)