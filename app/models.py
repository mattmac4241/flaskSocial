from app import db,app
import datetime

from sqlalchemy_searchable import make_searchable
from sqlalchemy_utils.types import TSVectorType
from flask.ext.sqlalchemy import SQLAlchemy, BaseQuery
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_searchable import SearchQueryMixin


#Table for user's posts
association_table = db.Table('association_table',
    db.Column('user_id', db.Integer, db.ForeignKey('posts.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('users.id'))
)

#relationship table for user's friends
friends = db.Table('friends',
    db.Column('friend1_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('friend2_id', db.Integer, db.ForeignKey('users.id'))
)

#relationship table for members of a group
members = db.Table('members',
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
)
#relationship table for banned members of a group
banned_members = db.Table('banned_members',
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
)

#relationship table for posts of a group
group_posts = db.Table('group_posts',
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'))
)

#relationship table for admins of a group
admins = db.Table('admins',
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
)

#relationship table for likes of a post
post_likes = db.Table('post_likes',
    db.Column('post_id',db.Integer,db.ForeignKey('posts.id')),
    db.Column('user_id',db.Integer,db.ForeignKey('users.id'))
)
#relationship table for comments on post
comment_likes = db.Table('comment_likes',
    db.Column('comment_id',db.Integer,db.ForeignKey('comments.id')),
    db.Column('user_id',db.Integer,db.ForeignKey('users.id'))
)

make_searchable()
db.configure_mappers()


'''The user class is for every user
'''
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
            db.session.commit()
            return self

    def is_friend(self,user):
        if user in self.friends:
            return True
        else:
            return False

    def add_post(self,post):
        self.posts.append(post)
        db.session.commit()

#for group and personal posts
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
    self_post = db.Column(db.Boolean,default=True)

    def __init__(self,title,content,poster,poster_name,self_post):
        self.title = title
        self.content = content
        self.poster = poster
        self.poster_name = poster_name
        self.self_post = self_post

    def like(self,user):
        self.likes.append(user)
        db.session.commit()

    def unlike(self,user):
        self.likes.remove(user)
        db.session.commit()

    def delete(self):
        self.likes = []
        Post.query.filter_by(id=self.id).delete()
        db.session.commit()

#a friend request is made between two users and if its accepted or rejcted it's deleted
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

#model for joining private group
class GroupRequest(db.Model):
    __tablename__ = 'group_requests'

    id = db.Column(db.Integer, primary_key = True)
    user = db.Column(db.Integer, db.ForeignKey('users.id'))
    group = db.Column(db.Integer, db.ForeignKey('groups.id'))
    accepted = db.Column(db.Boolean,default = False)


    def __init__(self,user,group):
        self.user = user
        self.group = group
        self.accepted = False

    def accept(self,user,group):
        group.join(user)
        self.reject()

    def reject(self):
        GroupRequest.query.filter_by(id=self.id).delete()
        db.session.commit()

#model for a message sent between users
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

#comments on a post
class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer,primary_key=True)
    content = db.Column(db.String,nullable=False)
    poster = db.Column(db.Integer, db.ForeignKey('users.id'))
    likes = db.relationship('User',secondary=comment_likes,backref=db.backref('comment_likes',lazy='dynamic'))
    time_posted = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    poster_name = db.Column(db.String)
    parent = db.Column(db.Integer,db.ForeignKey('posts.id'))

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


#user for searching a group
class GroupQuery(BaseQuery, SearchQueryMixin):
    pass


class Group(db.Model):
    query_class = GroupQuery
    __tablename__ = 'groups'

    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String,unique=True,nullable=False)
    members = db.relationship('User',secondary=members,backref=db.backref('group_users', lazy='dynamic'))
    group_posts = db.relationship('Post',secondary=group_posts,backref=db.backref('group_posts', lazy='dynamic',order_by=Post.time_posted))
    admins = db.relationship('User',secondary=admins,backref=db.backref('admin_users', lazy='dynamic'))
    banned_members = db.relationship('User',secondary=banned_members,backref=db.backref('group_banned_users', lazy='dynamic'))
    description = db.Column(db.String)
    private = db.Column(db.Boolean)
    search_vector = db.Column(TSVectorType('group_name', 'group_description'))

    def __init__(self,name,description,admin,private):
        self.name = name
        self.description = description
        self.admins.append(admin)
        self.private = private
        self.members.append(admin)

    def __repr__(self):
        return '<Group {0}>'.format(self.name)

    def is_member(self,user):
        if user in self.members:
            return True
        else:
            return False

    def is_admin(self,user):
        if user in self.admins:
            return True
        else:
            return False

    def join(self,user):
        self.members.append(user)
        db.session.commit()

    def leave(self,user):
        user = User.query.get(user)
        self.members.remove(user)
        db.session.commit()

    def make_admin(self,user):
        self.admins.append(user)
        db.session.commit()

    def add_post(self,post):
        self.group_posts.append(post)
        db.session.commit()

    def is_banned(self,user):
        if user in self.banned_members:
            return True
        else:
            return False









