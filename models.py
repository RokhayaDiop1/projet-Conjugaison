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