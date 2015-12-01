import datetime
from flask import Flask 
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bcrypt import Bcrypt
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand


app = Flask(__name__)
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

bcrypt = Bcrypt(app)

manager = Manager(app)
manager.add_command('db', MigrateCommand)



from users.views import users_blueprint
from posts.views import posts_blueprint
from messages.views import message_blueprint 
from groups.views import groups_blueprint 

app.register_blueprint(users_blueprint)
app.register_blueprint(posts_blueprint)
app.register_blueprint(message_blueprint)
app.register_blueprint(groups_blueprint)
