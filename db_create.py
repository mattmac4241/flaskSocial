<<<<<<< HEAD

=======
>>>>>>> c23f1ea9630e3d92b9b53c3ff24f30e0ac5c6a91
from app import db
from sqlalchemy.orm.mapper import configure_mappers

# create the database and the db table
db.drop_all()

db.create_all()

configure_mappers()

# commit the changes
db.session.commit()

