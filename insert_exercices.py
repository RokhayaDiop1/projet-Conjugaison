from app import db
from models import Exercice

with app.app_context():

 exercices = [
    # 🟢 Débutant
    {"titre": "Débutant - savoir", "type": "trou", "question": "Il faut que tu ______ (savoir) la vérité.", "reponse": "saches", "choix": "", "niveau": "débutant"},
    {"titre": "Débutant - avoir", "type": "trou", "question": "______ (avoir) confiance en toi !", "reponse": "Aie", "choix": "", "niveau": "débutant"},
    {"titre": "Débutant - vouloir", "type": "trou", "question": "Elle ______ (vouloir) venir, mais elle était malade.", "reponse": "voulait", "choix": "", "niveau": "débutant"},
    {"titre": "Débutant - mettre", "type": "trou", "question": "Nous ______ (mettre) toujours nos manteaux en hiver.", "reponse": "mettons", "choix": "", "niveau": "débutant"},
    {"titre": "Débutant - croire", "type": "trou", "question": "Ils ______ (croire) à cette histoire incroyable ?", "reponse": "croient", "choix": "", "niveau": "débutant"},
    {"titre": "Débutant - partir", "type": "trou", "question": "En ______ (partir) si tôt, tu risques de te perdre.", "reponse": "partant", "choix": "", "niveau": "débutant"},
    {"titre": "Débutant - conduire", "type": "trou", "question": "Tu ______ (conduire) prudemment, n’est-ce pas ?", "reponse": "conduisais", "choix": "", "niveau": "débutant"},

    # 🟠 Intermédiaire
    {"titre": "Intermédiaire - lire", "type": "trou", "question": "Si j’avais le temps, je ______ (lire) ce livre.", "reponse": "lirais", "choix": "", "niveau": "intermédiaire"},
    {"titre": "Intermédiaire - prendre", "type": "trou", "question": "Il faut que nous ______ (prendre) une décision rapidement.", "reponse": "prenions", "choix": "", "niveau": "intermédiaire"},
    {"titre": "Intermédiaire - voir", "type": "trou", "question": "Vous ______ (voir) ce film si vous étiez venus plus tôt.", "reponse": "auriez vu", "choix": "", "niveau": "intermédiaire"},
    {"titre": "Intermédiaire - vivre", "type": "trou", "question": "En ______ (vivre) à l’étranger, elle a appris plusieurs langues.", "reponse": "vivant", "choix": "", "niveau": "intermédiaire"},
    {"titre": "Intermédiaire - boire", "type": "trou", "question": "Nous ______ (boire) un verre d’eau après le repas.", "reponse": "buvons", "choix": "", "niveau": "intermédiaire"},
    {"titre": "Intermédiaire - recevoir", "type": "trou", "question": "Il est important que vous ______ (recevoir) cette information.", "reponse": "receviez", "choix": "", "niveau": "intermédiaire"},
    {"titre": "Intermédiaire - savoir", "type": "trou", "question": "______ (savoir) reconnaître ses erreurs est une qualité rare.", "reponse": "Savoir", "choix": "", "niveau": "intermédiaire"},

    # 🔴 Avancé
    {"titre": "Avancé - résoudre", "type": "trou", "question": "Il aurait fallu qu’il ______ (résoudre) ce problème plus tôt.", "reponse": "eût résolu", "choix": "", "niveau": "avancé"},
    {"titre": "Avancé - arriver", "type": "trou", "question": "Dès que vous ______ (arriver), nous commencerons.", "reponse": "serez arrivés", "choix": "", "niveau": "avancé"},
    {"titre": "Avancé - mourir", "type": "trou", "question": "Bien qu’elle ______ (mourir) jeune, elle a marqué son époque.", "reponse": "soit morte", "choix": "", "niveau": "avancé"},
    {"titre": "Avancé - plaire", "type": "trou", "question": "______ (Plaire) à tout le monde est impossible.", "reponse": "Plaire", "choix": "", "niveau": "avancé"},
    {"titre": "Avancé - atteindre", "type": "trou", "question": "Si nous ______ (atteindre) notre but, tout aurait changé.", "reponse": "avions atteint", "choix": "", "niveau": "avancé"},
    {"titre": "Avancé - peindre", "type": "trou", "question": "Il exigeait que je ______ (peindre) le mur avant ce soir.", "reponse": "peigne", "choix": "", "niveau": "avancé"},
    {"titre": "Avancé - falloir", "type": "trou", "question": "Il serait parti plus tôt s’il ______ (falloir) vraiment.", "reponse": "avait fallu", "choix": "", "niveau": "avancé"},
]

# 🔁 Insertion dans la base
 for data in exercices:
        exercice = Exercice(**data)
        db.session.add(exercice)

db.session.commit()
print("✅ Exercices insérés avec succès.")