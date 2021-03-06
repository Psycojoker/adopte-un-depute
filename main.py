# -*- encoding: utf-8 -*-
from urllib import quote_plus
from flask import Flask, render_template, flash, url_for, redirect
from flask.ext.login import LoginManager, login_user, logout_user, current_user
from database import Depute, create_user
from shortcuts import get_object_or_404
from utils import prepare_rss
from database import User
from werkzeug import ImmutableDict
from flask.ext.wtf import Form, TextField, Required, BooleanField, PasswordField


class FlaskWithHamlish(Flask):
    jinja_options = ImmutableDict(
        extensions=['jinja2.ext.autoescape', 'jinja2.ext.with_', 'hamlish_jinja.HamlishExtension']
    )


app = FlaskWithHamlish(__name__)
app.jinja_options.hamlish_mode = "indented"
app.jinja_options.hamlish_enable_div_shortcut = True

app.secret_key = "devel secret key, CHANGE IT!!!"

login_manager = LoginManager()
login_manager.setup_app(app)


@app.template_filter('ipdb')
def ipdb(element):
    from ipdb import set_trace; set_trace()
    return element


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


@app.route("/adopter/<depute>/")
def adopter(depute):
    if current_user.is_anonymous():
        return redirect(url_for('login'))
    current_user.follow(Depute.collection.find_one({'slug': depute}))
    return redirect(url_for('depute', depute=depute))

@login_manager.user_loader
def load_user(userid):
    return User.collection.find_one({"_id": userid})


class LoginForm(Form):
    username = TextField("login", validators=[Required()])
    password = PasswordField("password", validators=[Required()])
    rememberme = BooleanField("rememberme")


@app.route("/login/", methods=["POST", "GET"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.collection.find_one({"username": form.username.data})

        if user is None or not user.test_password(form.password.data):
            flash("This user doesn't exist or the password is wrong", "error")
            return render_template("login.haml", form=form)

        login_user(user, remember=form.rememberme.data)
        flash("Login success!", "success")
        return redirect(url_for("home"))

    return render_template("login.haml", form=form)


@app.route("/logout/")
def logout():
    logout_user()
    return redirect(url_for("home"))


class RegisterForm(Form):
    username = TextField("login", validators=[Required()])
    password = PasswordField("password", validators=[Required()])
    confirm_password = PasswordField("confirm_password", validators=[Required()])


@app.route("/register/", methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.collection.find_one({"username": form.username.data}):
            form.username.errors.append(u"Ce pseudonyme est déjà pris.")
            return render_template("register.haml", form=form)

        if form.password.data != form.confirm_password.data:
            form.confirm_password.errors.append(u"Les mots de passe ne correspondent pas.")
            return render_template("register.haml", form=form)

        user = create_user(form.username.data, form.password.data)
        login_user(user)
        flash(u"Votre compte a correctement été créé.", "success")
        return redirect(url_for("home"))
    return render_template("register.haml", form=form)


if __name__ == "__main__":
    app.run(debug=True)
