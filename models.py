from database import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Note(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    content = db.Column(
        db.Text,
        nullable=False
    )

    category = db.Column(
        db.String(100),
        nullable=False
    )

    favorite = db.Column(
        db.Boolean,
        default=False
    )

    pinned = db.Column(
        db.Boolean,
        default=False
    )

    created = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )
class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(150),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )
    notes = db.relationship(
        "Note",
        backref="owner",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)    