from flask import Flask
from models import db
from flask import Flask, request,render_template, redirect,session,url_for, send_from_directory,Response, flash,jsonify,send_file
from models.user import User
from models.application import Application
from models.company import Company
from models.document import Document
from models.evaluation import Evaluation
from models.intership import Intership
from models.intership_offer import InternshipOffer
from models.recuiter import Recruiter
from models.offer import Offer
from models.Notification import Notification
"""from models.interview import Interview"""
from models.Message import Message
from models.student import Student
from models.supervisor import Supervisor
from models.task import Task
from models.user import User
from werkzeug.security import generate_password_hash
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from flask import send_from_directory
from dateutil.relativedelta import relativedelta
import re
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from sqlalchemy import or_,and_
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader




app = Flask(__name__, template_folder='template')

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///stage.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'mykey'

db.init_app(app)
with app.app_context():
    db.create_all() 

@app.route("/logout")
def logout():

    session.clear()

    flash("Vous avez été déconnecté.", "success")

    return redirect(url_for("logininterface"))

@app.route('/')
def welcome():
    return render_template('acceuil.html')

@app.route('/registerinterface')
def registerinterface():
    return render_template('register.html')

@app.route("/student/offers/<int:offer_id>")
def student_offer_detail(offer_id):

    # Vérifier connexion
    if "user_id" not in session:
        return redirect(url_for("logininterface"))

    # Vérifier rôle
    if session.get("role") != "student":
        flash(
            "Accès réservé aux étudiants.",
            "danger"
        )
        return redirect(url_for("logininterface"))

    # Récupérer l'offre
    offer = Offer.query.get_or_404(offer_id)

    # Afficher le détail
    return render_template(
        "student/offer_detail.html",
        offer=offer
    )
@app.route("/student/offers/<int:offer_id>/apply", methods=["POST"])
def apply_offer(offer_id):

    # =========================
    # VERIFIER CONNEXION
    # =========================

    if "user_id" not in session:
        return redirect(url_for("logininterface"))

    # =========================
    # VERIFIER ROLE
    # =========================

    if session.get("role") != "student":

        flash(
            "Seuls les étudiants peuvent postuler.",
            "danger"
        )

        return redirect(url_for("student_offers"))

    # =========================
    # RECUPERER STUDENT
    # =========================

    student = Student.query.filter_by(
        user_id=session["user_id"]
    ).first()

    if not student:

        flash(
            "Profil étudiant introuvable.",
            "danger"
        )

        return redirect(url_for("student_profile"))

    # =========================
    # RECUPERER OFFRE
    # =========================

    offer = Offer.query.get_or_404(offer_id)

    # =========================
    # VERIFIER CANDIDATURE EXISTANTE
    # =========================

    existing_application = Application.query.filter_by(
        student_id=student.id,
        offer_id=offer.id
    ).first()

    if existing_application:

        flash(
            "Vous avez déjà postulé à cette offre.",
            "warning"
        )

        return redirect(
            url_for(
                "student_offer_detail",
                offer_id=offer.id
            )
        )

    # =========================
    # CREER CANDIDATURE
    # =========================

    application = Application(

        student_id=student.id,

        offer_id=offer.id,

        date_candidature=datetime.now(),

        cv=student.cv,

        lettre_motivation=None,

        statut="En attente",

        commentaire=None

    )

    db.session.add(application)

    db.session.commit()

    # =========================
    # MESSAGE
    # =========================

    flash(
        "Votre candidature a été envoyée avec succès.",
        "success"
    )

    return redirect(
        url_for(
            "student_offer_detail",
            offer_id=offer.id
        )
    )

@app.route("/student/applications")
def student_applications():

    # Vérifier connexion
    if "user_id" not in session:
        return redirect(url_for("logininterface"))

    # Vérifier rôle
    if session.get("role") != "student":
        flash(
            "Accès réservé aux étudiants.",
            "danger"
        )
        return redirect(url_for("logininterface"))

    # Récupérer l'étudiant
    student = Student.query.filter_by(
        user_id=session["user_id"]
    ).first()

    if not student:
        flash(
            "Profil étudiant introuvable.",
            "danger"
        )
        return redirect(url_for("student_profile"))

    # Récupérer ses candidatures
    applications = Application.query.filter_by(
        student_id=student.id
    ).order_by(
        Application.date_candidature.desc()
    ).all()

    return render_template(
        "student/applications.html",
        applications=applications
    )
@app.route("/recruiter/offers/create", methods=["GET", "POST"])
def create_offer():

    if "user_id" not in session:
        return redirect(url_for("logininterface"))

    user = User.query.get(session["user_id"])

    if not user:
        return redirect(url_for("logininterface"))

    if user.role != "recruiter":
        flash("Accès réservé aux recruteurs.", "danger")
        return redirect(url_for("logininterface"))

    recruiter = Recruiter.query.filter_by(
        user_id=user.id
    ).first()

    if not recruiter:
        flash("Profil recruteur introuvable.", "danger")
        return redirect(url_for("recruiter_dashboard"))

    if request.method == "POST":

        try:

            offer = Offer(
                recruiter_id=recruiter.id,
                titre=request.form.get("titre"),
                description=request.form.get("description"),
                competences=request.form.get("competences"),
                domaine=request.form.get("domaine"),
                type_stage=request.form.get("type_stage"),
                duree=request.form.get("duree"),
                lieu=request.form.get("lieu"),
                date_debut=request.form.get("date_debut"),
                date_limite=request.form.get("date_limite"),
                statut="active"
            )

            db.session.add(offer)
            db.session.commit()

            flash(
                "Offre publiée avec succès.",
                "success"
            )

            return redirect(
                url_for("recruiter_dashboard")
            )

        except Exception as e:

            db.session.rollback()

            print("Erreur création offre :", e)

            flash(
                "Erreur lors de la création de l'offre.",
                "danger"
            )

            return redirect(
                url_for("create_offer")
            )

    return render_template(
        "recruiter/create_offer.html",
        user=user,
        recruiter=recruiter
    )

@app.route("/student/offers")
def student_offers():

    # Vérifier connexion
    if "user_id" not in session:
        return redirect(url_for("logininterface"))

    # Vérifier rôle
    if session.get("role") != "student":
        flash(
            "Accès réservé aux étudiants.",
            "danger"
        )
        return redirect(url_for("logininterface"))

    # Récupérer toutes les offres
    offers = Offer.query.order_by(
        Offer.id.desc()
    ).all()

    return render_template(
        "student/offers.html",
        offers=offers
    )

@app.route('/logininterface')
def logininterface():
    return render_template('login.html')

@app.route("/forgot-password")
def forgot_password():

    return render_template("forgot_password.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        # =====================================================
        # INFORMATIONS USER
        # =====================================================

        nom = request.form.get("nom")
        prenom = request.form.get("prenom")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        role = request.form.get("role")


        # =====================================================
        # VERIFICATION DU ROLE
        # =====================================================

        if role not in ["student", "recruiter", "supervisor"]:

            flash(
                "Veuillez sélectionner votre type de compte.",
                "danger"
            )

            return redirect(url_for("register"))


        # =====================================================
        # VERIFICATION PASSWORD
        # =====================================================

        if not password or not confirm_password:

            flash(
                "Veuillez remplir les champs de mot de passe.",
                "danger"
            )

            return redirect(url_for("register"))


        if password != confirm_password:

            flash(
                "Les mots de passe ne correspondent pas.",
                "danger"
            )

            return redirect(url_for("register"))


        # =====================================================
        # VERIFICATION EMAIL
        # =====================================================

        existing_user = User.query.filter_by(
            email=email
        ).first()


        if existing_user:

            flash(
                "Cette adresse email est déjà utilisée.",
                "danger"
            )

            return redirect(url_for("register"))


        # =====================================================
        # CREATION USER
        # =====================================================

        hashed_password = generate_password_hash(
            password
        )


        user = User(

            nom=nom,

            prenom=prenom,

            email=email,

            password=hashed_password,

            role=role

        )


        db.session.add(user)


        # Permet d'obtenir user.id

        db.session.flush()


        # =====================================================
        # CREATION PROFIL STUDENT
        # =====================================================

        if role == "student":

            telephone = request.form.get(
                "telephone"
            )

            universite = request.form.get(
                "universite"
            )

            formation = request.form.get(
                "formation"
            )

            niveau = request.form.get(
                "niveau"
            )

            competences = request.form.get(
                "competences"
            )


            student = Student(

                user_id=user.id,

                telephone=telephone,

                universite=universite,

                formation=formation,

                niveau=niveau,

                competences=competences

            )


            db.session.add(student)


        # =====================================================
        # CREATION PROFIL RECRUITER + COMPANY
        # =====================================================

        elif role == "recruiter":

            # Informations entreprise

            nom_entreprise = request.form.get(
                "nom_entreprise"
            )

            secteur = request.form.get(
                "secteur"
            )

            telephone_entreprise = request.form.get(
                "telephone_entreprise"
            )

            adresse = request.form.get(
                "adresse"
            )

            description = request.form.get(
                "description"
            )


            # -------------------------------------------------
            # CREATION COMPANY
            # -------------------------------------------------

            company = Company(

                user_id=user.id,

                nom_entreprise=nom_entreprise,

                secteur=secteur,

                adresse=adresse,

                telephone=telephone_entreprise,

                description=description

            )


            db.session.add(company)


            # -------------------------------------------------
            # CREATION RECRUITER
            # -------------------------------------------------

            recruiter = Recruiter(

                user_id=user.id,

                nom_entreprise=nom_entreprise,

                secteur=secteur,

                telephone=telephone_entreprise,

                adresse=adresse,

                description=description

            )


            db.session.add(recruiter)


        # =====================================================
        # CREATION PROFIL SUPERVISOR
        # =====================================================

      
        elif role == "supervisor":

            fonction = request.form.get("fonction")
            specialite = request.form.get("specialite")
            telephone = request.form.get("telephone")

            supervisor = Supervisor(
                user_id=user.id,
                fonction=fonction,
                specialite=specialite,
                telephone=telephone
            )

            db.session.add(supervisor)




        # =====================================================
        # ENREGISTREMENT EN BASE
        # =====================================================

        try:

            db.session.commit()

        except Exception as e:

            db.session.rollback()

            print(
                "Erreur inscription :",
                e
            )

            flash(
                "Une erreur est survenue lors de la création du compte.",
                "danger"
            )

            return redirect(
                url_for("register")
            )


        # =====================================================
        # MESSAGE DE SUCCES
        # =====================================================

        flash(
            "Votre compte a été créé avec succès.",
            "success"
        )


        return redirect(
            url_for("logininterface")
        )


    # =====================================================
    # AFFICHAGE PAGE REGISTER
    # =====================================================

    return render_template(
        "register.html"
    )

@app.route("/recruiter/application/<int:application_id>/reject", methods=["POST"])
def reject_application(application_id):

    # =========================
    # VERIFIER CONNEXION
    # =========================

    if "user_id" not in session:
        return redirect(url_for("logininterface"))

    # =========================
    # VERIFIER ROLE
    # =========================

    if session.get("role") != "recruiter":
        flash(
            "Accès réservé aux recruteurs.",
            "danger"
        )
        return redirect(url_for("logininterface"))

    # =========================
    # RECUPERER UTILISATEUR
    # =========================

    user = User.query.get(
        session["user_id"]
    )

    if not user:
        session.clear()
        return redirect(url_for("logininterface"))

    # =========================
    # RECUPERER RECRUTEUR
    # =========================

    recruiter = Recruiter.query.filter_by(
        user_id=user.id
    ).first()

    if not recruiter:
        flash(
            "Profil recruteur introuvable.",
            "danger"
        )
        return redirect(
            url_for("recruiter_dashboard")
        )

    # =========================
    # RECUPERER CANDIDATURE
    # =========================

    application = Application.query.get_or_404(
        application_id
    )

    # =========================
    # VERIFIER L'OFFRE
    # =========================

    offer = Offer.query.get(
        application.offer_id
    )

    if not offer or offer.recruiter_id != recruiter.id:
        flash(
            "Vous n'avez pas accès à cette candidature.",
            "danger"
        )

        return redirect(
            url_for("recruiter_applications")
        )

    # =========================
    # REFUSER LA CANDIDATURE
    # =========================

    application.statut = "Refusée"

    db.session.commit()

    flash(
        "La candidature a été refusée.",
        "success"
    )

    return redirect(
        url_for("recruiter_applications")
    )



@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        # Récupérer les données du formulaire
        email = request.form.get("email")
        password = request.form.get("password")

        # Vérifier que les champs sont remplis
        if not email or not password:
            flash("Veuillez remplir tous les champs.", "danger")
            return redirect(url_for("login"))

        # Rechercher l'utilisateur avec son email
        user = User.query.filter_by(email=email).first()

        # Vérifier si l'utilisateur existe
        if user is None:
            flash("Email ou mot de passe incorrect.", "danger")
            return redirect(url_for("login"))

        # Vérifier le mot de passe
        if not check_password_hash(user.password, password):
            flash("Email ou mot de passe incorrect.", "danger")
            return redirect(url_for("login"))

        # Créer la session
        session["user_id"] = user.id
        session["nom"] = user.nom
        session["prenom"] = user.prenom
        session["email"] = user.email
        session["role"] = user.role

        flash(
            f"Bienvenue {user.prenom} !",
            "success"
        )

        # Redirection selon le rôle
        if user.role == "student":
            return redirect(url_for("student_dashboard"))

        elif user.role == "recruiter":
            return redirect(url_for("recruiter_dashboard"))

        elif user.role == "supervisor":
            return redirect(url_for("supervisor_dashboard"))

        else:
            flash("Rôle utilisateur invalide.", "danger")
            session.clear()
            return redirect(url_for("login"))

    # GET → afficher la page login
    return render_template("login.html")


       
@app.route("/student/dashboard")
def student_dashboard():

    # Vérifier la connexion
    if "user_id" not in session:
        return redirect(url_for("logininterface"))

    # Vérifier le rôle
    if session.get("role") != "student":
        flash("Accès réservé aux étudiants.", "danger")
        return redirect(url_for("logininterface"))

    # Récupérer l'étudiant connecté
    student = Student.query.filter_by(
        user_id=session["user_id"]
    ).first()

    if not student:
        flash("Profil étudiant introuvable.", "danger")
        return redirect(url_for("student_profile"))

    # =========================
    # NOMBRE DE CANDIDATURES
    # =========================

    total_applications = Application.query.filter_by(
        student_id=student.id
    ).count()

    # =========================
    # NOMBRE D'OFFRES
    # =========================

    total_offers = Offer.query.count()

    # =========================
    # AFFICHAGE DASHBOARD
    # =========================

    return render_template(
        "student/dashboard.html",
        student=student,
        total_applications=total_applications,
        total_offers=total_offers
    )


@app.route("/supervisor/dashboard")
def supervisor_dashboard():

    # =====================================================
    # 1. VERIFIER LA CONNEXION
    # =====================================================

    if "user_id" not in session:
        return redirect(url_for("logininterface"))

    # =====================================================
    # 2. RECUPERER L'UTILISATEUR
    # =====================================================

    user = User.query.get(session["user_id"])

    if not user or user.role != "supervisor":

        flash(
            "Accès non autorisé.",
            "danger"
        )

        return redirect(
            url_for("logininterface")
        )

    # =====================================================
    # 3. RECUPERER LE PROFIL ENCADRANT
    # =====================================================

    supervisor = Supervisor.query.filter_by(
        user_id=user.id
    ).first()

    if not supervisor:

        flash(
            "Profil encadrant introuvable.",
            "danger"
        )

        return redirect(
            url_for("logininterface")
        )

    # =====================================================
    # 4. RECUPERER LES STAGES AFFECTES A CET ENCADRANT
    # =====================================================

    internships = Intership.query.filter_by(
        supervisor_id=supervisor.id
    ).all()

    # =====================================================
    # 5. AFFICHER LE DASHBOARD
    # =====================================================

    return render_template(
        "supervisor/dashboard.html",
        user=user,
        supervisor=supervisor,
        internships=internships
    )



@app.route("/student/cv", methods=["GET", "POST"])
def student_cv():

    # =========================
    # Vérifier la connexion
    # =========================

    if "user_id" not in session:
        return redirect(url_for("login"))


    # =========================
    # Récupérer User
    # =========================

    user = User.query.get(session["user_id"])

    if not user:
        flash("Utilisateur introuvable.", "danger")
        return redirect(url_for("login"))


    # =========================
    # Récupérer Student
    # =========================

    student = Student.query.filter_by(
        user_id=user.id
    ).first()


    if not student:

        flash(
            "Profil étudiant introuvable.",
            "danger"
        )

        return redirect(
            url_for("student_profile")
        )


    # =========================
    # UPLOAD CV
    # =========================

    if request.method == "POST":

        cv_file = request.files.get("cv")


        # Aucun fichier
        if not cv_file or cv_file.filename == "":

            flash(
                "Veuillez sélectionner un fichier PDF.",
                "danger"
            )

            return redirect(
                url_for("student_cv")
            )


        # Vérifier l'extension
        filename = secure_filename(
            cv_file.filename
        )


        if not filename.lower().endswith(".pdf"):

            flash(
                "Seuls les fichiers PDF sont acceptés.",
                "danger"
            )

            return redirect(
                url_for("student_cv")
            )


        # =========================
        # Supprimer ancien CV
        # =========================

        if student.cv:

            old_file = os.path.join(
                app.config["UPLOAD_FOLDER"],
                student.cv
            )

            if os.path.exists(old_file):

                os.remove(old_file)


        # =========================
        # Nouveau nom du fichier
        # =========================

        filename = f"student_{user.id}_{filename}"


        # =========================
        # Enregistrer le fichier
        # =========================

        file_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        cv_file.save(file_path)


        # =========================
        # Enregistrer dans DB
        # =========================

        student.cv = filename

        db.session.commit()


        flash(
            "Votre CV a été téléchargé avec succès.",
            "success"
        )


        return redirect(
            url_for("student_cv")
        )


    # =========================
    # Afficher la page
    # =========================

    return render_template(
        "student/cv.html",
        user=user,
        student=student
    )


@app.route("/recruiter/offers")
def recruiter_offers():

    # =========================
    # VERIFICATION CONNEXION
    # =========================

    if "user_id" not in session:

        return redirect(
            url_for("logininterface")
        )


    # =========================
    # VERIFICATION ROLE
    # =========================

    if session.get("role") != "recruiter":

        flash(
            "Accès réservé aux recruteurs.",
            "danger"
        )

        return redirect(
            url_for("logininterface")
        )


    # =========================
    # RECUPERER RECRUITER
    # =========================

    recruiter = Recruiter.query.filter_by(
        user_id=session["user_id"]
    ).first()


    if not recruiter:

        flash(
            "Profil recruteur introuvable.",
            "danger"
        )

        return redirect(
            url_for("recruiter_dashboard")
        )


    # =========================
    # RECUPERER SES OFFRES
    # =========================

    offers = Offer.query.filter_by(
        recruiter_id=recruiter.id
    ).order_by(
        Offer.id.desc()
    ).all()


    return render_template(
        "recruiter/offers.html",
        recruiter=recruiter,
        offers=offers
    )

@app.route(
    "/recruiter/offers/edit/<int:offer_id>",
    methods=["GET", "POST"]
)
def edit_offer(offer_id):

    # =========================
    # VERIFICATION CONNEXION
    # =========================

    if "user_id" not in session:

        return redirect(
            url_for("logininterface")
        )


    # =========================
    # VERIFICATION ROLE
    # =========================

    if session.get("role") != "recruiter":

        flash(
            "Accès réservé aux recruteurs.",
            "danger"
        )

        return redirect(
            url_for("logininterface")
        )


    # =========================
    # RECUPERER RECRUITER
    # =========================

    recruiter = Recruiter.query.filter_by(
        user_id=session["user_id"]
    ).first()


    if not recruiter:

        flash(
            "Profil recruteur introuvable.",
            "danger"
        )

        return redirect(
            url_for("recruiter_dashboard")
        )


    # =========================
    # RECUPERER OFFRE
    # =========================

    offer = Offer.query.filter_by(
        id=offer_id,
        recruiter_id=recruiter.id
    ).first()


    if not offer:

        flash(
            "Offre introuvable ou accès non autorisé.",
            "danger"
        )

        return redirect(
            url_for("recruiter_offers")
        )


    # =========================
    # MODIFICATION
    # =========================

    if request.method == "POST":

        titre = request.form.get("titre")
        description = request.form.get("description")
        competences = request.form.get("competences")
        domaine = request.form.get("domaine")
        type_stage = request.form.get("type_stage")
        duree = request.form.get("duree")
        lieu = request.form.get("lieu")
        date_debut = request.form.get("date_debut")
        date_limite = request.form.get("date_limite")
        statut = request.form.get("statut")


        # =========================
        # VALIDATION
        # =========================

        if not titre or not description:

            flash(
                "Le titre et la description sont obligatoires.",
                "danger"
            )

            return redirect(
                url_for(
                    "edit_offer",
                    offer_id=offer.id
                )
            )


        try:

            # =========================
            # MISE À JOUR
            # =========================

            offer.titre = titre

            offer.description = description

            offer.competences = competences

            offer.domaine = domaine

            offer.type_stage = type_stage

            offer.duree = duree

            offer.lieu = lieu

            offer.date_debut = date_debut

            offer.date_limite = date_limite

            offer.statut = statut


            db.session.commit()


            flash(
                "L'offre a été modifiée avec succès.",
                "success"
            )


            return redirect(
                url_for("recruiter_offers")
            )


        except Exception as e:

            db.session.rollback()

            print(
                "Erreur modification offre :",
                e
            )

            flash(
                "Une erreur est survenue lors de la modification.",
                "danger"
            )


    # =========================
    # AFFICHER FORMULAIRE
    # =========================

    return render_template(
        "recruiter/edit_offer.html",
        offer=offer,
        recruiter=recruiter
    )

@app.route(
    "/recruiter/offers/delete/<int:offer_id>",
    methods=["POST"]
)
def delete_offer(offer_id):

    # =========================
    # VERIFICATION CONNEXION
    # =========================

    if "user_id" not in session:

        return redirect(
            url_for("logininterface")
        )


    # =========================
    # VERIFICATION ROLE
    # =========================

    if session.get("role") != "recruiter":

        flash(
            "Accès réservé aux recruteurs.",
            "danger"
        )

        return redirect(
            url_for("logininterface")
        )


    # =========================
    # RECUPERER RECRUITER
    # =========================

    recruiter = Recruiter.query.filter_by(
        user_id=session["user_id"]
    ).first()


    if not recruiter:

        flash(
            "Profil recruteur introuvable.",
            "danger"
        )

        return redirect(
            url_for("recruiter_dashboard")
        )


    # =========================
    # RECUPERER OFFRE
    # =========================

    offer = Offer.query.filter_by(
        id=offer_id,
        recruiter_id=recruiter.id
    ).first()


    if not offer:

        flash(
            "Offre introuvable ou accès non autorisé.",
            "danger"
        )

        return redirect(
            url_for("recruiter_offers")
        )


    # =========================
    # SUPPRESSION
    # =========================

    try:

        db.session.delete(offer)

        db.session.commit()

        flash(
            "L'offre a été supprimée.",
            "success"
        )

    except Exception as e:

        db.session.rollback()

        print(
            "Erreur suppression offre :",
            e
        )

        flash(
            "Impossible de supprimer l'offre.",
            "danger"
        )


    return redirect(
        url_for("recruiter_offers")
    )

@app.route("/recruiter/dashboard")
def recruiter_dashboard():

    # =========================
    # VÉRIFICATION CONNEXION
    # =========================

    if "user_id" not in session:
        return redirect(url_for("logininterface"))

    # =========================
    # VÉRIFICATION ROLE
    # =========================

    if session.get("role") != "recruiter":
        flash("Accès réservé aux recruteurs.", "danger")
        return redirect(url_for("logininterface"))

    # =========================
    # RÉCUPÉRER USER
    # =========================

    user = User.query.get(session["user_id"])

    if not user:
        session.clear()
        return redirect(url_for("logininterface"))

    # =========================
    # RÉCUPÉRER RECRUTEUR
    # =========================

    recruiter = Recruiter.query.filter_by(
        user_id=user.id
    ).first()

    if not recruiter:
        flash("Profil recruteur introuvable.", "danger")
        return redirect(url_for("logininterface"))

    # =========================
    # RÉCUPÉRER LES OFFRES
    # =========================

    offers = Offer.query.filter_by(
        recruiter_id=recruiter.id
    ).order_by(
        Offer.id.desc()
    ).all()

    total_offers = len(offers)

    # IDs des offres du recruteur
    offer_ids = [offer.id for offer in offers]

    # =========================
    # CANDIDATURES
    # =========================

    if offer_ids:

        applications = Application.query.filter(
            Application.offer_id.in_(offer_ids)
        ).order_by(
            Application.date_candidature.desc()
        ).all()

    else:

        applications = []

    # Nombre total de candidatures
    total_applications = len(applications)

    # Candidatures en attente
    pending_application = sum(
        1 for application in applications
        if application.statut == "En attente"
    )

    # =========================
    # CANDIDATURES RÉCENTES
    # =========================

    recent_applications = []

    for application in applications[:5]:

        # Récupérer student
        student = Student.query.get(
            application.student_id
        )

        # Récupérer user du student
        user_student = None

        if student:

            user_student = User.query.get(
                student.user_id
            )

        # Récupérer offre
        offer = Offer.query.get(
            application.offer_id
        )

        recent_applications.append({

            "application": application,

            "student": student,

            "user": user_student,

            "offer": offer

        })

    # =========================
    # AFFICHAGE
    # =========================

    return render_template(
        "recruiter/dashboard.html",

        user=user,

        recruiter=recruiter,

        offers=offers,

        total_offers=total_offers,

        total_applications=total_applications,

        pending_application=pending_application,

        applications=applications,

        recent_applications=recent_applications
    )

    # =========================
    # RECUPERER STUDENT
@app.route("/student/internship")
def student_internship():

    if "user_id" not in session:
        return redirect(url_for("logininterface"))

    user = User.query.get(session["user_id"])

    if not user or user.role != "student":
        flash("Accès non autorisé.", "danger")
        return redirect(url_for("logininterface"))

    student = Student.query.filter_by(
        user_id=user.id
    ).first()

    if not student:
        flash("Profil étudiant introuvable.", "danger")
        return redirect(url_for("student_dashboard"))

    internship = Intership.query.filter_by(
        student_id=student.id
    ).first()

    return render_template(
        "student/intership.html",
        user=user,
        student=student,
        internship=internship
    ) 

@app.route("/student/tasks")
def student_tasks():

    return render_template(
        "student/tasks.html"
    )




@app.route("/student/profile", methods=["GET", "POST"])
def student_profile():

    # Vérifier la connexion
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Récupérer l'utilisateur connecté
    user = User.query.get(session["user_id"])

    if not user:
        flash("Utilisateur introuvable.", "danger")
        return redirect(url_for("login"))

    # Récupérer son profil Student
    student = Student.query.filter_by(
        user_id=user.id
    ).first()

    # Si le profil Student n'existe pas
    if not student:

        student = Student(
            user_id=user.id
        )

        db.session.add(student)
        db.session.commit()

    # ==========================
    # MODIFICATION
    # ==========================

    if request.method == "POST":

        # Informations User
        user.nom = request.form.get("nom")
        user.prenom = request.form.get("prenom")
        user.email = request.form.get("email")

        # Informations Student
        student.telephone = request.form.get("telephone")
        student.universite = request.form.get("universite")
        student.formation = request.form.get("formation")
        student.niveau = request.form.get("niveau")
        student.competences = request.form.get("competences")

        # Sauvegarder
        db.session.commit()

        # Mettre à jour la session
        session["nom"] = user.nom
        session["prenom"] = user.prenom
        session["email"] = user.email

        flash(
            "Profil mis à jour avec succès.",
            "success"
        )

        return redirect(url_for("student_profile"))

    # ==========================
    # AFFICHER PROFILE.HTML
    # ==========================

    return render_template(
        "student/profile.html",
        user=user,
        student=student
    )

@app.route("/recruiter/profile", methods=["GET", "POST"])
def recruiter_profile():

    # =========================
    # Vérifier connexion
    # =========================

    if "user_id" not in session:

        return redirect(
            url_for("logininterface")
        )


    # =========================
    # Récupérer USER
    # =========================

    user = User.query.get(
        session["user_id"]
    )


    if not user:

        flash(
            "Utilisateur introuvable.",
            "danger"
        )

        return redirect(
            url_for("logininterface")
        )


    # =========================
    # Vérifier ROLE
    # =========================

    if user.role != "recruiter":

        flash(
            "Accès non autorisé.",
            "danger"
        )

        return redirect(
            url_for("logininterface")
        )


    # =========================
    # Récupérer RECRUITER
    # =========================

    recruiter = Recruiter.query.filter_by(
        user_id=user.id
    ).first()


    if not recruiter:

        flash(
            "Profil recruteur introuvable.",
            "danger"
        )

        return redirect(
            url_for("recruiter_dashboard")
        )


    # =========================
    # MODIFICATION
    # =========================

    if request.method == "POST":

        # Informations User

        user.nom = request.form.get("nom")
        user.prenom = request.form.get("prenom")
        user.email = request.form.get("email")


        # Informations Recruiter

        recruiter.nom_entreprise = request.form.get(
            "nom_entreprise"
        )

        recruiter.secteur = request.form.get(
            "secteur"
        )

        recruiter.telephone = request.form.get(
            "telephone"
        )

        recruiter.adresse = request.form.get(
            "adresse"
        )

        recruiter.description = request.form.get(
            "description"
        )


        # Enregistrer

        db.session.commit()


        # Mise à jour session

        session["nom"] = user.nom
        session["prenom"] = user.prenom
        session["email"] = user.email


        flash(
            "Profil entreprise mis à jour avec succès.",
            "success"
        )


        return redirect(
            url_for("recruiter_profile")
        )


    # =========================
    # AFFICHAGE
    # =========================

    return render_template(
        "recruiter/profile.html",
        user=user,
        recruiter=recruiter
    )

UPLOAD_FOLDER = os.path.join(
    app.root_path,
    "static",
    "uploads",
    "cv"
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(
    app.config["UPLOAD_FOLDER"],
    exist_ok=True
)


@app.route("/recruiter/applications")
def recruiter_applications():

    # Vérifier la connexion
    if "user_id" not in session:
        return redirect(url_for("logininterface"))

    # Vérifier le rôle
    if session.get("role") != "recruiter":
        flash("Accès réservé aux recruteurs.", "danger")
        return redirect(url_for("logininterface"))

    # Récupérer l'utilisateur
    user = User.query.get(session["user_id"])

    if not user:
        session.clear()
        return redirect(url_for("logininterface"))

    # Récupérer le recruteur
    recruiter = Recruiter.query.filter_by(
        user_id=user.id
    ).first()

    if not recruiter:
        flash("Profil recruteur introuvable.", "danger")
        return redirect(url_for("logininterface"))

    # Récupérer les offres du recruteur
    offers = Offer.query.filter_by(
        recruiter_id=recruiter.id
    ).all()

    # IDs des offres
    offer_ids = [offer.id for offer in offers]

    # =========================
    # PARAMÈTRES DE RECHERCHE
    # =========================

    search = request.args.get("search", "").strip()
    statut = request.args.get("statut", "").strip()
    offer_id = request.args.get("offer_id", "").strip()

    # =========================
    # RÉCUPÉRER LES CANDIDATURES
    # =========================

    if offer_ids:

        query = Application.query.filter(
            Application.offer_id.in_(offer_ids)
        )

        # Filtre par statut
        if statut:
            query = query.filter(
                Application.statut == statut
            )

        # Filtre par offre
        if offer_id:
            try:
                query = query.filter(
                    Application.offer_id == int(offer_id)
                )
            except ValueError:
                pass

        applications = query.order_by(
            Application.id.desc()
        ).all()

    else:

        applications = []

    # =========================
    # RECHERCHE DU CANDIDAT
    # =========================

    application_data = []

    for application in applications:

        # Grâce à la relation déjà présente
        # dans ton modèle Application
        student = application.student

        if not student:
            continue

        # Student possède user_id
        # mais pas de relation student.user
        student_user = User.query.filter_by(
            id=student.user_id
        ).first()

        if not student_user:
            continue

        # Recherche par nom, prénom ou email
        if search:

            texte_recherche = (
                (student_user.nom or "") + " " +
                (student_user.prenom or "") + " " +
                (student_user.email or "")
            ).lower()

            if search.lower() not in texte_recherche:
                continue

        application_data.append({
            "application": application,
            "student": student,
            "student_user": student_user
        })

    # =========================
    # AFFICHAGE
    # =========================

    return render_template(
        "recruiter/applications.html",
        user=user,
        recruiter=recruiter,
        applications=application_data,
        offers=offers,
        search=search,
        statut=statut,
        offer_id=offer_id
    )

@app.route("/recruiter/cv/<filename>")
def recruiter_cv(filename):

    # Vérifier connexion
    if "user_id" not in session:
        return redirect(url_for("logininterface"))

    # Vérifier rôle
    if session.get("role") != "recruiter":
        flash("Accès réservé aux recruteurs.", "danger")
        return redirect(url_for("logininterface"))

    # Ouvrir le fichier sans afficher le formulaire
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )


@app.route(
    "/recruiter/application/<int:application_id>/accept",
    methods=["POST"]
)
def accept_application(application_id):

    # =====================================================
    # 1. VERIFIER LA CONNEXION
    # =====================================================

    if "user_id" not in session:
        return redirect(url_for("logininterface"))

    # =====================================================
    # 2. VERIFIER LE ROLE
    # =====================================================

    if session.get("role") != "recruiter":

        flash(
            "Accès réservé aux recruteurs.",
            "danger"
        )

        return redirect(
            url_for("logininterface")
        )

    # =====================================================
    # 3. RECUPERER L'UTILISATEUR
    # =====================================================

    user = User.query.get(session["user_id"])

    if not user:

        session.clear()

        return redirect(
            url_for("logininterface")
        )

    # =====================================================
    # 4. RECUPERER LE RECRUTEUR
    # =====================================================

    recruiter = Recruiter.query.filter_by(
        user_id=user.id
    ).first()

    if not recruiter:

        flash(
            "Profil recruteur introuvable.",
            "danger"
        )

        return redirect(
            url_for("recruiter_dashboard")
        )

    # =====================================================
    # 5. RECUPERER LA CANDIDATURE
    # =====================================================

    application = Application.query.get_or_404(
        application_id
    )

    # =====================================================
    # 6. RECUPERER L'OFFRE
    # =====================================================

    offer = Offer.query.get(
        application.offer_id
    )

    if not offer:

        flash(
            "Offre introuvable.",
            "danger"
        )

        return redirect(
            url_for("recruiter_applications")
        )

    # =====================================================
    # 7. VERIFIER QUE L'OFFRE APPARTIENT AU RECRUTEUR
    # =====================================================

    if offer.recruiter_id != recruiter.id:

        flash(
            "Vous n'avez pas accès à cette candidature.",
            "danger"
        )

        return redirect(
            url_for("recruiter_applications")
        )

    # =====================================================
    # 8. RECUPERER LE STAGIAIRE
    # =====================================================

    student = Student.query.get(
        application.student_id
    )

    if not student:

        flash(
            "Profil du stagiaire introuvable.",
            "danger"
        )

        return redirect(
            url_for("recruiter_applications")
        )

    # =====================================================
    # 9. RECUPERER LES ENCADRANTS
    # =====================================================

    supervisors = Supervisor.query.all()

    if not supervisors:

        flash(
            "Aucun encadrant disponible. "
            "Veuillez créer un compte encadrant.",
            "danger"
        )

        return redirect(
            url_for("recruiter_applications")
        )

    # =====================================================
    # 10. RECUPERER L'ENCADRANT SELECTIONNE
    # =====================================================

    supervisor_id = request.form.get(
        "supervisor_id"
    )

    # =====================================================
    # 11. PREMIER CLIC :
    # AFFICHER LA PAGE DE CHOIX DE L'ENCADRANT
    # =====================================================

    if not supervisor_id:

        return render_template(
            "recruiter/assign_supervisor.html",
            application=application,
            offer=offer,
            student=student,
            supervisors=supervisors
        )

    # =====================================================
    # 12. VERIFIER L'ENCADRANT
    # =====================================================

    try:

        supervisor_id = int(supervisor_id)

    except (ValueError, TypeError):

        flash(
            "Encadrant invalide.",
            "danger"
        )

        return redirect(
            url_for("recruiter_applications")
        )

    supervisor = Supervisor.query.get(
        supervisor_id
    )

    if not supervisor:

        flash(
            "Encadrant invalide.",
            "danger"
        )

        return redirect(
            url_for("recruiter_applications")
        )

    # =====================================================
    # 13. VERIFIER SI UN STAGE EXISTE DEJA
    # =====================================================

    existing_internship = Intership.query.filter_by(
        student_id=student.id
    ).first()

    if existing_internship:

        flash(
            "Un stage existe déjà pour ce stagiaire.",
            "warning"
        )

        return redirect(
            url_for("recruiter_applications")
        )

    # =====================================================
    # 14. CALCULER LA DATE DE DEBUT
    # =====================================================

    date_debut = None
    date_fin = None

    if offer.date_debut:

        try:

            # Exemple :
            # "2026-09-01"

            date_debut = datetime.strptime(
                offer.date_debut,
                "%Y-%m-%d"
            ).date()

        except (ValueError, TypeError):

            flash(
                "La date de début de l'offre est invalide.",
                "danger"
            )

            return redirect(
                url_for("recruiter_applications")
            )

    # =====================================================
    # 15. CALCULER LA DATE DE FIN
    # =====================================================

    if date_debut and offer.duree:

        try:

            # Exemple :
            # "2 mois"
            # "3 mois"
            # "6 mois"

            match = re.search(
                r"\d+",
                str(offer.duree)
            )

            if not match:

                flash(
                    "La durée du stage est invalide.",
                    "danger"
                )

                return redirect(
                    url_for("recruiter_applications")
                )

            duree_mois = int(
                match.group()
            )

            date_fin = (
                date_debut
                + relativedelta(
                    months=duree_mois
                )
            )

        except (ValueError, TypeError):

            flash(
                "La durée du stage est invalide.",
                "danger"
            )

            return redirect(
                url_for("recruiter_applications")
            )

    # =====================================================
    # 16. CREER LE STAGE
    # =====================================================

    internship = Intership(

        student_id=student.id,

        supervisor_id=supervisor.id,

        titre=offer.titre,

        date_debut=date_debut,

        date_fin=date_fin,

        statut="En cours",

        objectifs=None,

        taches=None,

        remarques=None,

        evaluation=None
    )

    # =====================================================
    # 17. AJOUTER LE STAGE
    # =====================================================

    db.session.add(
        internship
    )

    # =====================================================
    # 18. MODIFIER LE STATUT DE LA CANDIDATURE
    # =====================================================

    application.statut = "Acceptée"

    # =====================================================
    # 19. MODIFIER LE STATUT DE L'OFFRE
    # =====================================================

    offer.statut = "Pourvue"

    # =====================================================
    # 20. ENREGISTRER TOUT
    # =====================================================

    try:

        db.session.commit()

        print("====================================")
        print("CANDIDATURE :", application.id)
        print("STATUT :", application.statut)
        print("OFFRE :", offer.id)
        print("STATUT OFFRE :", offer.statut)
        print("STAGE :", internship.id)
        print("ETUDIANT :", internship.student_id)
        print("ENCADRANT :", internship.supervisor_id)
        print("DATE DEBUT :", internship.date_debut)
        print("DATE FIN :", internship.date_fin)
        print("====================================")

        flash(
            "Candidature acceptée. "
            "Le stage a été créé avec succès "
            "et l'encadrant a été affecté.",
            "success"
        )

    except Exception as e:

        db.session.rollback()

        print(
            "ERREUR LORS DE LA CREATION DU STAGE :",
            repr(e)
        )

        flash(
            "Une erreur est survenue lors de la "
            "création du stage.",
            "danger"
        )

    # =====================================================
    # 21. RETOUR AUX CANDIDATURES
    # =====================================================

    return redirect(
        url_for("recruiter_applications")
    )


@app.route(
    "/supervisor/internship/<int:internship_id>/manage",
    methods=["GET", "POST"]
)
def supervisor_manage_internship(internship_id):

    # ==========================================
    # 1. Vérifier la connexion
    # ==========================================

    if "user_id" not in session:
        return redirect(url_for("login"))

    # ==========================================
    # 2. Vérifier le rôle
    # ==========================================

    user = User.query.get(session["user_id"])

    if not user or user.role != "supervisor":

        flash(
            "Accès non autorisé.",
            "danger"
        )

        return redirect(url_for("login"))

    # ==========================================
    # 3. Récupérer l'encadrant
    # ==========================================

    supervisor = Supervisor.query.filter_by(
        user_id=user.id
    ).first()

    if not supervisor:

        flash(
            "Profil encadrant introuvable.",
            "danger"
        )

        return redirect(
            url_for("supervisor_dashboard")
        )

    # ==========================================
    # 4. Récupérer le stage
    # ==========================================

    internship = Intership.query.filter_by(
        id=internship_id,
        supervisor_id=supervisor.id
    ).first()

    if not internship:

        flash(
            "Stage introuvable ou vous n'êtes pas son encadrant.",
            "danger"
        )

        return redirect(
            url_for("supervisor_dashboard")
        )

    # ==========================================
    # 5. AJOUTER UNE TÂCHE
    # ==========================================

    if request.method == "POST":

        titre = request.form.get(
            "titre",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        date_debut = request.form.get(
            "date_debut"
        )

        date_limite = request.form.get(
            "date_limite"
        )

        priorite = request.form.get(
            "priorite"
        )

        statut = request.form.get(
            "statut"
        )

        progression = request.form.get(
            "progression"
        )

        # ======================================
        # Vérifier le titre
        # ======================================

        if not titre:

            flash(
                "Le titre de la tâche est obligatoire.",
                "danger"
            )

            return redirect(
                url_for(
                    "supervisor_manage_internship",
                    internship_id=internship.id
                )
            )

        # ======================================
        # Convertir les dates
        # ======================================

        date_debut_obj = None
        date_limite_obj = None

        try:

            if date_debut:

                date_debut_obj = datetime.strptime(
                    date_debut,
                    "%Y-%m-%d"
                ).date()

            if date_limite:

                date_limite_obj = datetime.strptime(
                    date_limite,
                    "%Y-%m-%d"
                ).date()

        except ValueError:

            flash(
                "Les dates saisies sont invalides.",
                "danger"
            )

            return redirect(
                url_for(
                    "supervisor_manage_internship",
                    internship_id=internship.id
                )
            )

        # ======================================
        # Progression
        # ======================================

        try:

            progression_value = int(
                progression
            ) if progression else 0

        except (ValueError, TypeError):

            progression_value = 0

        progression_value = max(
            0,
            min(
                progression_value,
                100
            )
        )

        # ======================================
        # Valeurs par défaut
        # ======================================

        if not priorite:
            priorite = "Normale"

        if not statut:
            statut = "À faire"

        # ======================================
        # Cohérence statut / progression
        # ======================================

        if progression_value == 100:

            statut = "Terminée"

        elif progression_value > 0 and statut == "À faire":

            statut = "En cours"

        # ======================================
        # Créer la tâche
        # ======================================

        task = Task(

            internship_id=internship.id,

            titre=titre,

            description=description,

            date_debut=date_debut_obj,

            date_limite=date_limite_obj,

            priorite=priorite,

            statut=statut,

            progression=progression_value
        )

        db.session.add(task)

        # ======================================
        # Enregistrer
        # ======================================

        try:

            db.session.commit()

            flash(
                "La tâche a été ajoutée avec succès.",
                "success"
            )

        except Exception as e:

            db.session.rollback()

            print(
                "Erreur ajout tâche :",
                e
            )

            flash(
                "Erreur lors de l'ajout de la tâche.",
                "danger"
            )

        return redirect(
            url_for(
                "supervisor_manage_internship",
                internship_id=internship.id
            )
        )

    # ==========================================
    # 6. Récupérer les tâches
    # ==========================================

    tasks = Task.query.filter_by(
        internship_id=internship.id
    ).order_by(
        Task.id.asc()
    ).all()

    # ==========================================
    # 7. Afficher la page
    # ==========================================

    return render_template(
        "supervisor/manage_internship.html",
        user=user,
        supervisor=supervisor,
        internship=internship,
        tasks=tasks
    )


# ==========================================================
# MODIFIER UNE TÂCHE
# ==========================================================

@app.route(
    "/supervisor/task/<int:task_id>/edit",
    methods=["GET", "POST"]
)
def supervisor_edit_task(task_id):

    # ==========================================
    # Vérifier connexion
    # ==========================================

    if "user_id" not in session:
        return redirect(url_for("login"))

    # ==========================================
    # Vérifier utilisateur
    # ==========================================

    user = User.query.get(session["user_id"])

    if not user or user.role != "supervisor":

        flash(
            "Accès non autorisé.",
            "danger"
        )

        return redirect(
            url_for("login")
        )

    # ==========================================
    # Récupérer encadrant
    # ==========================================

    supervisor = Supervisor.query.filter_by(
        user_id=user.id
    ).first()

    if not supervisor:

        flash(
            "Profil encadrant introuvable.",
            "danger"
        )

        return redirect(
            url_for("supervisor_dashboard")
        )

    # ==========================================
    # Récupérer tâche
    # ==========================================

    task = Task.query.get_or_404(task_id)

    # ==========================================
    # Vérifier que le stage appartient
    # à cet encadrant
    # ==========================================

    internship = Intership.query.filter_by(
        id=task.internship_id,
        supervisor_id=supervisor.id
    ).first()

    if not internship:

        flash(
            "Vous n'avez pas accès à cette tâche.",
            "danger"
        )

        return redirect(
            url_for("supervisor_dashboard")
        )

    # ==========================================
    # MODIFICATION
    # ==========================================

    if request.method == "POST":

        task.titre = request.form.get(
            "titre",
            ""
        ).strip()

        task.description = request.form.get(
            "description",
            ""
        ).strip()

        date_debut = request.form.get(
            "date_debut"
        )

        date_limite = request.form.get(
            "date_limite"
        )

        try:

            task.date_debut = (
                datetime.strptime(
                    date_debut,
                    "%Y-%m-%d"
                ).date()
                if date_debut
                else None
            )

            task.date_limite = (
                datetime.strptime(
                    date_limite,
                    "%Y-%m-%d"
                ).date()
                if date_limite
                else None
            )

        except ValueError:

            flash(
                "Date invalide.",
                "danger"
            )

            return redirect(
                url_for(
                    "supervisor_edit_task",
                    task_id=task.id
                )
            )

        task.priorite = request.form.get(
            "priorite"
        ) or "Normale"

        task.statut = request.form.get(
            "statut"
        ) or "À faire"

        # ==========================================
        # Progression
        # ==========================================

        try:

            progression = int(
                request.form.get(
                    "progression",
                    0
                )
            )

        except (ValueError, TypeError):

            progression = 0

        progression = max(
            0,
            min(
                progression,
                100
            )
        )

        task.progression = progression

        # ==========================================
        # Cohérence statut / progression
        # ==========================================

        if progression == 100:

            task.statut = "Terminée"

        elif progression > 0 and task.statut == "À faire":

            task.statut = "En cours"

        # ==========================================
        # Enregistrer
        # ==========================================

        try:

            db.session.commit()

            flash(
                "La tâche a été modifiée avec succès.",
                "success"
            )

        except Exception as e:

            db.session.rollback()

            print(
                "Erreur modification tâche :",
                e
            )

            flash(
                "Erreur lors de la modification.",
                "danger"
            )

        return redirect(
            url_for(
                "supervisor_manage_internship",
                internship_id=internship.id
            )
        )

    # ==========================================
    # Afficher formulaire
    # ==========================================

    return render_template(
        "supervisor/edit_task.html",
        user=user,
        supervisor=supervisor,
        internship=internship,
        task=task
    )


# ==========================================================
# SUPPRIMER UNE TÂCHE
# ==========================================================

@app.route(
    "/supervisor/task/<int:task_id>/delete",
    methods=["POST"]
)
def supervisor_delete_task(task_id):

    # ==========================================
    # Vérifier connexion
    # ==========================================

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    # ==========================================
    # Vérifier utilisateur
    # ==========================================

    user = User.query.get(
        session["user_id"]
    )

    if not user or user.role != "supervisor":

        flash(
            "Accès non autorisé.",
            "danger"
        )

        return redirect(
            url_for("login")
        )

    # ==========================================
    # Récupérer encadrant
    # ==========================================

    supervisor = Supervisor.query.filter_by(
        user_id=user.id
    ).first()

    if not supervisor:

        flash(
            "Profil encadrant introuvable.",
            "danger"
        )

        return redirect(
            url_for("supervisor_dashboard")
        )

    # ==========================================
    # Récupérer tâche
    # ==========================================

    task = Task.query.get_or_404(
        task_id
    )

    # ==========================================
    # Vérifier le stage
    # ==========================================

    internship = Intership.query.filter_by(
        id=task.internship_id,
        supervisor_id=supervisor.id
    ).first()

    if not internship:

        flash(
            "Vous n'avez pas accès à cette tâche.",
            "danger"
        )

        return redirect(
            url_for("supervisor_dashboard")
        )

    # ==========================================
    # Supprimer
    # ==========================================

    try:

        db.session.delete(task)

        db.session.commit()

        flash(
            "La tâche a été supprimée.",
            "success"
        )

    except Exception as e:

        db.session.rollback()

        print(
            "Erreur suppression tâche :",
            e
        )

        flash(
            "Erreur lors de la suppression.",
            "danger"
        )

    return redirect(
        url_for(
            "supervisor_manage_internship",
            internship_id=internship.id
        )
    )

@app.route(
    "/supervisor/task/<int:task_id>/update",
    methods=["POST"]
)
def supervisor_update_task(task_id):

    # Vérifier la connexion
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Récupérer l'utilisateur
    user = User.query.get(session["user_id"])

    if not user or user.role != "supervisor":
        flash("Accès non autorisé.", "danger")
        return redirect(url_for("login"))

    # Récupérer l'encadrant
    supervisor = Supervisor.query.filter_by(
        user_id=user.id
    ).first()

    if not supervisor:
        flash("Profil encadrant introuvable.", "danger")
        return redirect(url_for("supervisor_dashboard"))

    # Récupérer la tâche
    task = Task.query.get_or_404(task_id)

    # Récupérer le stage
    internship = Intership.query.filter_by(
        id=task.internship_id,
        supervisor_id=supervisor.id
    ).first()

    if not internship:
        flash(
            "Vous n'avez pas accès à cette tâche.",
            "danger"
        )
        return redirect(
            url_for("supervisor_dashboard")
        )

    # Récupérer les données du formulaire
    statut = request.form.get("statut")
    progression = request.form.get("progression")
    priorite = request.form.get("priorite")

    # Vérifier la progression
    try:
        progression = int(progression)
    except (ValueError, TypeError):
        progression = 0

    progression = max(
        0,
        min(progression, 100)
    )

    # Si progression = 100, la tâche est terminée
    if progression == 100:
        statut = "Terminée"

    # Si progression > 0 et < 100
    elif progression > 0:
        statut = "En cours"

    # Si progression = 0
    elif progression == 0 and statut not in [
        "En cours",
        "Terminée"
    ]:
        statut = "À faire"

    # Modifier la tâche
    task.progression = progression
    task.statut = statut
    task.priorite = priorite

    try:

        db.session.commit()

        flash(
            "La tâche a été mise à jour avec succès.",
            "success"
        )

    except Exception as e:

        db.session.rollback()

        print(
            "Erreur modification tâche :",
            e
        )

        flash(
            "Erreur lors de la modification de la tâche.",
            "danger"
        )

    return redirect(
        url_for(
            "supervisor_manage_internship",
            internship_id=internship.id
        )
    )

@app.route(
    "/supervisor/internship/<int:internship_id>/evaluation",
    methods=["GET", "POST"]
)
def supervisor_evaluation(internship_id):

    # Vérification connexion
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Vérification utilisateur
    user = User.query.get(session["user_id"])

    if not user or user.role != "supervisor":
        flash("Accès non autorisé.", "danger")
        return redirect(url_for("login"))

    # Récupérer le superviseur
    supervisor = Supervisor.query.filter_by(
        user_id=user.id
    ).first()

    if not supervisor:
        flash(
            "Profil encadrant introuvable.",
            "danger"
        )
        return redirect(
            url_for("supervisor_dashboard")
        )

    # Récupérer le stage
    internship = Intership.query.filter_by(
        id=internship_id,
        supervisor_id=supervisor.id
    ).first()

    if not internship:
        flash(
            "Stage introuvable ou vous n'êtes pas son encadrant.",
            "danger"
        )
        return redirect(
            url_for("supervisor_dashboard")
        )

    # Récupérer le stagiaire
    student = internship.student

    # Récupérer l'évaluation existante
    evaluation = Evaluation.query.filter_by(
        internship_id=internship.id,
        supervisor_id=supervisor.id,
        student_id=internship.student_id
    ).first()

    # ==========================================
    # ENREGISTREMENT
    # ==========================================

    if request.method == "POST":

        try:

            note_technique = float(
                request.form.get("note_technique", 0)
            )

            note_travail = float(
                request.form.get("note_travail", 0)
            )

            note_comportement = float(
                request.form.get("note_comportement", 0)
            )

            note_assiduite = float(
                request.form.get("note_assiduite", 0)
            )

        except ValueError:

            flash(
                "Les notes doivent être numériques.",
                "danger"
            )

            return redirect(
                url_for(
                    "supervisor_evaluation",
                    internship_id=internship.id
                )
            )

        # Vérifier les notes
        notes = [
            note_technique,
            note_travail,
            note_comportement,
            note_assiduite
        ]

        if any(note < 0 or note > 20 for note in notes):

            flash(
                "Les notes doivent être comprises entre 0 et 20.",
                "danger"
            )

            return redirect(
                url_for(
                    "supervisor_evaluation",
                    internship_id=internship.id
                )
            )

        # Calcul de la note finale
        note_finale = round(
            (
                note_technique
                + note_travail
                + note_comportement
                + note_assiduite
            ) / 4,
            2
        )

        commentaire = request.form.get(
            "commentaire",
            ""
        ).strip()

        # ==========================================
        # CRÉER OU MODIFIER
        # ==========================================

        if evaluation:

            evaluation.note_technique = note_technique
            evaluation.note_travail = note_travail
            evaluation.note_comportement = note_comportement
            evaluation.note_assiduite = note_assiduite
            evaluation.note_finale = note_finale
            evaluation.commentaire = commentaire

        else:

            evaluation = Evaluation(

                internship_id=internship.id,

                supervisor_id=supervisor.id,

                student_id=internship.student_id,

                note_technique=note_technique,

                note_travail=note_travail,

                note_comportement=note_comportement,

                note_assiduite=note_assiduite,

                note_finale=note_finale,

                commentaire=commentaire
            )

            db.session.add(evaluation)

        db.session.commit()

        flash(
            "Évaluation enregistrée avec succès.",
            "success"
        )

        return redirect(
            url_for(
                "supervisor_evaluation",
                internship_id=internship.id
            )
        )

    # ==========================================
    # AFFICHER LA PAGE
    # ==========================================

    return render_template(
        "supervisor/evaluation.html",
        user=user,
        supervisor=supervisor,
        internship=internship,
        student=student,
        evaluation=evaluation
    )

@app.route(
    "/supervisor/internship/<int:internship_id>/evaluation/pdf"
)
def supervisor_evaluation_pdf(internship_id):

    # ==========================================
    # 1. Vérifier la connexion
    # ==========================================

    if "user_id" not in session:
        return redirect(url_for("login"))

    # ==========================================
    # 2. Vérifier l'utilisateur
    # ==========================================

    user = User.query.get(session["user_id"])

    if not user or user.role != "supervisor":

        flash(
            "Accès non autorisé.",
            "danger"
        )

        return redirect(
            url_for("login")
        )

    # ==========================================
    # 3. Récupérer l'encadrant
    # ==========================================

    supervisor = Supervisor.query.filter_by(
        user_id=user.id
    ).first()

    if not supervisor:

        flash(
            "Profil encadrant introuvable.",
            "danger"
        )

        return redirect(
            url_for("supervisor_dashboard")
        )

    # ==========================================
    # 4. Récupérer le stage
    # ==========================================

    internship = Intership.query.filter_by(
        id=internship_id,
        supervisor_id=supervisor.id
    ).first()

    if not internship:

        flash(
            "Stage introuvable ou accès non autorisé.",
            "danger"
        )

        return redirect(
            url_for("supervisor_dashboard")
        )

    # ==========================================
    # 5. Récupérer l'évaluation
    # ==========================================

    evaluation = Evaluation.query.filter_by(
        internship_id=internship.id
    ).first()

    if not evaluation:

        flash(
            "Aucune évaluation n'a encore été enregistrée.",
            "warning"
        )

        return redirect(
            url_for(
                "supervisor_evaluation",
                internship_id=internship.id
            )
        )

    # ==========================================
    # 6. Récupérer le stagiaire
    # ==========================================

    student = internship.student

    student_user = None

    if student and student.user_id:

        student_user = User.query.get(
            student.user_id
        )

    # Nom complet et email

    if student_user:

        nom_complet = (
            f"{student_user.prenom} "
            f"{student_user.nom}"
        )

        email = (
            student_user.email
            or "Non renseigné"
        )

    else:

        nom_complet = "Non renseigné"
        email = "Non renseigné"

    # ==========================================
    # 7. Créer le PDF
    # ==========================================

    buffer = BytesIO()

    pdf = canvas.Canvas(
        buffer,
        pagesize=A4
    )

    width, height = A4

    # ==========================================
    # 8. LOGO
    # ==========================================

    logo_path = os.path.join(
        app.root_path,
        "static",
        "assets",
        "img",
        "amen-bank.jpg"
    )

    print("Chemin du logo :", logo_path)
    print("Logo existe :", os.path.isfile(logo_path))

    if os.path.isfile(logo_path):

        try:

            logo = ImageReader(logo_path)

            pdf.drawImage(
                logo,
                50,
                height - 95,
                width=110,
                height=55,
                preserveAspectRatio=True,
                anchor="c",
                mask="auto"
            )

        except Exception as e:

            print(
                "Erreur lors du chargement du logo :",
                e
            )

    else:

        print(
            "ERREUR : logo introuvable :",
            logo_path
        )

    # ==========================================
    # 9. TITRE
    # ==========================================

    pdf.setFont(
        "Helvetica-Bold",
        18
    )

    pdf.drawCentredString(
        width / 2,
        height - 60,
        "RAPPORT D'ÉVALUATION DU STAGE"
    )

    # Position de départ du contenu

    y = height - 125

    # ==========================================
    # 10. INFORMATIONS DU STAGE
    # ==========================================

    pdf.setFont(
        "Helvetica-Bold",
        13
    )

    pdf.drawString(
        50,
        y,
        "Informations du stage"
    )

    y -= 25

    pdf.setFont(
        "Helvetica",
        11
    )

    pdf.drawString(
        60,
        y,
        f"Intitulé du stage : "
        f"{internship.titre or 'Non renseigné'}"
    )

    y -= 20

    pdf.drawString(
    60,
    y,
    f"Date de début : "
    f"{internship.date_debut.strftime('%d/%m/%Y') if internship.date_debut else 'Non renseignée'}"
)

    y -= 20

    pdf.drawString(
    60,
    y,
    f"Date de fin : "
    f"{internship.date_fin.strftime('%d/%m/%Y') if internship.date_fin else 'Non renseignée'}"
)

    y -= 35

    # ==========================================
    # 11. INFORMATIONS DU STAGIAIRE
    # ==========================================

    pdf.setFont(
        "Helvetica-Bold",
        13
    )

    pdf.drawString(
        50,
        y,
        "Informations du stagiaire"
    )

    y -= 25

    pdf.setFont(
        "Helvetica",
        11
    )

    pdf.drawString(
        60,
        y,
        f"Nom et prénom : {nom_complet}"
    )

    y -= 20

    pdf.drawString(
        60,
        y,
        f"Email : {email}"
    )

    if student:

        y -= 20

        pdf.drawString(
            60,
            y,
            f"Formation : "
            f"{student.formation or 'Non renseignée'}"
        )

        y -= 20

        pdf.drawString(
            60,
            y,
            f"Niveau : "
            f"{student.niveau or 'Non renseigné'}"
        )

        y -= 20

        pdf.drawString(
            60,
            y,
            f"Université : "
            f"{student.universite or 'Non renseignée'}"
        )

    y -= 35

    # ==========================================
    # 12. ÉVALUATION
    # ==========================================

    pdf.setFont(
        "Helvetica-Bold",
        13
    )

    pdf.drawString(
        50,
        y,
        "Évaluation"
    )

    y -= 30

    pdf.setFont(
        "Helvetica",
        11
    )

    pdf.drawString(
        60,
        y,
        f"Note technique : "
        f"{evaluation.note_technique or 0}/20"
    )

    y -= 20

    pdf.drawString(
        60,
        y,
        f"Note travail : "
        f"{evaluation.note_travail or 0}/20"
    )

    y -= 20

    pdf.drawString(
        60,
        y,
        f"Note comportement : "
        f"{evaluation.note_comportement or 0}/20"
    )

    y -= 20

    pdf.drawString(
        60,
        y,
        f"Note assiduité : "
        f"{evaluation.note_assiduite or 0}/20"
    )

    y -= 30

    # ==========================================
    # 13. NOTE FINALE
    # ==========================================

    pdf.setFont(
        "Helvetica-Bold",
        14
    )

    pdf.drawString(
        60,
        y,
        f"NOTE FINALE : "
        f"{evaluation.note_finale or 0}/20"
    )

    y -= 40

    # ==========================================
    # 14. COMMENTAIRE
    # ==========================================

    pdf.setFont(
        "Helvetica-Bold",
        13
    )

    pdf.drawString(
        50,
        y,
        "Commentaire de l'encadrant"
    )

    y -= 25

    pdf.setFont(
        "Helvetica",
        11
    )

    commentaire = (
        evaluation.commentaire
        if evaluation.commentaire
        else "Aucun commentaire."
    )

    # ==========================================
    # Découpage du commentaire
    # ==========================================

    lignes = []

    mots = commentaire.split()

    ligne = ""

    for mot in mots:

        test = (
            ligne + " " + mot
            if ligne
            else mot
        )

        if len(test) > 85:

            if ligne:
                lignes.append(ligne)

            ligne = mot

        else:

            ligne = test

    if ligne:
        lignes.append(ligne)

    # ==========================================
    # Afficher le commentaire
    # ==========================================

    for ligne_commentaire in lignes:

        pdf.drawString(
            60,
            y,
            ligne_commentaire.strip()
        )

        y -= 18

        # Nouvelle page si nécessaire

        if y < 60:

            pdf.showPage()

            y = height - 50

            pdf.setFont(
                "Helvetica",
                11
            )

    # ==========================================
    # 15. PIED DE PAGE
    # ==========================================

    pdf.setFont(
        "Helvetica",
        9
    )

    pdf.drawCentredString(
        width / 2,
        30,
        "Plateforme de gestion des stages"
    )

    # ==========================================
    # 16. FINALISER LE PDF
    # ==========================================

    pdf.save()

    buffer.seek(0)

    # ==========================================
    # 17. NOM DU FICHIER
    # ==========================================

    if student_user:

        filename = (
            f"evaluation_"
            f"{student_user.nom}_"
            f"{student_user.prenom}.pdf"
        )

    else:

        filename = (
            "evaluation_stagiaire.pdf"
        )

    # ==========================================
    # 18. TÉLÉCHARGER LE PDF
    # ==========================================

    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype="application/pdf"
    )

@app.route("/student/evaluation")
def student_evaluation():


    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])

    if not user or user.role != "student":
        flash("Accès non autorisé.", "danger")
        return redirect(url_for("login"))

    student = Student.query.filter_by(
        user_id=user.id
    ).first()

    if not student:
        flash("Profil étudiant introuvable.", "danger")
        return redirect(url_for("student_dashboard"))

    internship = Intership.query.filter_by(
        student_id=student.id
    ).first()

    evaluation = None

    if internship:

        evaluation = Evaluation.query.filter_by(
            internship_id=internship.id,
            student_id=student.id
        ).first()

    return render_template(
        "student/evaluation.html",
        user=user,
        student=student,
        internship=internship,
        evaluation=evaluation
    )

@app.route("/student/evaluation/pdf")
def student_evaluation_pdf():

# ==========================================
# 1. Vérifier la connexion
# ==========================================

    if "user_id" not in session:
        return redirect(url_for("login"))

    # ==========================================
    # 2. Récupérer l'utilisateur connecté
    # ==========================================

    user = User.query.get(session["user_id"])

    if not user or user.role != "student":

        flash(
            "Accès non autorisé.",
            "danger"
        )

        return redirect(url_for("login"))

    # ==========================================
    # 3. Récupérer le profil Student
    # ==========================================

    student = Student.query.filter_by(
        user_id=user.id
    ).first()

    if not student:

        flash(
            "Profil étudiant introuvable.",
            "danger"
        )

        return redirect(
            url_for("student_dashboard")
        )

    # ==========================================
    # 4. Récupérer le stage
    # ==========================================

    internship = Intership.query.filter_by(
        student_id=student.id
    ).first()

    if not internship:

        flash(
            "Aucun stage trouvé.",
            "warning"
        )

        return redirect(
            url_for("student_evaluation")
        )

    # ==========================================
    # 5. Récupérer l'évaluation
    # ==========================================

    evaluation = Evaluation.query.filter_by(
        internship_id=internship.id,
        student_id=student.id
    ).first()

    if not evaluation:

        flash(
            "Aucune évaluation n'est encore disponible.",
            "warning"
        )

        return redirect(
            url_for("student_evaluation")
        )

    # ==========================================
    # 6. Créer le PDF
    # ==========================================

    from io import BytesIO

    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle
    )
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.enums import TA_CENTER

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    title_style.alignment = TA_CENTER

    normal_style = styles["Normal"]

    elements = []

    # ==========================================
    # TITRE
    # ==========================================

    elements.append(
        Paragraph(
            "RAPPORT D'ÉVALUATION DU STAGE",
            title_style
        )
    )

    elements.append(Spacer(1, 15))

    # ==========================================
    # INFORMATIONS STAGIAIRE
    # ==========================================

    elements.append(
        Paragraph(
            "<b>Informations du stagiaire</b>",
            styles["Heading2"]
        )
    )

    elements.append(Spacer(1, 10))

    student_name = f"{user.prenom} {user.nom}"

    student_data = [
        ["Nom et prénom", student_name],
        ["Formation", student.formation or "Non renseignée"],
        ["Niveau", student.niveau or "Non renseigné"],
        ["Université", student.universite or "Non renseignée"],
        ["Téléphone", student.telephone or "Non renseigné"]
    ]

    student_table = Table(
        student_data,
        colWidths=[150, 330]
    )

    student_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8)
        ])
    )

    elements.append(student_table)

    elements.append(Spacer(1, 15))

    # ==========================================
    # INFORMATIONS DU STAGE
    # ==========================================

    elements.append(
        Paragraph(
            "<b>Informations du stage</b>",
            styles["Heading2"]
        )
    )

    elements.append(Spacer(1, 10))

    date_debut = (
        internship.date_debut.strftime("%d/%m/%Y")
        if internship.date_debut
        else "Non renseignée"
    )

    date_fin = (
        internship.date_fin.strftime("%d/%m/%Y")
        if internship.date_fin
        else "Non renseignée"
    )

    internship_data = [
        ["Stage", internship.titre or "Stage"],
        ["Date de début", date_debut],
        ["Date de fin", date_fin],
        ["Statut", internship.statut or "Non renseigné"]
    ]

    internship_table = Table(
        internship_data,
        colWidths=[150, 330]
    )

    internship_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8)
        ])
    )

    elements.append(internship_table)

    elements.append(Spacer(1, 15))

    # ==========================================
    # ÉVALUATION
    # ==========================================

    elements.append(
        Paragraph(
            "<b>Évaluation du stagiaire</b>",
            styles["Heading2"]
        )
    )

    elements.append(Spacer(1, 10))

    evaluation_data = [
        ["Critère", "Note"],
        ["Compétences techniques", f"{evaluation.note_technique or 0}/20"],
        ["Qualité du travail", f"{evaluation.note_travail or 0}/20"],
        ["Comportement", f"{evaluation.note_comportement or 0}/20"],
        ["Assiduité", f"{evaluation.note_assiduite or 0}/20"],
        ["Note finale", f"{evaluation.note_finale or 0}/20"]
    ]

    evaluation_table = Table(
        evaluation_data,
        colWidths=[330, 150]
    )

    evaluation_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("ALIGN", (1, 0), (1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8)
        ])
    )

    elements.append(evaluation_table)

    elements.append(Spacer(1, 15))

    # ==========================================
    # COMMENTAIRE
    # ==========================================

    elements.append(
        Paragraph(
            "<b>Commentaire de l'encadrant</b>",
            styles["Heading2"]
        )
    )

    elements.append(Spacer(1, 10))

    commentaire = (
        evaluation.commentaire
        if evaluation.commentaire
        else "Aucun commentaire."
    )

    elements.append(
        Paragraph(
            commentaire,
            normal_style
        )
    )

    elements.append(Spacer(1, 30))

    # ==========================================
    # Génération
    # ==========================================

    doc.build(elements)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="evaluation_stage.pdf",
        mimetype="application/pdf"
    )


@app.route('/student/offers')
def search_offers():

    keyword = request.args.get('keyword', '').strip()

    if not keyword:
        offers = Offer.query.all()

    else:
        search = f"%{keyword}%"

        offers = Offer.query.filter(
            or_(
                Offer.titre.ilike(search),
                Offer.description.ilike(search),
                Offer.competences.ilike(search),
                Offer.domaine.ilike(search),
                Offer.lieu.ilike(search),
                Offer.type_stage.ilike(search)
            )
        ).all()

    return render_template(
        'offers.html',
        offers=offers,
        keyword=keyword
    )
        
@app.route('/student/search-offers')
def ajax_search_offers():

    keyword = request.args.get('keyword', '').strip()

    if not keyword:
        offers = Offer.query.all()

    else:
        search = f"%{keyword}%"

        offers = Offer.query.filter(
            or_(
                Offer.titre.ilike(search),
                Offer.description.ilike(search),
                Offer.competences.ilike(search),
                Offer.domaine.ilike(search),
                Offer.lieu.ilike(search),
                Offer.type_stage.ilike(search)
            )
        ).all()

    results = []

    for offer in offers:

        results.append({
            'id': offer.id,
            'titre': offer.titre,
            'description': offer.description,
            'competences': offer.competences,
            'domaine': offer.domaine,
            'lieu': offer.lieu,
            'type_stage': offer.type_stage,
            'duree': offer.duree
        })

    return jsonify(results)
@app.context_processor
def inject_notifications():

    if session.get("user_id"):

        unread_notifications = Notification.query.filter_by(
            user_id=session.get("user_id"),
            lu=False
        ).count()

    else:
        unread_notifications = 0

    return {
        "unread_notifications": unread_notifications
    }


@app.route('/student/notifications')
def student_notifications():

    if not session.get("user_id"):
        return redirect(url_for("login"))

    user_id = session.get("user_id")

    notifications = Notification.query.filter_by(
        user_id=user_id
    ).order_by(
        Notification.date_creation.desc()
    ).all()

    return render_template(
        "notifications.html",
        notifications=notifications
    )


@app.route('/student/notifications/<int:notification_id>')
def student_notification_detail(notification_id):

    if not session.get("user_id"):
        return redirect(url_for("login"))

    notification = Notification.query.filter_by(
        id=notification_id,
        user_id=session.get("user_id")
    ).first_or_404()

    notification.lu = True
    db.session.commit()

    if notification.message_id:
        return redirect(
            url_for(
                "student_message_detail",
                message_id=notification.message_id
            )
        )

    return redirect(url_for("student_notifications"))


@app.route('/student/messages/<int:message_id>')
def student_message_detail(message_id):

    if not session.get("user_id"):
        return redirect(url_for("login"))

    user_id = session.get("user_id")

    message = Message.query.filter(
        Message.id == message_id,
        or_(
            Message.sender_id == user_id,
            Message.receiver_id == user_id
        )
    ).first_or_404()

    message.lu = True
    db.session.commit()

    return render_template(
        "student/message_detail.html",
        message=message
    )
@app.route('/student/chat/<int:internship_id>')
def student_chat(internship_id):

    if not session.get("user_id"):
        return redirect(url_for("login"))

    student_user_id = session.get("user_id")

    # Récupérer le profil étudiant
    student = Student.query.filter_by(
        user_id=student_user_id
    ).first_or_404()

    # Vérifier que le stage appartient bien à cet étudiant
    internship = Intership.query.filter_by(
        id=internship_id,
        student_id=student.id
    ).first_or_404()

    # Vérifier qu'un encadreur est affecté
    if not internship.supervisor_id:
        flash("Aucun encadreur n'est encore affecté à ce stage.", "warning")
        return redirect(url_for("student_internship"))

    # Récupérer l'encadreur
    supervisor = Supervisor.query.filter_by(
        id=internship.supervisor_id
    ).first_or_404()

    supervisor_user_id = supervisor.user_id

    # Récupérer tous les messages entre étudiant et encadreur
    messages = Message.query.filter(
        or_(
            and_(
                Message.sender_id == student_user_id,
                Message.receiver_id == supervisor_user_id
            ),
            and_(
                Message.sender_id == supervisor_user_id,
                Message.receiver_id == student_user_id
            )
        )
    ).order_by(
        Message.date_envoi.asc()
    ).all()

    # Marquer comme lus les messages reçus de l'encadreur
    Message.query.filter(
        Message.sender_id == supervisor_user_id,
        Message.receiver_id == student_user_id,
        Message.lu == False
    ).update(
        {Message.lu: True},
        synchronize_session=False
    )

    db.session.commit()

    return render_template(
        "student/chat.html",
        internship=internship,
        supervisor=supervisor,
        messages=messages
    )
@app.route(
    '/student/chat/<int:internship_id>/send',
    methods=['POST']
)
def student_send_message(internship_id):

    if not session.get("user_id"):
        return redirect(url_for("login"))

    user_id = session.get("user_id")

    # Stagiaire connecté
    student = Student.query.filter_by(
        user_id=user_id
    ).first_or_404()

    # Vérifier le stage
    internship = Intership.query.filter_by(
        id=internship_id,
        student_id=student.id
    ).first_or_404()

    # Vérifier l'encadreur
    if not internship.supervisor_id:
        flash(
            "Aucun encadreur n'est affecté à ce stage.",
            "warning"
        )

        return redirect(
            url_for(
                "student_internship"
            )
        )

    supervisor = Supervisor.query.filter_by(
        id=internship.supervisor_id
    ).first_or_404()

    supervisor_user_id = supervisor.user_id

    contenu = request.form.get(
        "contenu",
        ""
    ).strip()

    if not contenu:
        flash(
            "Veuillez saisir un message.",
            "warning"
        )

        return redirect(
            url_for(
                "student_chat",
                internship_id=internship_id
            )
        )

    # Création du message
    nouveau_message = Message(
        sender_id=user_id,
        receiver_id=supervisor_user_id,
        contenu=contenu,
        lu=False
    )

    db.session.add(nouveau_message)
    db.session.commit()

    return redirect(
        url_for(
            "student_chat",
            internship_id=internship_id
        )
    )
@app.context_processor
def inject_student_chat_data():

    unread_messages = 0
    student_internship = None

    if session.get("user_id"):

        user_id = session.get("user_id")

        # Nombre de messages non lus
        unread_messages = Message.query.filter_by(
            receiver_id=user_id,
            lu=False
        ).count()

        # Récupérer le profil étudiant
        student = Student.query.filter_by(
            user_id=user_id
        ).first()

        if student:

            # Stage avec encadreur affecté
            student_internship = Intership.query.filter(
                Intership.student_id == student.id,
                Intership.supervisor_id.isnot(None)
            ).first()

    return {
        "unread_messages": unread_messages,
        "student_internship": student_internship
    }
@app.route('/supervisor/notifications')
def supervisor_notifications():

    if not session.get("user_id"):
        return redirect(url_for("login"))

    user_id = session.get("user_id")

    notifications = Notification.query.filter_by(
        user_id=user_id
    ).order_by(
        Notification.date_creation.desc()
    ).all()

    return render_template(
        "supervisor/notifications.html",
        notifications=notifications
    )

@app.route('/supervisor/notifications/<int:notification_id>')
def supervisor_notification_detail(notification_id):

    if not session.get("user_id"):
        return redirect(url_for("login"))

    notification = Notification.query.filter_by(
        id=notification_id,
        user_id=session.get("user_id")
    ).first_or_404()

    notification.lu = True
    db.session.commit()

    if notification.message_id:
        return redirect(
            url_for(
                "supervisor_message_detail",
                message_id=notification.message_id
            )
        )

    return redirect(url_for("supervisor_notifications"))


@app.route('/supervisor/chat/<int:internship_id>')
def supervisor_chat(internship_id):

    if not session.get("user_id"):
        return redirect(url_for("login"))

    # User de l'encadreur connecté
    supervisor_user_id = session.get("user_id")

    # Récupérer le profil Supervisor
    supervisor = Supervisor.query.filter_by(
        user_id=supervisor_user_id
    ).first_or_404()

    # Vérifier que le stage appartient à cet encadreur
    internship = Intership.query.filter_by(
        id=internship_id,
        supervisor_id=supervisor.id
    ).first_or_404()

    # Récupérer le Student
    student = Student.query.filter_by(
        id=internship.student_id
    ).first_or_404()

    # Récupérer le User correspondant au Student
    student_user = User.query.filter_by(
        id=student.user_id
    ).first_or_404()

    student_user_id = student_user.id

    # Récupérer les messages entre l'encadreur et le stagiaire
    messages = Message.query.filter(
        or_(
            and_(
                Message.sender_id == supervisor_user_id,
                Message.receiver_id == student_user_id
            ),
            and_(
                Message.sender_id == student_user_id,
                Message.receiver_id == supervisor_user_id
            )
        )
    ).order_by(
        Message.date_envoi.asc()
    ).all()

    # Marquer comme lus les messages reçus du stagiaire
    Message.query.filter(
        Message.sender_id == student_user_id,
        Message.receiver_id == supervisor_user_id,
        Message.lu == False
    ).update(
        {Message.lu: True},
        synchronize_session=False
    )

    db.session.commit()

    return render_template(
        "supervisor/chat.html",
        internship=internship,
        student=student,
        student_user=student_user,
        messages=messages
    )
@app.route(
    '/supervisor/chat/<int:internship_id>/send',
    methods=['POST']
)
def supervisor_send_message(internship_id):

    if not session.get("user_id"):
        return redirect(url_for("login"))

    supervisor_user_id = session.get("user_id")

    supervisor = Supervisor.query.filter_by(
        user_id=supervisor_user_id
    ).first_or_404()

    internship = Intership.query.filter_by(
        id=internship_id,
        supervisor_id=supervisor.id
    ).first_or_404()

    student = Student.query.filter_by(
        id=internship.student_id
    ).first_or_404()

    student_user_id = student.user_id

    contenu = request.form.get(
        "contenu",
        ""
    ).strip()

    if not contenu:

        flash(
            "Veuillez saisir un message.",
            "warning"
        )

        return redirect(
            url_for(
                "supervisor_chat",
                internship_id=internship_id
            )
        )

    nouveau_message = Message(
        sender_id=supervisor_user_id,
        receiver_id=student_user_id,
        contenu=contenu,
        lu=False
    )

    db.session.add(nouveau_message)
    db.session.commit()

    return redirect(
        url_for(
            "supervisor_chat",
            internship_id=internship_id
        )
    )

@app.context_processor
def inject_unread_messages():

    unread_messages = 0

    if session.get("user_id"):

        user_id = session.get("user_id")

        unread_messages = Message.query.filter_by(
            receiver_id=user_id,
            lu=False
        ).count()

    return {
        "unread_messages": unread_messages
    }
@app.route('/supervisor/messages/<int:message_id>')
def supervisor_message_detail(message_id):

    if not session.get("user_id"):
        return redirect(url_for("login"))

    user_id = session.get("user_id")

    message = Message.query.filter(
        Message.id == message_id,
        or_(
            Message.sender_id == user_id,
            Message.receiver_id == user_id
        )
    ).first_or_404()

    message.lu = True
    db.session.commit()

    return render_template(
        "supervisor/message_detail.html",
        message=message
    )

@app.route('/supervisor/messages')
def supervisor_messages():

    if not session.get("user_id"):
        return redirect(url_for("login"))

    supervisor_user_id = session.get("user_id")

    # Récupérer l'encadreur connecté
    supervisor = Supervisor.query.filter_by(
        user_id=supervisor_user_id
    ).first_or_404()

    # Récupérer les stages de cet encadreur
    internships = Intership.query.filter_by(
        supervisor_id=supervisor.id
    ).all()

    conversations = []

    for internship in internships:

        # Récupérer le stagiaire
        student = Student.query.filter_by(
            id=internship.student_id
        ).first()

        if not student:
            continue

        # Récupérer son User
        student_user = User.query.filter_by(
            id=student.user_id
        ).first()

        if not student_user:
            continue

        student_user_id = student.user_id

        # Dernier message entre le stagiaire et l'encadreur
        last_message = Message.query.filter(
            or_(
                and_(
                    Message.sender_id == supervisor_user_id,
                    Message.receiver_id == student_user_id
                ),
                and_(
                    Message.sender_id == student_user_id,
                    Message.receiver_id == supervisor_user_id
                )
            )
        ).order_by(
            Message.date_envoi.desc()
        ).first()

        # Nombre de messages non lus envoyés par le stagiaire
        unread_count = Message.query.filter_by(
            sender_id=student_user_id,
            receiver_id=supervisor_user_id,
            lu=False
        ).count()

        conversations.append({
            "internship": internship,
            "student": student,
            "student_user": student_user,
            "last_message": last_message,
            "unread_count": unread_count
        })

    return render_template(
        "supervisor/messages.html",
        conversations=conversations
    )
if __name__ == "__main__":
    app.run(debug=True)