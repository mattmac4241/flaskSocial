import sqlite3
from app import db
# from datetime import datetime
from app.config import DATABASE_PATH
from sqlalchemy.orm.mapper import configure_mappers


with sqlite3.connect(DATABASE_PATH) as connection:
    db.session.remove()
    db.drop_all()
    configure_mappers()
    db.create_all()