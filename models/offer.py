from . import db


class Offer(db.Model):

    __tablename__ = "offer"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    recruiter_id = db.Column(
        db.Integer,
        db.ForeignKey("recruiter.id"),
        nullable=False
    )

    titre = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    competences = db.Column(
        db.Text
    )

    domaine = db.Column(
        db.String(150)
    )

    type_stage = db.Column(
        db.String(100)
    )

    duree = db.Column(
        db.String(100)
    )

    lieu = db.Column(
        db.String(150)
    )

    date_debut = db.Column(
        db.String(50)
    )

    date_limite = db.Column(
        db.String(50)
    )

    statut = db.Column(
        db.String(50),
        default="active"
    )