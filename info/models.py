from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from info import constants
from . import db


class BaseModel(object):
    created_time = db.Column(db.DateTime, default=datetime.now())
    updated_time = db.Column(db.DateTime, default=datetime.now(),onupdate=datetime.now())

tb_user_collection = db.Table(
    'user_collection',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'),primary_key=True),
    db.Column('news_id', db.Integer, db.ForeignKey('news.id'),primary_key=True),
    db.Column('create_time', db.DateTime, default=datetime.now())
)

tb_user_follows = db.Table(
    'user_fans',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id'),primary_key=True),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'),primary_key=True),
)

class User(BaseModel, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(32), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    mobile = db.Column(db.String(11), unique=True, nullable=False)
    avatar_url = db.Column(db.String(256))
    last_login = db.Column(db.DateTime, default=datetime.now())
    is_admin = db.Column(db.Boolean, default=False)
    signature = db.Column(db.String(512))
    gender = db.Column(db.String(32))
