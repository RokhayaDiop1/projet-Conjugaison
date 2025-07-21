from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()

class Mode(db.Model):
    __tablename__ = 'mode'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)

    conjugaisons = db.relationship('Conjugaison', backref='mode', lazy=True)

class Conjugaison(db.Model):
    __tablename__ = 'conjugaison'
    id = db.Column(db.Integer, primary_key=True)
    verbe = db.Column(db.String(100), nullable=False)
    groupe = db.Column(db.String(50))
    pronominal = db.Column(db.Boolean)
    temps = db.Column(db.String(100))
    conjugaisons = db.Column(db.Text)
    mode_id = db.Column(db.Integer, db.ForeignKey('mode.id'))

    __table_args__ = (db.UniqueConstraint('verbe', 'temps', 'mode_id', name='unique_conjugaison'),)

class Utilisateur(db.Model):
    __tablename__ = 'utilisateur'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mot_de_passe = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')
    bloque = db.Column(db.Boolean, default=False)


class Connexion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateur.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    utilisateur = db.relationship('Utilisateur', backref='connexions')



    

class Historique(db.Model):
    __tablename__ = 'historiques'

    id = db.Column(db.Integer, primary_key=True)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateur.id'), nullable=True)
    conjugaison_id = db.Column(db.Integer, db.ForeignKey('conjugaison.id'), nullable=False)
    date_consultation = db.Column(db.DateTime, default=datetime.utcnow)

    utilisateur = db.relationship('Utilisateur', backref='historiques')
    conjugaison = db.relationship('Conjugaison', backref='historiques')



class Cours(db.Model):
    __tablename__ = 'cours'

    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(255), nullable=False)
    contenu = db.Column(db.Text, nullable=False)  

    def __repr__(self):
        return f"<Cours {self.titre}>"
    

class Exercice(db.Model):
    __tablename__ = 'exercices'
    
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(255))  # ➕ Nouveau champ
    type = db.Column(db.String(50))  # qcm, saisie, trou, ordre, etc.
    question = db.Column(db.Text)
    reponse = db.Column(db.Text)
    choix = db.Column(db.Text)  # Pour QCM ou options, séparés par ;
    niveau = db.Column(db.String(50))  # débutant, intermédiaire, avancé


class Resultat(db.Model):
    __tablename__ = 'resultats'

    id = db.Column(db.Integer, primary_key=True)
    exercice_id = db.Column(db.Integer, db.ForeignKey('exercices.id'), nullable=False)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateur.id'), nullable=True)  # optionnel
    reponse_donnee = db.Column(db.String(255))
    score = db.Column(db.Integer)
    date_reponse = db.Column(db.DateTime, default=datetime.utcnow)

    exercice = db.relationship('Exercice', backref='resultats')
