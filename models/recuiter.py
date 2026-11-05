from . import db


class Recruiter(db.Model):

    __tablename__ = "recruiter"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False,
        unique=True
    )

    nom_entreprise = db.Column(
        db.String(150)
    )

    secteur = db.Column(
        db.String(150)
    )

    telephone = db.Column(
        db.String(30)
    )

    adresse = db.Column(
        db.String(250)
    )

    description = db.Column(
        db.Text
    )