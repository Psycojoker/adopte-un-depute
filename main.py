from flask import Flask, render_template
from database import Depute
from shortcuts import get_object_or_404
from utils import prepare_rss
from urllib import quote_plus
from werkzeug import ImmutableDict


class FlaskWithHamlish(Flask):
    jinja_options = ImmutableDict(
        extensions=['jinja2.ext.autoescape', 'jinja2.ext.with_', 'hamlish_jinja.HamlishExtension']
    )


app = FlaskWithHamlish(__name__)
app.jinja_options.hamlish_mode = "indented"


@app.route("/")
def home():
    deputes_by_letter = {}
    for depute in Depute.collection.find(sort=[("nom_de_famille",1)]):
        if not deputes_by_letter.get(depute["nom_de_famille"][0]):
            deputes_by_letter[depute["nom_de_famille"][0]] = []
        deputes_by_letter[depute["nom_de_famille"][0]].append(depute)
    return render_template("home.haml", deputes_by_letter=deputes_by_letter, letters=sorted(deputes_by_letter.keys())[1:])


@app.route("/depute/<depute>/")
def depute(depute):
    return render_template("depute.haml", depute=get_object_or_404(Depute, {"slug": depute}))


@app.route("/depute/gnews/<depute>/")
def google_news(depute):
    depute = get_object_or_404(Depute, {"slug": depute})
    quoted_query = quote_plus("%s %s" % (depute["prenom"].encode("Utf-8"), depute["nom_de_famille"].encode("Utf-8")))
    return render_template("rss_to_html.haml", entries=prepare_rss("http://news.google.fr/news?q=%s&hl=fr&ie=UTF-8&output=rss" % quoted_query))

@app.route("/depute/nosdeputes_rss/<depute>/")
def nosdeputes_rss(depute):
    depute = get_object_or_404(Depute, {"slug": depute})
    return render_template("rss_to_html.haml", entries=prepare_rss("http://www.nosdeputes.fr/%s/rss" % depute["slug"]))


if __name__ == "__main__":
    app.run(debug=True)
