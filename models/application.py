from . import db
class Application(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer)

    offer_id = db.Column(db.Integer)

    date_candidature = db.Column(db.DateTime)

    cv = db.Column(db.String(255))

    lettre_motivation = db.Column(db.String(255))

    statut = db.Column(db.String(50))

    commentaire = db.Column(db.Text)

    offer = db.relationship(
        "Offer",
        primaryjoin="Application.offer_id == Offer.id",
        foreign_keys=[offer_id],
        viewonly=True
    )

    student = db.relationship(
        "Student",
        primaryjoin="Application.student_id == Student.id",
        foreign_keys=[student_id],
        viewonly=True
    )