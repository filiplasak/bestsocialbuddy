from datetime import datetime
from app import db
from flask_login import UserMixin


class User(db.Model, UserMixin):

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False,
                        onupdate=datetime.utcnow)
    name = db.Column(db.String(80), nullable=False)
    profile_url = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    access_token = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.name

    def __str__(self):
        return '<User %r>' % self.name
