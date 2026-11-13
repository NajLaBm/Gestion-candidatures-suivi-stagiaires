# 🎓 Gestion des candidatures et suivi des stagiaires

## 📌 Présentation du projet

**Gestion des candidatures et suivi des stagiaires** est une application web développée avec Python et Flask, destinée à centraliser et à faciliter la gestion du recrutement des stagiaires au sein d’une entreprise.

La plateforme couvre l’ensemble du processus, depuis la publication des offres de stage et le dépôt des candidatures jusqu’à l’affectation des stagiaires, au suivi de leurs activités et à leur évaluation finale.

Elle repose sur trois acteurs principaux — le recruteur, le stagiaire et l’encadrant — qui disposent de fonctionnalités adaptées à leurs responsabilités.

## 🎯 Objectifs

- Centraliser les offres de stage et les candidatures.
- Simplifier le processus de sélection des candidats.
- Assurer le suivi des stagiaires pendant toute la durée de leur stage.
- Faciliter la communication entre les recruteurs, les stagiaires et les encadrants.
- Organiser les tâches, les objectifs et les évaluations.
- Améliorer la traçabilité des candidatures et le suivi de progression.

## 👥 Acteurs et fonctionnalités

### 1. 🧑‍💼 Recruteur

Le recruteur gère le processus de recrutement et la sélection des candidats.

- Publier et gérer les offres de stage.
- Consulter les candidatures reçues.
- Examiner les profils et les CV des candidats.
- Accepter ou refuser les candidatures.
- Déclencher l’affectation des candidats retenus à un encadrant.
- Consulter les informations relatives aux stages.

### 2. 🎓 Stagiaire

Le stagiaire utilise la plateforme pour rechercher des opportunités et suivre son parcours.

- Créer et gérer son profil.
- Ajouter ou mettre à jour son CV.
- Consulter les offres de stage disponibles.
- Déposer des candidatures.
- Suivre le statut de ses candidatures.
- Consulter les informations relatives à son stage.
- Accéder aux objectifs et aux tâches qui lui sont attribués.
- Suivre l’évolution de son stage.

### 3. 👨‍🏫 Encadrant

L’encadrant assure le suivi opérationnel et pédagogique des stagiaires qui lui sont affectés.

- Consulter les informations des stagiaires encadrés.
- Définir les objectifs du stage.
- Attribuer et suivre les tâches.
- Ajouter des remarques sur la progression.
- Suivre l’avancement des activités.
- Évaluer le stagiaire à la fin du stage.

## 🔄 Processus métier

Le fonctionnement de la plateforme suit le cycle suivant :

1. **Publication :** le recruteur crée une offre de stage en précisant les informations nécessaires.
2. **Candidature :** le stagiaire consulte les offres et soumet sa candidature.
3. **Sélection :** le recruteur examine les dossiers et accepte ou refuse les candidatures.
4. **Affectation :** après acceptation, le stagiaire est associé à un encadrant.
5. **Planification :** l’encadrant définit les objectifs et les tâches à réaliser.
6. **Suivi :** l’encadrant suit la progression et consigne ses remarques.
7. **Évaluation :** les résultats du stage sont évalués à la fin de la période.

## 🛠️ Technologies utilisées

| Technologie | Utilisation |
|---|---|
| Python | Langage de programmation principal |
| Flask | Développement de l’application web |
| SQLAlchemy | Mapping objet-relationnel et accès aux données |
| SQL | Gestion et interrogation des données relationnelles |
| HTML5 | Structure des pages web |
| CSS3 | Mise en forme et présentation |
| JavaScript | Interactions côté client |
| Bootstrap | Conception d’interfaces web adaptatives |

**Base de données :** MySQL.

## 🏗️ Architecture générale

L’application suit une architecture web organisée autour de plusieurs composants :

- **Couche présentation :** interfaces HTML, CSS, JavaScript et Bootstrap.
- **Couche applicative :** routes Flask et logique métier.
- **Couche données :** modèles SQLAlchemy et base de données relationnelle.

Les principales entités métier sont :

- `User` : utilisateurs et informations associées aux rôles.
- `Offer` : offres de stage.
- `Application` : candidatures et statuts de traitement.
- `Internship` : informations relatives aux stages.
- `Task` : tâches attribuées aux stagiaires.
- `Evaluation` : évaluations des stages.

La structure exacte des modèles dépend de l’implémentation du projet.

## 📂 Structure du projet

Exemple d’organisation du code :

```text
Gestion-candidatures-suivi-stagiaires/
│
├── app.py
├── config.py
├── requirements.txt
│
├── models/
│   ├── user.py
│   ├── offer.py
│   ├── application.py
│   ├── internship.py
│   ├── task.py
│   └── evaluation.py
│
├── routes/
│   ├── auth.py
│   ├── recruiter.py
│   ├── student.py
│   └── supervisor.py
│
├── templates/
│   ├── auth/
│   ├── recruiter/
│   ├── student/
│   └── supervisor/
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
└── README.md
```


## ⚙️ Installation et lancement

### Prérequis

- Python 3.10 ou version compatible avec les dépendances du projet.
- pip.
- Git.
- Une base de données configurée selon les paramètres de l’application.

### 1. Cloner le dépôt

```bash
git clone https://github.com/NajLaBm/Gestion-candidatures-suivi-stagiaires.git
cd Gestion-candidatures-suivi-stagiaires
```

### 2. Créer un environnement virtuel

Sous Windows :

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer la base de données

Configurer les paramètres de connexion dans le fichier de configuration prévu à cet effet. Vérifier également les éventuelles variables d’environnement nécessaires au lancement de l’application.

### 5. Lancer l’application

Si le point d’entrée du projet est `app.py` :

```bash
python app.py
```

Ouvrir ensuite dans le navigateur l’adresse locale indiquée par Flask, généralement `http://127.0.0.1:5000`.

## 🧪 Tests et validation

Le développement d’une application de ce type nécessite notamment de vérifier :

- L’authentification et les autorisations associées aux rôles.
- La création et la gestion des offres.
- Le dépôt et le traitement des candidatures.
- L’affectation des stagiaires aux encadrants.
- L’attribution et le suivi des tâches.
- L’enregistrement des évaluations.
- La cohérence et l’intégrité des données.

## 🚀 Perspectives d’évolution

Les améliorations possibles comprennent :

- Un tableau de bord avec des indicateurs clés sur les candidatures et les stages.
- Des notifications automatiques lors des changements de statut.
- Des statistiques sur les offres, les candidatures et la progression des stagiaires.
- Une fonctionnalité de rapprochement entre les compétences des candidats et les exigences des offres.
- L’export de rapports de suivi et d’évaluation.

Ces éléments constituent des pistes d’évolution et ne sont pas nécessairement implémentés dans la version actuelle.

## 💡 Valeur ajoutée

Cette plateforme vise à structurer le processus de recrutement et le suivi des stages dans un environnement centralisé. Elle relie les besoins du recruteur, les démarches du stagiaire et les missions de l’encadrant au sein d’un même processus métier.

Le projet met en pratique le développement web avec Python, la conception de modèles de données relationnels, l’implémentation de règles métier et la gestion des interactions entre plusieurs profils utilisateurs.

## 👩‍💻 Auteur

**Najia Ben Mahmoud**

- GitHub : [NajLaBm](https://github.com/NajLaBm)
- Portfolio : [najia-benmahmoud.netlify.app](https://najia-benmahmoud.netlify.app)

---

*Projet de développement web consacré à la digitalisation du recrutement et au suivi des stages.*
