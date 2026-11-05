from . import db
class Student(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer)

    telephone = db.Column(db.String(30))

    universite = db.Column(db.String(150))

    formation = db.Column(db.String(150))

    niveau = db.Column(db.String(50))

    competences = db.Column(db.Text)

    cv = db.Column(db.String(255))