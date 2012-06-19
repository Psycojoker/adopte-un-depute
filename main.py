from flask import Flask, render_template
from database import Depute
from shortcuts import get_object_or_404
app = Flask(__name__)


@app.route("/")
def home():
    deputes_by_letter = {}
    for depute in Depute.collection.find(sort=[("nom_de_famille",1)]):
        if not deputes_by_letter.get(depute["nom_de_famille"][0]):
            deputes_by_letter[depute["nom_de_famille"][0]] = []
        deputes_by_letter[depute["nom_de_famille"][0]].append(depute)
    return render_template("home.html", deputes_by_letter=deputes_by_letter, letters=sorted(deputes_by_letter.keys())[1:])


@app.route("/depute/<depute>/")
def depute(depute):
    return render_template("depute.html", depute=get_object_or_404(Depute, {"slug": depute}))


if __name__ == "__main__":
    app.run(debug=True)
