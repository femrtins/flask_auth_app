from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(100), unique=True , nullable=False)
    password = db.Column(db.String(100), nullable=False)    
    biography = db.Column(db.String(155))
    image_path = db.Column(db.String(255))
