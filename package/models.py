from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from package import db, login_manager
from flask import current_app
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    profile_pic = db.Column(db.String(20), unique=False, nullable=False, default='default.jpg')
    password = db.Column(db.String(60), unique=False, nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except KeyError:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.password}')"


class Atable(db.Model):
    __tablename__ = 'atable'
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), primary_key=True)
    tag = db.relationship('Tag', back_populates='post_list')
    post = db.relationship('Post', back_populates='tag_list')


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, unique=False, nullable=False, default=datetime.utcnow)
    picture = db.Column(db.String(50), unique=False, nullable=False)
    picture_w = db.Column(db.Integer, nullable=False)
    picture_h = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    edit_tags = db.Column(db.String, nullable=False)
    tag_list = db.relationship('Atable', back_populates='post')
    comment_list = db.relationship('Comment', back_populates='under')

    def __repr__(self):
        return f"Post('{self.id}', '{self.date_posted}')"


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    post_list = db.relationship('Atable', back_populates='tag')

    def __repr__(self):
        return f"{self.name}"


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String, unique=False, nullable=False)
    date_posted = db.Column(db.DateTime, unique=False, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, unique=False, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    under = db.relationship('Post', back_populates='comment_list')
