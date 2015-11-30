from app import db,app
import datetime

association_table = db.Table('association_table',
    db.Column('user_id', db.Integer, db.ForeignKey('posts.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('users.id'))
)

friends = db.Table('friends',
    db.Column('friend1_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('friend2_id', db.Integer, db.ForeignKey('users.id'))
)

class User(db.Model):
	__tablename__ = 'users'

	id = db.Column(db.Integer,primary_key=True)
	user_name = db.Column(db.String,unique=True,nullable=False)
	email = db.Column(db.String,unique=True,nullable=False)
	password = db.Column(db.String,nullable=False)
	posts = db.relationship('Post',secondary=association_table,backref=db.backref('posts', lazy='dynamic'))
	friends = db.relationship('User', 
                               secondary=friends, 
                               primaryjoin=(friends.c.friend1_id == id), 
                               secondaryjoin=(friends.c.friend2_id == id), 
                               backref=db.backref('user_friends', lazy='dynamic'), 
                               lazy='dynamic')

	def __init__(self,user_name,email,password):
		self.user_name = user_name
		self.email = email
		self.password = password

	def delete_friend(self,user):
		if user in self.friends:
			self.friends.remove(user)
			user.friends.remove(self)
			return self

	def is_friend(self,user):
		if user in self.friends:
			return True
		else:
			return False

	
class Post(db.Model):
	__tablename__ = 'posts'
	id = db.Column(db.Integer,primary_key=True)
	title = db.Column(db.String,nullable=False)
	content = db.Column(db.String,nullable=False)
	poster = db.Column(db.Integer, db.ForeignKey('users.id'))
	likes  = db.relationship('User', 
                               secondary=friends, 
                               primaryjoin=(friends.c.friend1_id == id), 
                               secondaryjoin=(friends.c.friend2_id == id), 
                               backref=db.backref('user_', lazy='dynamic'), 
                               lazy='dynamic')

	def __init__(self,title,content,poster):
		self.title = title
		self.content = content
		self.poster = poster

class FriendRequest(db.Model):
	__tablename__ = 'friend_requests'
	id = db.Column(db.Integer, primary_key = True)
	user_sent_from = db.Column(db.Integer, db.ForeignKey('users.id'))
	user_sent_to = db.Column(db.Integer, db.ForeignKey('users.id'))
	accepted = db.Column(db.Boolean,default = False)

	def __init__(self,user_sent_from,user_sent_to):
		self.user_sent_from = user_sent_from
		self.user_sent_to = user_sent_to
		self.accepted = False

	def accept(self):
		user1 = User.query.get(self.user_sent_from)
		user2 = User.query.get(self.user_sent_to)
		if user1 not in user2.friends or user2 not in user1.friends:
			user1.friends.append(user2)
			user2.friends.append(user1)
			FriendRequest.query.filter_by(id=self.id).delete()
			db.session.commit()
			return self

	def reject(self):
		user1 = User.query.get(self.user_sent_from)
		user2 = User.query.get(self.user_sent_to)
		if user1 not in user2.friends or user2 not in user1.friends:
			FriendRequest.query.filter_by(id=self.id).delete()
			db.session.commit()

class Message(db.Model):
	__tablename__ = 'messages'
	id = db.Column(db.Integer,primary_key=True)
	user_from = db.Column(db.Integer, db.ForeignKey('users.id'))
	user_to = db.Column(db.Integer, db.ForeignKey('users.id'))
	read = db.Column(db.Boolean,default=False)
	content = db.Column(db.String,nullable=False)


	def __init__(self,user_from,user_to,content):
		self.user_from = user_from
		self.user_to = user_to
		self.content = content



