from . import db


class Task(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    internship_id = db.Column(
        db.Integer,
        db.ForeignKey("intership.id"),
        nullable=False
    )

    titre = db.Column(
        db.String(150)
    )

    description = db.Column(
        db.Text
    )

    date_debut = db.Column(
        db.Date
    )

    date_limite = db.Column(
        db.Date
    )

    priorite = db.Column(
        db.String(30)
    )

    statut = db.Column(
        db.String(50)
    )

    progression = db.Column(
        db.Integer
    )

    internship = db.relationship(
        "Intership",
        back_populates="tasks"
    )