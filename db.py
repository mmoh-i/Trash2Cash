from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import uuid

db = SQLAlchemy()

def init_db(app):
    with app.app_context():
        db.init_app(app)
        db.create_all()
        print("Database tables created!")

class User(UserMixin, db.Model):
    id = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=True)
    profile_pic = db.Column(db.String(255))

    def __init__(self, name, email, password=None, profile_pic=None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.email = email
        self.password = password
        self.profile_pic = profile_pic

    @staticmethod
    def get(user_id):
        return User.query.get(user_id)

    @staticmethod
    def create(name, email, profile_pic=None, password=None):
        user = User(name=name, email=email, profile_pic=profile_pic, password=password)
        db.session.add(user)
        db.session.commit()
        return user