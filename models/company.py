from . import db
class Company(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer)

    nom_entreprise = db.Column(db.String(150))

    secteur = db.Column(db.String(100))

    adresse = db.Column(db.String(200))

    telephone = db.Column(db.String(30))

    description = db.Column(db.Text)