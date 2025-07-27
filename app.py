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
from models import Exercice
from models import Resultat
from models import Connexion
from models import Quiz
from sqlalchemy import func
from flask import jsonify
from flask import send_file, render_template, redirect, url_for, flash, request, session
from models import db, Cours 
from flask import make_response
from flask import render_template_string
import io
import markdown
import pdfkit
from datetime import datetime, timedelta
import json
from flask import request, render_template, session
from datetime import datetime
from verbecc import Conjugator
from bs4 import BeautifulSoup
import requests


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
        email = request.form.get('email')
        mot_de_passe = request.form.get('mot_de_passe')
        
        utilisateur = Utilisateur.query.filter_by(email=email).first()

        if utilisateur and check_password_hash(utilisateur.mot_de_passe, mot_de_passe):
            # ✅ Stocker l'ID dans la session
            session['utilisateur_id'] = utilisateur.id

            # ✅ Enregistrer la connexion
            nouvelle_connexion = Connexion(
                utilisateur_id=utilisateur.id,
                date_connexion=datetime.utcnow()
            )
            db.session.add(nouvelle_connexion)
            db.session.commit()

            flash("Connexion réussie.")

            # ✅ Redirection selon le rôle
            if utilisateur.role == 'admin':
                return redirect(url_for('admin'))
            elif utilisateur.role == 'professeur':
                return redirect(url_for('professeur'))
            else:
                return redirect(url_for('user'))
        
        else:
            flash("Email ou mot de passe incorrect.")

    return render_template('connexion.html')





@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        email = request.form['email']
        mot_de_passe = generate_password_hash(request.form['mot_de_passe'])
        role = 'user'

        if Utilisateur.query.filter_by(email=email).first():
            flash("Cet email est déjà utilisé.")
            return redirect(url_for('inscription'))

        nouvel_utilisateur = Utilisateur(nom=nom, prenom=prenom, email=email, mot_de_passe=mot_de_passe, role=role)
        db.session.add(nouvel_utilisateur)
        db.session.commit()
        return redirect(url_for('connexion'))

    return render_template('inscription.html')


@app.route('/mot_de_passe_oublie', methods=['GET', 'POST'])
def mot_de_passe_oublie():
    if request.method == 'POST':
        email = request.form['email'].strip()
        utilisateur = Utilisateur.query.filter_by(email=email).first()

        if utilisateur:
            
            flash("Si cet email est enregistré, un lien de réinitialisation a été envoyé.")
        else:
            flash("Aucun utilisateur trouvé avec cet email.")

    return render_template('mot_de_passe_oublie.html')



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
    contenu_html = markdown.markdown(cours.contenu, extensions=["tables", "fenced_code"])
    return render_template('cours_detail.html', cours=cours, contenu_html=contenu_html)





@app.route('/cours/<int:id>/telecharger')
def telecharger_cours(id):
    cours = Cours.query.get_or_404(id)
    rendered = render_template('cours_pdf.html', cours=cours, contenu_html=cours.contenu)

    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

    pdf = pdfkit.from_string(rendered, False, configuration=config)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={cours.titre}.pdf'

    return response


@app.route('/cours/<int:id>/quiz')
def get_quiz(id):
    quizzes = Quiz.query.filter_by(cours_id=id).all()
    data = [{
        "question": q.question,
        "choix": q.choix,
        "bonne_reponse": q.bonne_reponse
    } for q in quizzes]
    return jsonify(data)



@app.route('/exercices')
def exercices():
    return render_template('exercices.html')


# ⚙️ Barème de points selon le niveau
points_par_niveau = {
    'débutant': 3,
    'intermédiaire': 5,
    'avancé': 7
}



@app.route('/exercices/qcm', methods=['GET', 'POST'])
def exercices_qcm():
    niveau = request.args.get('niveau') or session.get('niveau_selectionne')
    if not niveau:
        return render_template('exercices_qcm.html', exercice=None)

    # Réinitialiser si changement de niveau
    if niveau != session.get('niveau_selectionne'):
        session['qcm_index'] = 0
        session['niveau_selectionne'] = niveau
        session['score_session'] = 0  # 🔸 Initialiser le score pour la session
        session.pop('reponse_donnee', None)
        session.pop('afficher_correction', None)


    exercices = Exercice.query.filter_by(type='qcm', niveau=niveau).all()
    if not exercices:
        return render_template('exercices_qcm.html', exercice=None)

    if 'qcm_index' not in session:
        session['qcm_index'] = 0

    index = session['qcm_index']

    # ➤ si "suivant" est cliqué, on passe à l'exercice suivant
    if request.args.get('suivant') == '1':
        session['qcm_index'] += 1
        return redirect(url_for('exercices_qcm', niveau=niveau))

    if index >= len(exercices):
        total_score = session.get('score_session', 0)
        total_possible = len(exercices) * (
            3 if niveau == 'débutant' else 5 if niveau == 'intermédiaire' else 7
        )
        session.pop('qcm_index', None)
        session.pop('niveau_selectionne', None)
        session.pop('score_session', None)  # 🔸 on peut vider le score ensuite

        return render_template(
            'exercices_qcm.html',
            exercice=None,
            niveau=niveau,
            afficher_modal_score=True,
            total_score=total_score,
            total_possible=total_possible
        )

    exercice = exercices[index]

    if request.method == 'POST':
        reponse_donnee = request.form['reponse']
        est_correcte = (reponse_donnee.strip() == exercice.reponse.strip())

        score = 0
        if est_correcte:
            score = 3 if niveau == 'débutant' else 5 if niveau == 'intermédiaire' else 7
            session['score_session'] = session.get('score_session', 0) + score


        resultat = Resultat(
            exercice_id=exercice.id,
            utilisateur_id=session.get('utilisateur_id'),
            reponse_donnee=reponse_donnee,
            score=score
        )
        db.session.add(resultat)
        db.session.commit()

        session['reponse_donnee'] = reponse_donnee
        session['afficher_correction'] = True
        return redirect(url_for('exercices_qcm', niveau=niveau))

    reponse_donnee = session.pop('reponse_donnee', None)
    afficher_correction = session.pop('afficher_correction', False)
    progression = int((index + 1) / len(exercices) * 100)

    return render_template(
        'exercices_qcm.html',
        exercice=exercice,
        niveau=niveau,
        numero_question=index + 1,
        total_questions=len(exercices),
        progression=progression,
        reponse_donnee=reponse_donnee,
        show_quiz=True
    )





@app.route('/exercices/trou', methods=['GET', 'POST'])
def exercices_trou():
    niveau = request.args.get('niveau') or session.get('niveau_trou')
    if not niveau:
        return render_template('exercices_trou.html', exercice=None)

    if niveau != session.get('niveau_trou'):
        session['niveau_trou'] = niveau
        session['index_trou'] = 0
        session['score_trou'] = 0

    exercices = Exercice.query.filter_by(type='trou', niveau=niveau).all()
    if not exercices:
        return render_template('exercices_trou.html', exercice=None)

    index = session.get('index_trou', 0)

    if index >= len(exercices):
        total_score = session.pop('score_trou', 0)
        total_possible = len(exercices) * (
            3 if niveau == 'débutant' else 5 if niveau == 'intermédiaire' else 7
        )
        session.pop('niveau_trou', None)
        session.pop('index_trou', None)
        return render_template('exercices_trou.html',
                               exercice=None,
                               afficher_modal_score=True,
                               total_score=total_score,
                               total_possible=total_possible,
                               niveau=niveau)

    exercice = exercices[index]

    if request.method == 'POST':
        reponse_donnee = request.form.get('reponse', '').strip().lower()
        bonne_reponse = exercice.reponse.strip().lower()
        est_correcte = reponse_donnee == bonne_reponse

        score = 0
        if est_correcte:
            score = 3 if niveau == 'débutant' else 5 if niveau == 'intermédiaire' else 7

        resultat = Resultat(
            exercice_id=exercice.id,
            utilisateur_id=session.get('utilisateur_id'),
            reponse_donnee=reponse_donnee,
            score=score
        )
        db.session.add(resultat)
        db.session.commit()

        session['score_trou'] += score
        session['index_trou'] = index + 1

        return redirect(url_for('exercices_trou', niveau=niveau))

    progression = int((index + 1) / len(exercices) * 100)

    return render_template('exercices_trou.html',
                           exercice=exercice,
                           niveau=niveau,
                           numero_question=index + 1,
                           total_questions=len(exercices),
                           progression=progression)


@app.route('/exercices/libre')
def exercices_libre():
    exercices = Exercice.query.filter_by(type='libre').all()
    return render_template('exercices_libre.html', exercices=exercices)


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






def verbe_est_un_verbe_wiktionnaire(verbe):
    url = f"https://fr.wiktionary.org/wiki/{verbe}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return False
        soup = BeautifulSoup(response.text, "html.parser")
        fr_section = soup.find("span", id="Français")
        if not fr_section:
            return False
        current = fr_section.find_parent()
        while current and current.name != "h2":
            current = current.find_next_sibling()
        while current:
            if current.name in ["h3", "h4"] and "Verbe" in current.text:
                return True
            current = current.find_next_sibling()
        return False
    except:
        return False




def get_definition_depuis_wiktionnaire(verbe):
    try:
        url = f"https://fr.wiktionary.org/wiki/{verbe}"
        response = requests.get(url)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        section_fr = soup.find('span', id='Français')
        if not section_fr:
            return None

        ol = section_fr.find_next('ol')
        if ol:
            return ol.find('li').get_text()
        return None
    except Exception as e:
        print(f"Erreur de définition : {e}")
        return None





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
                # Vérifier si c’est un vrai verbe
                definition = get_definition_depuis_wiktionnaire(verbe)
                if not definition:
                    definition = f"⚠️ Le mot « {verbe} » n’est pas reconnu comme un verbe."
                    return render_template("conjugaison.html",
                                           verbe=verbe,
                                           conjugaisons={},
                                           groupe="Inconnu",
                                           pronominal="non",
                                           definition=definition)

                # Si c'est un vrai verbe, on le conjugue avec verbecc
                conj = Conjugator(lang='fr')
                result = conj.conjugate(verbe)
                moods = result.get("moods", {})

                if verbe.endswith("er") and verbe != "aller":
                    groupe = "1er"
                elif verbe.endswith("ir") and verbe not in ['courir', 'mourir', 'fuir']:  # à adapter
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

                # Historique
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

        except Exception as e:
            print("Erreur globale :", e)
            definition = "❌ Erreur lors de la récupération de la conjugaison."

    return render_template("conjugaison.html",
                           verbe=verbe,
                           conjugaisons=conjugaisons,
                           groupe=f"{groupe} groupe" if groupe in ["1er", "2e", "3e"] else groupe,
                           pronominal="oui" if pronominal else "non",
                           definition=definition)



@app.route('/espace')
def espace():
    if 'utilisateur_id' not in session:
        flash("Veuillez vous connecter pour accéder à cette page.")
        return redirect(url_for('connexion'))

    return "Bienvenue dans l'espace membre"

def calculer_niveau_et_progression(total_points):
    # Progression sur 100 points max
    progression = min(int(total_points), 100)

    if progression < 30:
        niveau = "Débutant"
    elif progression < 60:
        niveau = "Intermédiaire"
    else:
        niveau = "Avancé"

    return niveau, progression

    


@app.route('/user')
def user():
    if 'utilisateur_id' not in session:
        flash("Veuillez vous connecter.")
        return redirect(url_for('connexion'))

    utilisateur = Utilisateur.query.get(session['utilisateur_id'])

    # 🔸 Récupérer les historiques
    historiques = (
        db.session.query(Historique, Conjugaison)
        .join(Conjugaison, Historique.conjugaison_id == Conjugaison.id)
        .join(Mode, Conjugaison.mode_id == Mode.id)
        .filter(Historique.utilisateur_id == utilisateur.id)
        .order_by(Historique.date_consultation.desc())
        .limit(10)
        .all()
    )
    total_verbes = len(historiques)
    verbes_historiques = list({conj.verbe for _, conj in historiques})

    # 🔹 Conjugaisons et corrections
    conjugaisons = (
        db.session.query(Conjugaison, Mode)
        .join(Mode, Conjugaison.mode_id == Mode.id)
        .filter(Conjugaison.verbe.in_(verbes_historiques))
        .all()
    )

    corrections_par_verbe_temps = {}
    temps_par_verbe = {}

    for conj, mode in conjugaisons:
        key = f"{mode.nom}||{conj.temps}"
        if conj.verbe not in corrections_par_verbe_temps:
            corrections_par_verbe_temps[conj.verbe] = {}
            temps_par_verbe[conj.verbe] = []
        corrections_par_verbe_temps[conj.verbe][key] = conj.conjugaisons
        temps_par_verbe[conj.verbe].append((mode.nom, conj.temps))

    # 🔸 Progression et niveau depuis la table Resultat
    total_points = db.session.query(db.func.sum(Resultat.score)).filter_by(utilisateur_id=utilisateur.id).scalar() or 0
    niveau, progression = calculer_niveau_et_progression(total_points)
    utilisateur.niveau = niveau


    return render_template(
        'user.html',
        utilisateur=utilisateur,
        historique=historiques,
        total_verbes=total_verbes,
        progression=progression,
        corrections_par_verbe_temps=corrections_par_verbe_temps,
        temps_par_verbe=temps_par_verbe,
        verbes_historiques=verbes_historiques
    )


@app.route('/professeur')
def professeur():
    if 'utilisateur_id' not in session:
        flash("Veuillez vous connecter.")
        return redirect(url_for('connexion'))

    utilisateur = Utilisateur.query.get(session['utilisateur_id'])
    if utilisateur.role != 'professeur':
        flash("Accès réservé aux professeurs.")
        return redirect(url_for('connexion'))

    total_utilisateurs = Utilisateur.query.count()
    total_cours = Cours.query.count()
    total_historiques = Historique.query.count()
    total_exercices = Exercice.query.count()


    return render_template('professeur.html',
                       utilisateur=utilisateur,
                       total_utilisateurs=total_utilisateurs,
                       total_cours=total_cours,
                       total_historiques=total_historiques,
                       total_exercices=total_exercices)






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



@app.route('/gerer_cours', methods=['GET', 'POST'])
def gerer_cours():
    if 'utilisateur_id' not in session:
        flash("Veuillez vous connecter.")
        return redirect(url_for('connexion'))

    utilisateur = Utilisateur.query.get(session['utilisateur_id'])
    if utilisateur.role != 'professeur':
        return redirect(url_for('connexion'))

    # Ajouter un cours
    if request.method == 'POST':
        titre = request.form['titre']
        contenu = request.form['contenu']
        if titre and contenu:
            nouveau_cours = Cours(titre=titre, contenu=contenu)
            db.session.add(nouveau_cours)
            db.session.commit()
            return redirect(url_for('gerer_cours'))

    cours = Cours.query.all()
    return render_template('gerer_cours.html', utilisateur=utilisateur, cours=cours)



import markdown

@app.route('/ajouter_cours', methods=['GET', 'POST'])
def ajouter_cours():
    if request.method == 'POST':
        titre = request.form['titre'].strip()
        contenu_brut = request.form['contenu'].strip()

        # Convertir le Markdown en HTML
        contenu_html = markdown.markdown(
            contenu_brut, extensions=['extra', 'tables', 'fenced_code']
        )

        cours = Cours(titre=titre, contenu=contenu_html)
        db.session.add(cours)
        db.session.commit()

        flash("Cours ajouté avec succès.")
        return redirect(url_for('gerer_cours'))

    return render_template('ajouter_cours.html')





@app.route('/modifier_cours', methods=['GET', 'POST'])
def modifier_cours():
    cours_id = request.args.get('id')
    cours = None

    if cours_id:
        cours = Cours.query.get_or_404(cours_id)

    if request.method == 'POST':
        id_cours = request.form['id']
        titre = request.form['titre'].strip()
        contenu_html = request.form['contenu'].strip()  # ✅ On garde le HTML tel quel

        cours_modif = Cours.query.get_or_404(id_cours)
        cours_modif.titre = titre
        cours_modif.contenu = contenu_html  # ✅ Pas de transformation

        db.session.commit()
        flash("Cours modifié avec succès.")
        return redirect(url_for('modifier_cours', id=id_cours))  # Garde l'ID pour rester sur le même cours

    tous_les_cours = Cours.query.all()
    return render_template('modifier_cours.html', cours=cours, cours_list=tous_les_cours)

@app.route('/ajouter_exercice', methods=['GET', 'POST'])
def ajouter_exercice():
    if request.method == 'POST':
        titre = request.form['titre'].strip()
        type_ex = request.form['type'].strip()
        niveau = request.form['niveau'].strip()
        question = request.form['question'].strip()
        reponse = request.form['reponse'].strip()
        choix = request.form.get('choix', '').strip()  # optionnel

        exercice = Exercice(
            titre=titre,
            type=type_ex,
            niveau=niveau,
            question=question,
            reponse=reponse,
            choix=choix
        )
        db.session.add(exercice)
        db.session.commit()
        flash("Exercice ajouté avec succès.")
        return redirect(url_for('ajouter_exercice'))

    return render_template('ajouter_exercice.html')

@app.route('/professeur/modifier_exercice')
@app.route('/professeur/modifier_exercice/<int:id>', methods=['GET', 'POST'])
def modifier_exercice(id=None):
    exercice = Exercice.query.get(id) if id else None
    exercices = Exercice.query.all()

    if request.method == 'POST' and exercice:
        exercice.titre = request.form['titre']
        exercice.type = request.form['type']
        exercice.niveau = request.form['niveau']
        exercice.question = request.form['question']
        exercice.choix = request.form.get('choix', '')
        exercice.reponse = request.form['reponse']
        db.session.commit()
        flash("Exercice modifié avec succès.")
        return redirect(url_for('modifier_exercice', id=exercice.id))

    return render_template("modifier_exercice.html", exercice=exercice, exercices=exercices)

@app.route('/admin/supprimer_exercice/<int:id>', methods=['POST'])
def supprimer_exercice(id):
    exercice = Exercice.query.get_or_404(id)
    db.session.delete(exercice)
    db.session.commit()
    flash("Exercice supprimé avec succès.")
    return redirect(url_for('modifier_exercice'))




@app.route('/admin')
def admin():
    if 'utilisateur_id' not in session:
        flash("Veuillez vous connecter.")
        return redirect(url_for('connexion'))

    utilisateur = Utilisateur.query.get(session['utilisateur_id'])

    if utilisateur.role != 'admin':
        flash("Accès réservé à l'administrateur.")
        return redirect(url_for('connexion'))

    utilisateurs = Utilisateur.query.all()
    
    return render_template(
        'admin.html',
        utilisateur=utilisateur,
        total_utilisateurs=len(utilisateurs),
        total_professeurs=len([u for u in utilisateurs if u.role == 'professeur']),
        total_eleves=len([u for u in utilisateurs if u.role == 'user'])
    )


@app.route('/admin/gestion_utilisateurs')
def gestion_utilisateurs():
    if 'utilisateur_id' not in session:
        flash("Veuillez vous connecter.")
        return redirect(url_for('connexion'))

    utilisateur = Utilisateur.query.get(session['utilisateur_id'])

    if utilisateur.role != 'admin':
        flash("Accès réservé à l'administrateur.")
        return redirect(url_for('connexion'))

    utilisateurs = Utilisateur.query.all()
    return render_template('admin_gestion_utilisateurs.html', utilisateurs=utilisateurs, utilisateur=utilisateur)






@app.route('/admin/utilisateur/<int:id>/changer_role', methods=['POST'])
def changer_role_utilisateur(id):
    if 'utilisateur_id' not in session:
        flash("Veuillez vous connecter.")
        return redirect(url_for('connexion'))

    admin = Utilisateur.query.get(session['utilisateur_id'])
    if admin.role != 'admin':
        flash("Accès réservé à l'administrateur.")
        return redirect(url_for('connexion'))

    utilisateur = Utilisateur.query.get_or_404(id)
    nouveau_role = request.form['nouveau_role']
    utilisateur.role = nouveau_role
    db.session.commit()
    flash(f"Rôle de {utilisateur.prenom} mis à jour en {nouveau_role}.", "success")
    return redirect(url_for('gestion_utilisateurs'))


@app.route('/admin/utilisateur/<int:id>/bloquer', methods=['POST'])
def bloquer_utilisateur(id):
    if 'utilisateur_id' not in session:
        flash("Connexion requise.")
        return redirect(url_for('connexion'))

    admin = Utilisateur.query.get(session['utilisateur_id'])
    if admin.role != 'admin':
        flash("Accès non autorisé.")
        return redirect(url_for('connexion'))

    utilisateur = Utilisateur.query.get_or_404(id)
    utilisateur.bloque = not utilisateur.bloque
    db.session.commit()

    action = "bloqué" if utilisateur.bloque else "débloqué"
    flash(f"⚠️ Utilisateur {utilisateur.prenom} a été {action}.", "warning")
    return redirect(url_for('gestion_utilisateurs'))







@app.route('/admin/statistiques')
def statistiques():
    if 'utilisateur_id' not in session:
        flash("Veuillez vous connecter.")
        return redirect(url_for('connexion'))

    utilisateur = Utilisateur.query.get(session['utilisateur_id'])

    if utilisateur.role != 'admin':
        flash("Accès réservé à l'administrateur.")
        return redirect(url_for('connexion'))

    # ✅ Calcul des 7 derniers jours
    aujourd_hui = datetime.utcnow().date()
    il_y_a_7_jours = aujourd_hui - timedelta(days=6)

    # ✅ Connexions limitées aux 7 derniers jours
    connexions_par_jour = (
        db.session.query(
            func.date(Connexion.date_connexion).label('date'),
            func.count(Connexion.id).label('nb_connexions')
        )
        .filter(Connexion.date_connexion >= il_y_a_7_jours)
        .group_by(func.date(Connexion.date_connexion))
        .order_by(func.date(Connexion.date_connexion))
        .all()
    )

    # ✅ Créer une liste complète pour chaque jour (même si 0 connexion)
    labels = [(il_y_a_7_jours + timedelta(days=i)).strftime('%d/%m') for i in range(7)]
    data_dict = {c.date.strftime('%d/%m'): c.nb_connexions for c in connexions_par_jour}
    data = [data_dict.get(day, 0) for day in labels]

    return render_template("admin_statistiques.html", labels=json.dumps(labels), data=json.dumps(data), utilisateur=utilisateur)




@app.route('/deconnexion')
def deconnexion():
    session.pop('utilisateur_id', None)
    flash("")
    return redirect(url_for('accueil'))


if __name__ == '__main__':
    app.run(debug=True)


