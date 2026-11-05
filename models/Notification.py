from . import db
from datetime import datetime

class Notification(db.Model):
    __tablename__ = "notification"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    message_id = db.Column(
        db.Integer,
        db.ForeignKey("message.id"),
        nullable=True
    )

    message = db.Column(db.Text, nullable=False)

    date_creation = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    lu = db.Column(
        db.Boolean,
        default=False
    )