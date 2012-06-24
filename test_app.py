# -*- encoding: utf-8 -*-
import unittest
from test_utils import prepare_db_for_tests, test_depute
from flask import url_for
from flask.testing import FlaskClient
from flask.ext.fillin import FormWrapper
from main import app
from database import Depute, create_user


class FlaskrTestCase(unittest.TestCase):
    def setUp(self):
        prepare_db_for_tests()
        self.app = FlaskClient(app, response_wrapper=FormWrapper)
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
        self.assertTrue("Login" in rv.data)
        self.assertTrue("Username" in rv.data)
        self.assertTrue("Password" in rv.data)

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
        self.assertTrue("Logout" in rv.data)


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
        self.assertTrue("This user doesn't exist or the password is false" in rv.data)

    def test_login_bad_password(self):
        rv = self.app.post(url_for("login"),
                           data={"username": "test", "password": "bad"},
                          follow_redirects=True)
        self.assertTrue("This user doesn't exist or the password is false" in rv.data)
