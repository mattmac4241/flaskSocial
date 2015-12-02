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

members = db.Table('members',
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
)

group_posts = db.Table('group_posts',
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'))
)

admins = db.Table('admins',
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
)

post_likes = db.Table('post_likes',
	db.Column('post_id',db.Integer,db.ForeignKey('posts.id')),
	db.Column('user_id',db.Integer,db.ForeignKey('users.id'))
)

comment_likes = db.Table('comment_likes',
	db.Column('comment_id',db.Integer,db.ForeignKey('comments.id')),
	db.Column('user_id',db.Integer,db.ForeignKey('users.id'))
)

class User(db.Model):
	__tablename__ = 'users'

	id = db.Column(db.Integer,primary_key=True)
	user_name = db.Column(db.String,unique=True,nullable=False)
	email = db.Column(db.String,unique=True,nullable=False)
	password = db.Column(db.String,nullable=False)
	posts = db.relationship('Post',secondary=association_table,backref=db.backref('user_posts', lazy='dynamic'))
	friends = db.relationship('User', 
                               secondary=friends, 
                               primaryjoin=(friends.c.friend1_id == id), 
                               secondaryjoin=(friends.c.friend2_id == id), 
                               backref=db.backref('user_friends', lazy='dynamic'), 
                               lazy='dynamic')
	groups = db.relationship('Group',secondary=members,backref=db.backref('user_groups', lazy='dynamic'))


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
	likes = db.relationship('User',secondary=post_likes,backref=db.backref('post_likes', lazy='dynamic'))
	time_posted = db.Column(db.DateTime, default=datetime.datetime.utcnow())
	group = db.Column(db.Integer,db.ForeignKey('groups.id'))
	poster_name = db.Column(db.String)

	def __init__(self,title,content,poster,poster_name):
		self.title = title
		self.content = content
		self.poster = poster
		self.poster_name = poster_name

	def like(self,user):
		self.likes.append(user)
		db.session.commit()

	def unlike(self,user):
		self.likes.remove(user)
		db.session.commit()



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

class Comment(db.Model):
	__tablename__ = 'comments'

	id = db.Column(db.Integer,primary_key=True)
	content = db.Column(db.String,nullable=False)
	poster = db.Column(db.Integer, db.ForeignKey('users.id'))
	likes = db.relationship('User',secondary=comment_likes,backref=db.backref('comment_likes',lazy='dynamic'))
	time_posted = db.Column(db.DateTime, default=datetime.datetime.utcnow())
	poster_name = db.Column(db.String)
	parent = db.Column(db.Integer,db.ForeignKey('comments.id'))

	def __init__(self,content,poster,parent,poster_name):
		self.content = content
		self.poster = poster
		self.parent = parent
		self.poster_name = poster_name
	
	def delete(self):
		Comment.query.filter_by(id=self.id).delete()
		db.session.commit()

	def like(self,user):
		self.likes.append(user)
		db.session.commit()

	def unlike(self,user):
		self.likes.remove(user)
		db.session.commit()

class Group(db.Model):
	__tablename__ = 'groups'

	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String,unique=True,nullable=False)
	members = db.relationship('User',secondary=members,backref=db.backref('group_users', lazy='dynamic'))
	group_posts = db.relationship('Post',secondary=group_posts,backref=db.backref('group_posts', lazy='dynamic'))
	admins = db.relationship('User',secondary=admins,backref=db.backref('admin_users', lazy='dynamic'))
	description = db.Column(db.String)
	private = db.Column(db.Boolean)

	def __init__(self,name,description,admin,private):
		self.name = name
		self.description = description
		self.admins.append(admin)
		self.private = private
		self.members.append(admin)

	def is_member(self,user):
		if user in members:
			return True
		else:
			return False

	def is_admin(self,user):
		if user in admins:
			return True
		else:
			return False

	def join(self,user):
		self.members.append(user)
		db.session.commit()

	def leave(self,user):
		self.members.remove(user)
		user = User.query.get(user)
		user.groups.remove(self)
		db.session.commit()

	def make_admin(self,user):
		self.admins.append(user)
		db.session.commit()

	def add_post(self,post):
		self.group_posts.append(post)
		db.session.commit()






