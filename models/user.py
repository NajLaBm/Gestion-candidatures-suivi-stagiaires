from . import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    nom = db.Column(db.String(100))
    prenom = db.Column(db.String(100))

    email = db.Column(db.String(150), unique=True)

    password = db.Column(db.String(255))

    role = db.Column(db.String(30))