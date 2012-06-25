# -*- encoding: utf-8 -*-
import unittest
from test_utils import prepare_db_for_tests, test_depute
from flask import url_for
from database import User
from flask.testing import FlaskClient
from flask.ext.fillin import FormWrapper
from main import app
from database import Depute, create_user


class AuDTestCase(unittest.TestCase):
    def setUp(self):
        prepare_db_for_tests()
        self.app = FlaskClient(app, response_wrapper=FormWrapper)
        self.app.application.config["CSRF_ENABLED"] = False
        self.depute = Depute(test_depute).save()
        create_user("test", "test")
        self.ctx = app.test_request_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def test_empty_home(self):
        Depute.collection.remove()
        rv = self.app.get(url_for("home"))
        self.assertTrue("Éric Ciotti" not in rv.data)

    def test_deputy_on_home(self):
        rv = self.app.get(url_for("home"))
        self.assertTrue("Éric Ciotti" in rv.data)

    def test_deputy_personnal_page(self):
        rv = self.app.get(url_for("depute", depute=self.depute.slug))
        self.assertTrue("Éric Ciotti" in rv.data)

    def test_link_to_nosdeputes_fr(self):
        rv = self.app.get(url_for("depute", depute=self.depute.slug))
        self.assertTrue("http://www.nosdeputes.fr/eric-ciotti" in rv.data)

    def test_link_to_memopol(self):
        rv = self.app.get(url_for("depute", depute=self.depute.slug))
        self.assertTrue('https://memopol.lqdn.fr/france/assemblee/depute/EricCiotti/' in rv.data)

    def test_link_to_an(self):
        rv = self.app.get(url_for("depute", depute=self.depute.slug))
        self.assertTrue("http://www.assembleenationale.fr/13/tribun/fiches_id/330240.asp" in rv.data)

    def test_display_group(self):
        rv = self.app.get(url_for("depute", depute=self.depute.slug))
        self.assertTrue(self.depute.groupe_sigle.encode("Utf-8") in rv.data)

    def test_login_on_home(self):
        rv = self.app.get(url_for("home"))
        self.assertTrue(url_for("login") in rv.data)

    def test_login_page(self):
        rv = self.app.get(url_for("login"))
        self.assertTrue("Se connecter" in rv.data)
        self.assertTrue("Login" in rv.data)
        self.assertTrue("Mot de passe" in rv.data)

    def test_login_form(self):
        rv = self.app.get(url_for("login"))
        rv.form.fields["username"] = "test"
        rv.form.fields["password"] = "test"
        rv = rv.form.submit(self.app)
        self.assertEqual(rv.status_code, 302)

    def test_login_success(self):
        rv = self.app.post(url_for("login"),
                           data={"username": "test", "password": "test"},
                           follow_redirects=True)
        self.assertTrue("Login success!" in rv.data)
        self.assertTrue("Se déconnecter" in rv.data)


    def test_logout(self):
        rv = self.app.post(url_for("login"),
                           data={"username": "test", "password": "test"},
                           follow_redirects=True)
        self.app.get(url_for("logout"))
        self.assertTrue("Login" in rv.data)

    def test_login_bad_login(self):
        rv = self.app.post(url_for("login"),
                           data={"username": "bad", "password": "test"},
                           follow_redirects=True)
        self.assertTrue("This user doesn't exist or the password is wrong" in rv.data)

    def test_login_bad_password(self):
        rv = self.app.post(url_for("login"),
                           data={"username": "test", "password": "bad"},
                           follow_redirects=True)
        self.assertTrue("This user doesn't exist or the password is wrong" in rv.data)

    def test_register_on_home(self):
        rv = self.app.get(url_for("home"))
        self.assertTrue(url_for("register") in rv.data)

    def test_register_page(self):
        rv = self.app.get(url_for("register"))
        self.assertTrue("Username" in rv.data)
        self.assertTrue("Password" in rv.data)
        self.assertTrue("Confirm password" in rv.data)

    def test_register_form(self):
        rv = self.app.get(url_for("register"))
        rv.form.fields["username"] = "toto"
        rv.form.fields["password"] = "test"
        rv.form.fields["confirm_password"] = "test"
        rv = rv.form.submit(self.app)
        self.assertEqual(rv.status_code, 302)

    def test_register_create_user(self):
        before = User.collection.count()
        self.app.post(url_for('register'),
                      data={"username": "pouet", "password": "pouet", "confirm_password": "pouet"},
                      follow_redirects=True)
        self.assertEqual(before + 1, User.collection.count())
        user = User.collection.find_one({"username": "pouet"})
        self.assertFalse(user is None)
        self.assertTrue(user.test_password("pouet"))

    def test_empty_fields(self):
        rv = self.app.post(url_for('register'),
                      data={"username": "", "password": "", "confirm_password": ""},
                      follow_redirects=True)
        self.assertTrue("This field is required" in rv.data)

    def test_duplicated_user(self):
        rv = self.app.post(url_for('register'),
                      data={"username": "test", "password": "test", "confirm_password": "test"},
                      follow_redirects=True)
        self.assertTrue("Ce pseudonyme est déjà pris." in rv.data)

    def test_password_doesnt_match(self):
        rv = self.app.post(url_for('register'),
                      data={"username": "pouet", "password": "test", "confirm_password": "bad"},
                      follow_redirects=True)
        self.assertTrue("Les mots de passe ne correspondent pas." in rv.data)

    def test_register_login(self):
        rv = self.app.post(url_for('register'),
                      data={"username": "pouet", "password": "test", "confirm_password": "test"},
                      follow_redirects=True)
        self.assertTrue("Votre compte a correctement été créé." in rv.data)
        self.assertTrue(url_for("logout") in rv.data)
