from flask import Flask, render_template
from flask import Flask, render_template, request
from verbecc import Conjugator
from flask_sqlalchemy import SQLAlchemy
from models import db, Mode, Conjugaison
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session, redirect, flash
from models import db, Utilisateur
from flask import Flask, render_template, request, redirect, flash, session, url_for
from models import Historique
from datetime import datetime
import csv
from flask import request
from models import Cours
import io




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

    



# def get_definition(verbe):
#     url = f"https://fr.wiktionary.org/wiki/{verbe}"
#     try:
#         response = requests.get(url, timeout=5)
#         if response.status_code != 200:
#             return "Définition non disponible."

#         soup = BeautifulSoup(response.text, "html.parser")

#         # Trouve la section Français
#         francais = soup.find('span', {'id': 'Français'})
#         if not francais:
#             return "Définition non trouvée."

#         h2 = francais.find_parent("h2")

#         # Cherche les éléments suivants jusqu'à la prochaine section
#         current = h2.find_next_sibling()
#         while current:
#             if current.name == 'h2':  # Fin de la section Français
#                 break
#             if current.name == 'ol':
#                 li = current.find("li")
#                 if li:
#                     return li.text.strip()
#             current = current.find_next_sibling()

#     except Exception as e:
#         print("Erreur BeautifulSoup définition :", e)
#         return "Erreur lors de la récupération de la définition."

#     return "Définition non trouvée."





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
        prenom = request.form['prenom']  
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


@app.route('/cours')
def cours():
    tous_les_cours = Cours.query.all()
    return render_template('cours.html', cours=tous_les_cours)


@app.route('/cours/<int:id>')
def cours_detail(id):
    cours = Cours.query.get_or_404(id)
    return render_template('cours_detail.html', cours=cours)


@app.route('/exercices')
def exercices():
    return render_template('exercices.html')

@app.route('/chatbot')
def chatbot():
    return "Page Chatbot (à faire)"






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
    definition = ""

    if request.method == 'POST':
        verbe = request.form.get('verbe', '').strip().lower()
    elif request.method == 'GET':
        verbe = request.args.get('verbe', '').strip().lower()

    if verbe:
        try:
            resultats = Conjugaison.query.filter_by(verbe=verbe).all()
            if resultats:
                for conj in resultats:
                    mode_nom = conj.mode.nom
                    if mode_nom not in conjugaisons:
                        conjugaisons[mode_nom] = {}
                    conjugaisons[mode_nom][conj.temps] = conj.conjugaisons.split("\n")
                groupe = resultats[0].groupe
                pronominal = resultats[0].pronominal
            else:
                conj = Conjugator(lang='fr')
                result = conj.conjugate(verbe)
                moods = result.get("moods", {})

                if verbe.endswith("er") and verbe != "aller":
                    groupe = "1er"
                elif verbe.endswith("ir") and verbe not in verbes_3e_groupe_ir:
                    groupe = "2e"
                else:
                    groupe = "3e"

                if verbe.startswith("se ") or verbe.startswith("s'"):
                    pronominal = True

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
                            if mode_nom not in conjugaisons:
                                conjugaisons[mode_nom] = {}
                            conjugaisons[mode_nom][temps_nom] = formes
                db.session.commit()

            # ✅ HISTORIQUE (doit être EN DEHORS du `if resultats` et `else`)
            utilisateur_id = session.get('utilisateur_id')
            if utilisateur_id:
                mode_inf = Mode.query.filter_by(nom="Infinitif").first()
                if mode_inf:
                    infinitif = Conjugaison.query.filter_by(
                        verbe=verbe,
                        mode_id=mode_inf.id,
                        temps="infinitif-présent"
                    ).first()
                    if infinitif:
                        existe = Historique.query.filter_by(
                            utilisateur_id=utilisateur_id,
                            conjugaison_id=infinitif.id
                        ).first()
                        if not existe:
                            historique = Historique(
                                utilisateur_id=utilisateur_id,
                                conjugaison_id=infinitif.id,
                                date_consultation=datetime.now()
                            )
                            db.session.add(historique)
                            db.session.commit()
                            print("✅ Historique ajouté")
                    

        except Exception as e:
            print("Erreur globale :", e)
            definition = "Erreur lors de la récupération."

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

    

@app.route('/importer-cours', methods=['GET', 'POST'])
def importer_cours():
    if request.method == 'POST':
        fichier = request.files['fichier']
        if fichier.filename.endswith('.csv'):
            # ✅ Utilise io.StringIO pour gérer les sauts de ligne
            fichier_stream = io.StringIO(fichier.stream.read().decode("utf-8"))
            reader = csv.DictReader(fichier_stream)

            for ligne in reader:
                titre = ligne.get('titre', '').strip()
                contenu = ligne.get('contenu', '').strip()

                # Vérifie que contenu n’est pas vide
                if contenu and not Cours.query.filter_by(titre=titre).first():
                    cours = Cours(titre=titre, contenu=contenu)
                    db.session.add(cours)

            db.session.commit()
            return "Importation réussie !"
        else:
            return "Format non pris en charge. Veuillez fournir un fichier .csv"

    return '''
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="fichier" accept=".csv">
            <button type="submit">Importer</button>
        </form>
    '''



@app.route('/deconnexion')
def deconnexion():
    session.pop('utilisateur_id', None)
    flash("")
    return redirect(url_for('accueil'))


if __name__ == '__main__':
    app.run(debug=True)


