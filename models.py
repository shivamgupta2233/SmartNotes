from database import db


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