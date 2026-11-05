from . import db


class Evaluation(db.Model):

    __tablename__ = "evaluation"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    internship_id = db.Column(
        db.Integer,
        db.ForeignKey("intership.id"),
        nullable=False
    )

    supervisor_id = db.Column(
        db.Integer,
        db.ForeignKey("supervisor.id"),
        nullable=False
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("student.id"),
        nullable=False
    )

    note_technique = db.Column(
        db.Float
    )

    note_travail = db.Column(
        db.Float
    )

    note_comportement = db.Column(
        db.Float
    )

    note_assiduite = db.Column(
        db.Float
    )

    note_finale = db.Column(
        db.Float
    )

    commentaire = db.Column(
        db.Text
    )

    internship = db.relationship(
        "Intership",
        back_populates="evaluation"
    )

    supervisor = db.relationship(
        "Supervisor"
    )

    student = db.relationship(
        "Student"
    )