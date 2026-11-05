from . import db
from datetime import datetime


class Message(db.Model):
    __tablename__ = "message"

    id = db.Column(db.Integer, primary_key=True)

    sender_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    receiver_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    contenu = db.Column(
        db.Text,
        nullable=False
    )

    date_envoi = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    lu = db.Column(
        db.Boolean,
        default=False
    )