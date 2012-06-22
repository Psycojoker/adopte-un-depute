# -*- encoding: utf-8 -*-
import unittest
from test_utils import prepare_db_for_tests, test_depute
from main import app
from database import Depute


class FlaskrTestCase(unittest.TestCase):
    def setUp(self):
        prepare_db_for_tests()
        self.app = app.test_client()
        self.depute = Depute(test_depute).save()

    def test_empty_home(self):
        Depute.collection.remove()
        rv = self.app.get("/")
        self.assertTrue("Éric Ciotti" not in rv.data)

    def test_deputy_on_home(self):
        rv = self.app.get("/")
        self.assertTrue("Éric Ciotti" in rv.data)

    def test_deputy_personnal_page(self):
        rv = self.app.get("/depute/%s/" % self.depute.slug)
        self.assertTrue("Éric Ciotti" in rv.data)

    def test_link_to_nosdeputes_fr(self):
        rv = self.app.get("/depute/%s/" % self.depute.slug)
        self.assertTrue("http://www.nosdeputes.fr/eric-ciotti" in rv.data)

    def test_link_to_memopol(self):
        rv = self.app.get("/depute/%s/" % self.depute.slug)
        self.assertTrue('https://memopol.lqdn.fr/france/assemblee/depute/EricCiotti/' in rv.data)

    def test_link_to_an(self):
        rv = self.app.get("/depute/%s/" % self.depute.slug)
        self.assertTrue("http://www.assembleenationale.fr/13/tribun/fiches_id/330240.asp" in rv.data)

    def test_display_group(self):
        rv = self.app.get("/depute/%s/" % self.depute.slug)
        self.assertTrue(self.depute.groupe_sigle.encode("Utf-8") in rv.data)
