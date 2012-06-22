import unittest
from json import loads
from pymongo import Connection
from pymongo.database import Database
from minimongo.collection import Collection

from database import Depute, Extra, create_user, User

test_depute = loads("""
{
        "id":63,
        "nom":"\u00c9ric Ciotti",
        "nom_de_famille":"Ciotti",
        "prenom":"\u00c9ric",
        "sexe":"H",
        "date_naissance":"1965-09-28",
        "lieu_naissance":"Nice (Alpes-Maritimes)",
        "num_deptmt":"06",
        "nom_circo":"Alpes-Maritimes",
        "num_circo":1,
        "mandat_debut":"2007-06-20",
        "groupe_sigle":"UMP",
        "sites_web":[{
            "site":"http:\/\/twitter.com\/ECiotti"
        }],
        "emails":[{
            "email":"e.ciotti@orange.fr"
        },
        {
            "email":"eciotti@assemblee-nationale.fr"
        }],
        "adresses":[{
            "adresse":"Assembl\u00e9e nationale 126 Rue de l'Universit\u00e9 75355 Paris 07 SP T\u00e9l\u00e9phone : 01 40 63 75 44 T\u00e9l\u00e9copie : 01 40 63 78 28"
        },
        {
            "adresse":"12 Avenue Georges Cl\u00e9menceau 06000 Nice T\u00e9l\u00e9phone : 04 93 85 22 26 T\u00e9l\u00e9copie : 04 93 85 20 79"
        }],
        "anciens_mandats":[{
            "mandat":"20\/06\/2007 \/  \/ \u00e9lections g\u00e9n\u00e9rales"
        }],
        "autres_mandats":[{
            "mandat":"Alpes-Maritimes \/ Conseil g\u00e9n\u00e9ral \/ Pr\u00e9sident"
        }],
        "anciens_autres_mandats":[{
            "mandat":"Nice (Alpes-Maritimes) \/ Conseil municipal \/ Premier Adjoint au Maire \/ 17\/03\/2008 \/ 18\/12\/2008"
        },
        {
            "mandat":"Alpes-Maritimes \/ Conseil g\u00e9n\u00e9ral \/ Membre \/ 07\/12\/2008 \/ 27\/03\/2011"
        },
        {
            "mandat":"Alpes-Maritimes \/ Conseil g\u00e9n\u00e9ral \/ Pr\u00e9sident \/ 18\/12\/2008 \/ 27\/03\/2011"
        }],
        "profession":"Directeur de cabinet d'un pr\u00e9sident de conseil g\u00e9n\u00e9ral",
        "place_en_hemicycle":"269",
        "url_an":"http:\/\/www.assembleenationale.fr\/13\/tribun\/fiches_id\/330240.asp",
        "slug":"eric-ciotti",
        "url_nosdeputes":"http:\/\/2007-2012.nosdeputes.fr\/eric-ciotti",
        "url_nosdeputes_api":"http:\/\/2007-2012.nosdeputes.fr\/eric-ciotti\/json",
        "nb_mandats":2
    }""")


class TestDatabase(unittest.TestCase):
    def setUp(self):
        # monkey patch collection to avoid using the prod database
        Depute.collection = Collection(Database(Connection('localhost', 27017), u'test_adopteundepute'), u'depute', document_class=Depute)
        Depute.database = Database(Connection('localhost', 27017), u'test_adopteundepute')
        Depute.collection.remove()
        self.assertEqual(Depute.collection.count(), 0)

        Extra.collection = Collection(Database(Connection('localhost', 27017), u'test_adopteundepute'), u'extra', document_class=Extra)
        Extra.database = Database(Connection('localhost', 27017), u'test_adopteundepute')
        Extra.collection.remove()
        self.assertEqual(Extra.collection.count(), 0)

        User.collection = Collection(Database(Connection('localhost', 27017), u'test_adopteundepute'), u'user', document_class=Extra)
        User.database = Database(Connection('localhost', 27017), u'test_adopteundepute')
        User.collection.remove()
        self.assertEqual(User.collection.count(), 0)

        self.depute = Depute(test_depute)
        self.depute = self.depute.save()

    def tearDown(self):
        Depute.collection.remove()
        Extra.collection.remove()

    def test_for_memopol(self):
        self.assertEqual(self.depute.for_memopol, u"EricCiotti")

    def test_an_id(self):
        self.assertEqual(self.depute.an_id, '330240')

    def test_get_extra(self):
        self.assertTrue(isinstance(self.depute.extra, Extra))

    def test_extra_saved(self):
        self.depute.extra
        self.assertEqual(Extra.collection.count(), 1)

    def test_extra_save_depute_id(self):
        self.assertEqual(self.depute.extra.depute_id, self.depute.an_id)

    def test_extra_the_same(self):
        extra = self.depute.extra
        self.assertEqual(extra, self.depute.extra)


class TestUSer(unittest.TestCase):
    def setUp(self):
        # monkey patch collection to avoid using the prod database
        Depute.collection = Collection(Database(Connection('localhost', 27017), u'test_adopteundepute'), u'depute', document_class=Depute)
        Depute.database = Database(Connection('localhost', 27017), u'test_adopteundepute')
        Depute.collection.remove()
        self.assertEqual(Depute.collection.count(), 0)

        Extra.collection = Collection(Database(Connection('localhost', 27017), u'test_adopteundepute'), u'extra', document_class=Extra)
        Extra.database = Database(Connection('localhost', 27017), u'test_adopteundepute')
        Extra.collection.remove()
        self.assertEqual(Extra.collection.count(), 0)

        User.collection = Collection(Database(Connection('localhost', 27017), u'test_adopteundepute'), u'user', document_class=Extra)
        User.database = Database(Connection('localhost', 27017), u'test_adopteundepute')
        User.collection.remove()
        self.assertEqual(User.collection.count(), 0)

        self.depute = Depute(test_depute)
        self.depute = self.depute.save()

    def test_create_user(self):
        self.assertTrue(isinstance(create_user("foo", "bar"), User))

    def test_create_user_save(self):
        create_user("foo", "bar")
        self.assertEqual(User.collection.find().count(), 1)

    def test_user_as_login(self):
        user = create_user(username="foo", password="bar")
        self.assertEqual(user.username, "foo")

    def test_login_non_empty(self):
        self.assertRaises(ValueError, create_user, "", "pouet")

    def test_password_non_empty(self):
        self.assertRaises(ValueError, create_user, "pouet", "")

    def test_dont_store_password_in_clear(self):
        user = create_user(username="foo", password="bar")
        self.assertNotEqual(user.password, "bar")

    def test_password_is_correct(self):
        user = create_user(username="foo", password="bar")
        self.assertTrue(user.is_password("bar"))

    def test_password_is_not_correct(self):
        user = create_user(username="foo", password="bar")
        self.assertFalse(user.is_password("bad password"))
