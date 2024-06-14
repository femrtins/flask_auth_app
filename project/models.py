from flask_login import UserMixin
from . import db
from datetime import datetime
from sqlalchemy import LargeBinary


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(100), unique=True , nullable=False)
    password = db.Column(db.String(100), nullable=False)    
    biography = db.Column(db.String(155))
    image = db.Column(LargeBinary, nullable=True)
    posts = db.relationship('Post', backref='author', lazy=True)

    def get_followers(self):
        followers = User.query.join(Follow, Follow.follower_id == User.id).filter(Follow.followed_id == self.id).all()
        return followers
    
    def get_num_followers(self):
        followers_count = Follow.query.filter_by(followed_id=self.id).count()
        return followers_count
    
    def get_following(self):
        following = User.query.join(Follow, Follow.followed_id == User.id).filter(Follow.follower_id == self.id).all()
        return following

    def get_num_following(self):
        following_count = Follow.query.filter_by(follower_id=self.id).count()
        return following_count

    def is_following(self, user):
            return Follow.query.filter_by(follower_id=self.id, followed_id=user.id).first() is not None

    def get_following_ids(self):
        following_ids = db.session.query(Follow.followed_id).filter_by(follower_id=self.id).all()
        return [id for (id,) in following_ids]

class Post(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    username = db.Column(db.String(20), nullable=False)


class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


