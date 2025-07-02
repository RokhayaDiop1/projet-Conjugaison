from flask import Flask, render_template
from flask import Flask, render_template, request
from verbecc import Conjugator


app = Flask(__name__)

@app.route('/')
def accueil():
    return render_template('accueil.html')

@app.route('/connexion')
def connexion():
    return render_template('connexion.html')

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
    "s'offrir", "se servir", "s'endormir", "pouvoir","voir", "vouloir"
]

@app.route('/conjugaison', methods=['GET', 'POST']) 
def conjugaison():
    verbe = ''
    conjugaisons = None
    groupe = "Inconnu"
    auxiliaire = "Inconnu"
    pronominal = "non"

    if request.method == 'POST':
        verbe = request.form.get('verbe', '').strip().lower()
    elif request.method == 'GET':
        verbe = request.args.get('verbe', '').strip().lower()

    if verbe:
        try:
            conj = Conjugator(lang='fr')
            result = conj.conjugate(verbe)
            print(result)

            # Conjugaisons
            conjugaisons = result.get("moods", {})

            # Groupe du verbe
            if verbe.endswith("er") and verbe != "aller":
                groupe = "verbe du 1er groupe"
            elif verbe.endswith("ir") and verbe not in verbes_3e_groupe_ir:
                groupe = "verbe du 2e groupe"
            else:
                groupe = "verbe du 3e groupe"

            # Verbe pronominal
            if verbe.startswith("se ") or verbe.startswith("s'"):
                pronominal = "oui"

            # Auxiliaire — méthode directe
            aux = result.get("auxiliary")
            if aux in ["avoir", "être"]:
                auxiliaire = aux
            else:
                # Méthode de secours : passer par le passé composé
                passe_compose = conjugaisons.get("indicatif", {}).get("passé composé", [])
                if passe_compose:
                    forme = passe_compose[0].lower()
                    mots = forme.split()
                    if len(mots) >= 2:
                        aux = mots[1]
                        if aux in ["suis", "es", "est", "sommes", "êtes", "sont"]:
                            auxiliaire = "être"
                        elif aux in ["ai", "as", "a", "avons", "avez", "ont"]:
                            auxiliaire = "avoir"
        except Exception as e:
            print("Erreur :", e)

    return render_template(
        "conjugaison.html",
        verbe=verbe,
        conjugaisons=conjugaisons,
        groupe=groupe,
        auxiliaire=auxiliaire,
        pronominal=pronominal
    )





if __name__ == '__main__':
    app.run(debug=True)
