from flask import Flask, render_template
from flask import Flask, render_template, request
from verbecc import Conjugator
from flask_sqlalchemy import SQLAlchemy
from models import db, Mode, Conjugaison
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session, redirect, flash
from models import db, Utilisateur
from flask import Flask, render_template, request, redirect, flash, session, url_for


app = Flask(__name__)
app.secret_key = 'ta_clé_secrète'

# Configuration MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/App_Conjugaison'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisation de SQLAlchemy
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/')
def accueil():
    return render_template('accueil.html')



@app.route('/connexion', methods=['GET', 'POST'])
def connexion():
    if request.method == 'POST':
        email = request.form['email']
        mot_de_passe = request.form['mot_de_passe']

        utilisateur = Utilisateur.query.filter_by(email=email).first()

        if utilisateur and check_password_hash(utilisateur.mot_de_passe, mot_de_passe):
            session['utilisateur_id'] = utilisateur.id
            flash("")
            if utilisateur.role == 'admin':
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('user'))

        else:
            flash("Identifiants incorrects.")

    return render_template('connexion.html')

@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']  # 👈 AJOUT ICI
        email = request.form['email']
        mot_de_passe = generate_password_hash(request.form['mot_de_passe'])
        role = 'user'  # Par défaut

        # Vérifie que l'email n'est pas déjà utilisé
        if Utilisateur.query.filter_by(email=email).first():
            flash("Cet email est déjà utilisé.")
            return redirect(url_for('inscription'))

        nouvel_utilisateur = Utilisateur(
            nom=nom,
            prenom=prenom,
            email=email,
            mot_de_passe=mot_de_passe,
            role=role
        )

        db.session.add(nouvel_utilisateur)
        db.session.commit()
        flash("Inscription réussie.")
        return redirect(url_for('connexion'))

    return render_template('inscription.html')


@app.route('/apprentissage')
def apprentissage():
    return render_template('apprentissage.html')


@app.route('/exercices')
def exercices():
    return render_template('exercices.html')




# Liste (incomplète mais fonctionnelle) de verbes en -ir qui appartiennent au 3e groupe
verbes_3e_groupe_ir = [
    "acquérir", "assaillir", "bouillir", "courir", "couvrir",
    "cueillir", "défaillir", "dormir", "endormir", "fuir", 
    "mentir", "mourir", "offrir", "ouvrir", "partir", 
    "recueillir", "ressentir", "revenir", "sentir", 
    "servir", "sortir", "souffrir", "survenir", "tenir", 
    "venir", "se repentir", "s'endormir", "se sentir",
    "maintenir", "retenir", "contenir", "entretenir",
    "prévenir", "intervenir", "se souvenir", "soutenir",
    "subvenir", "se couvrir", "découvrir", "se mourir",
    "s'offrir", "se servir", "s'endormir", "pouvoir","voir", "vouloir", "avoir"
]

@app.route('/conjugaison', methods=['GET', 'POST'])
def conjugaison():
    verbe = ''
    conjugaisons = {}
    groupe = "Inconnu"
    pronominal = False

    if request.method == 'POST':
        verbe = request.form.get('verbe', '').strip().lower()
    elif request.method == 'GET':
        verbe = request.args.get('verbe', '').strip().lower()

    if verbe:
        try:
            # 1️⃣ Vérifier si le verbe existe en base (au moins une conjugaison)
            resultats = Conjugaison.query.filter_by(verbe=verbe).all()

            if resultats:
                # Regrouper les conjugaisons par mode et temps
                for conj in resultats:
                    mode_nom = conj.mode.nom
                    if mode_nom not in conjugaisons:
                        conjugaisons[mode_nom] = {}
                    conjugaisons[mode_nom][conj.temps] = conj.conjugaisons.split("\n")
                
                # Récupérer groupe et pronominal à partir de la première ligne (optimisation)
                groupe = resultats[0].groupe
                pronominal = resultats[0].pronominal

            else:
                # 2️⃣ Sinon, appeler Verbecc et enregistrer
                conj = Conjugator(lang='fr')
                result = conj.conjugate(verbe)
                moods = result.get("moods", {})

                # Détection du groupe
                if verbe.endswith("er") and verbe != "aller":
                    groupe = "1er"
                elif verbe.endswith("ir") and verbe not in verbes_3e_groupe_ir:
                    groupe = "2e"
                else:
                    groupe = "3e"

                # Verbe pronominal
                if verbe.startswith("se ") or verbe.startswith("s'"):
                    pronominal = True

                # Enregistrer les conjugaisons
                for mode_nom, temps_dict in moods.items():
                    mode = Mode.query.filter_by(nom=mode_nom).first()
                    if not mode:
                        mode = Mode(nom=mode_nom)
                        db.session.add(mode)
                        db.session.commit()

                    for temps_nom, formes in temps_dict.items():
                        existe = Conjugaison.query.filter_by(
                            verbe=verbe, temps=temps_nom, mode_id=mode.id
                        ).first()

                        if not existe:
                            nouv = Conjugaison(
                                verbe=verbe,
                                groupe=groupe,
                                pronominal=pronominal,
                                temps=temps_nom,
                                conjugaisons="\n".join(formes),
                                mode_id=mode.id
                            )
                            db.session.add(nouv)

                            # Ajouter aussi dans le dict pour l'affichage
                            if mode_nom not in conjugaisons:
                                conjugaisons[mode_nom] = {}
                            conjugaisons[mode_nom][temps_nom] = formes

                db.session.commit()

        except Exception as e:
            print("Erreur :", e)

    return render_template("conjugaison.html",
                           verbe=verbe,
                           conjugaisons=conjugaisons,
                           groupe=f"{groupe} groupe" if groupe in ["1er", "2e", "3e"] else groupe,
                           pronominal="oui" if pronominal else "non")



@app.route('/espace')
def espace():
    if 'utilisateur_id' not in session:
        flash("Veuillez vous connecter pour accéder à cette page.")
        return redirect(url_for('connexion'))

    return "Bienvenue dans l’espace membre"

@app.route('/user')
def user():
    if 'utilisateur_id' not in session:
        flash("Veuillez vous connecter.")
        return redirect(url_for('connexion'))

    utilisateur = Utilisateur.query.get(session['utilisateur_id'])
    return render_template('user.html', utilisateur=utilisateur)


@app.route('/admin')
def admin():
    if 'utilisateur_id' not in session:
        flash("Veuillez vous connecter.")
        return redirect(url_for('connexion'))

    utilisateur = Utilisateur.query.get(session['utilisateur_id'])

    if utilisateur.role != 'admin':
        flash("Accès réservé à l'administrateur.")
        return redirect(url_for('connexion'))

    return render_template('admin.html', utilisateur=utilisateur)


@app.route('/deconnexion')
def deconnexion():
    session.pop('utilisateur_id', None)
    flash("")
    return redirect(url_for('accueil'))


if __name__ == '__main__':
    app.run(debug=True)


