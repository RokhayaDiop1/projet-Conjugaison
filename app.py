from flask import Flask, render_template

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

@app.route('/conjugaison')
def conjugaison():
    return render_template('conjugaison.html')

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

if __name__ == '__main__':
    app.run(debug=True)
