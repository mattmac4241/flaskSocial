import os
import unittest

from app import app, db, bcrypt
from app.config import basedir
from app.models import User,FriendRequest

TEST_DB = 'test.db'


class UsersTest(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + os.path.join(basedir, TEST_DB)
        self.app = app.test_client()
        db.create_all()
        self.assertEquals(app.debug,False)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def create_user(self,username,email,password):
        new_user = User(
            user_name = username,
            email = email,
            password = bcrypt.generate_password_hash(password),
        )
        db.session.add(new_user)
        db.session.commit()
        return User.query.filter_by(email=email).first()

    def create_friend_request(self,user1,user2):
        new_request = FriendRequest(
            user_sent_from = user1.id,
            user_sent_to = user2.id,
            )
        db.session.add(new_request)
        db.session.commit()
        return FriendRequest.query.filter_by(user_sent_from=user1.id,user_sent_to=user2.id).first()

    def test_can_create_user_in_database(self):
        self.create_user("mattmac4241",'mattmac4241@gmail.com','password')
        test = db.session.query(User).all()
        for t in test:
            t.user_name
        assert t.user_name == 'mattmac4241'

    def test_user_can_accept_friend_request_in_database(self):
        user1 = self.create_user('mattmac4241','mattmac4241@gmail.com','password')
        user2 = self.create_user('testname','test@mail.com','password')
        request = self.create_friend_request(user1,user2)
        request.accept()
        assert user1 in user2.friends 
        assert user2 in user1.friends 

    def test_user_can_reject_friend_request_in_database(self):
        user1 = self.create_user('mattmac4241','mattmac4241@gmail.com','password')
        user2 = self.create_user('testname','test@mail.com','password')
        request = self.create_friend_request(user1,user2)
        request.reject()
        assert user1 not in user2.friends 
        assert user2 not in user1.friends 

    def test_user_is_friend_in_database(self):
        user1 = self.create_user('mattmac4241','mattmac4241@gmail.com','password')
        user2 = self.create_user('testname','test@mail.com','password')
        request = self.create_friend_request(user1,user2)
        request.accept()
        assert(user1.is_friend(user2)) 

    def test_user_is_not_friend_in_database(self):
        user1 = self.create_user('mattmac4241','mattmac4241@gmail.com','password')
        user2 = self.create_user('testname','test@mail.com','password')
        request = self.create_friend_request(user1,user2)
        request.reject()
        assert False == user1.is_friend(user2) 

    def test_user_can_delete_friend_in_database(self):
        user1 = self.create_user('mattmac4241','mattmac4241@gmail.com','password')
        user2 = self.create_user('testname','test@mail.com','password')
        request = self.create_friend_request(user1,user2)
        request.accept()
        assert True == user1.is_friend(user2)
        user1.delete_friend(user2)
        assert False == user1.is_friend(user2)        

if __name__ == "__main__":
    unittest.main()
