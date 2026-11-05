from . import db
class Document(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    internship_id = db.Column(db.Integer)

    student_id = db.Column(db.Integer)

    nom = db.Column(db.String(150))

    type = db.Column(db.String(50))

    fichier = db.Column(db.String(255))

    statut = db.Column(db.String(50))