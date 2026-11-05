
from . import db


class Supervisor(db.Model):

    __tablename__ = "supervisor"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    fonction = db.Column(
        db.String(150)
    )

    specialite = db.Column(
        db.String(150)
    )

    telephone = db.Column(
        db.String(30)
    )

    # Relation avec User
    user = db.relationship(
        "User",
        backref="supervisor",
        foreign_keys=[user_id]
    )

    # Relation avec les stages
    internships = db.relationship(
        "Intership",
        back_populates="supervisor",
        lazy=True
    )

