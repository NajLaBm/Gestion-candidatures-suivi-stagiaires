from . import db
class InternshipOffer(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    company_id = db.Column(db.Integer)

    titre = db.Column(db.String(150))

    description = db.Column(db.Text)

    domaine = db.Column(db.String(100))

    competences = db.Column(db.Text)

    duree = db.Column(db.String(50))

    date_debut = db.Column(db.Date)

    date_fin = db.Column(db.Date)

    localisation = db.Column(db.String(100))

    statut = db.Column(db.String(50))