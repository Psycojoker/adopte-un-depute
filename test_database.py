import unittest

from test_utils import prepare_db_for_tests, test_depute
from database import Depute, Extra, create_user, User


class TestDatabase(unittest.TestCase):
    def setUp(self):
        prepare_db_for_tests()

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
        prepare_db_for_tests()

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
