# chatbot.py

conjugaisons = {
    "aller": {
        "je": "vais",
        "tu": "vas",
        "il": "va",
        "nous": "allons",
        "vous": "allez",
        "ils": "vont"
    },
    "manger": {
        "je": "mange",
        "tu": "manges",
        "il": "mange",
        "nous": "mangeons",
        "vous": "mangez",
        "ils": "mangent"
    },
    "être": {
        "je": "suis",
        "tu": "es",
        "il": "est",
        "nous": "sommes",
        "vous": "êtes",
        "ils": "sont"
    }
}

def conjuguer(verbe):
    verbe = verbe.lower()
    if verbe in conjugaisons:
        lignes = [f"{pronom} {forme}" for pronom, forme in conjugaisons[verbe].items()]
        return "\n".join(lignes)
    else:
        return f"Je ne connais pas encore la conjugaison du verbe '{verbe}'."
