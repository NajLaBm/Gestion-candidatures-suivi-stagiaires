from . import db


class Intership(db.Model):

    __tablename__ = "intership"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("student.id"),
        nullable=False
    )

    supervisor_id = db.Column(
        db.Integer,
        db.ForeignKey("supervisor.id"),
        nullable=True
    )

    titre = db.Column(
        db.String(200),
        nullable=True
    )

    date_debut = db.Column(
        db.Date,
        nullable=True
    )

    date_fin = db.Column(
        db.Date,
        nullable=True
    )

    statut = db.Column(
        db.String(50),
        default="En cours"
    )

    objectifs = db.Column(
        db.Text,
        nullable=True
    )

    remarques = db.Column(
        db.Text,
        nullable=True
    )

    evaluation = db.Column(
        db.Text,
        nullable=True
    )

    # Relation avec Student
    student = db.relationship(
        "Student",
        backref="internships"
    )

    # Relation avec Supervisor
    supervisor = db.relationship(
        "Supervisor",
        back_populates="internships"
    )

    # Relation avec les tâches
    tasks = db.relationship(
        "Task",
        back_populates="internship",
        cascade="all, delete-orphan",
        lazy=True
    )
    evaluation = db.relationship(
    "Evaluation",
    back_populates="internship",
    uselist=False,
    cascade="all, delete-orphan"
)

