from flask import Flask, render_template
from database import Depute
from shortcuts import get_object_or_404
from feedparser import parse
from urllib import quote_plus
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


@app.route("/depute/gnews/<depute>/")
def google_news(depute):
    depute = get_object_or_404(Depute, {"slug": depute})
    quoted_query = quote_plus("%s %s" % (depute["prenom"].encode("Utf-8"), depute["nom_de_famille"].encode("Utf-8")))
    print "http://www.google.fr/#hl=fr&q=%s&oq=%s" % (quoted_query, quoted_query)
    return render_template("rss_to_html.html", entries=parse("http://news.google.fr/news?q=%s&hl=fr&ie=UTF-8&output=rss" % quoted_query).entries[:10])

if __name__ == "__main__":
    app.run(debug=True)
