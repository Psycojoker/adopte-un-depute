from flask import Flask, render_template, abort
from database import Depute
app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html", deputes=Depute.collection.find(sort=[("nom_de_famille",1)]))


@app.route("/depute/<depute>/")
def depute(depute):
    if not Depute.collection.find_one({"slug": depute}):
        abort(404)
    return render_template("depute.html", depute=Depute.collection.find_one({"slug": depute}))


if __name__ == "__main__":
    app.run(debug=True)
