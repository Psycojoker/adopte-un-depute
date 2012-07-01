import unittest

from test_utils import prepare_db_for_tests, test_depute
from database import Depute, Extra, create_user, User, DuplicatedUser


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
        self.assertEqual(self.depute.extra.depute_id, self.depute._id)

    def test_extra_the_same(self):
        extra = self.depute.extra
        self.assertEqual(extra, self.depute.extra)

    def test_extra_get_depute(self):
        self.assertEqual(self.depute, self.depute.extra.depute)


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
        self.assertTrue(user.test_password("bar"))

    def test_password_is_not_correct(self):
        user = create_user(username="foo", password="bar")
        self.assertFalse(user.test_password("bad password"))

    def test_duplicated_users(self):
        create_user(username="foo", password="bar")
        self.assertRaises(DuplicatedUser, create_user, username="foo", password="bar")


class TestUserFollow(unittest.TestCase):
    def setUp(self):
        prepare_db_for_tests()
        self.user = create_user("pouet", "pouet")
        self.depute = Depute(test_depute).save()

    def test_user_follow_list(self):
        self.assertEqual([], self.user.follow_list)

    def test_user_follow_raise_value_error(self):
        """should only work with a Depute  args"""
        self.assertRaises(ValueError, self.user.follow, None)

    def test_user_follow_depute(self):
        self.user.follow(self.depute)
        self.assertEqual(len(self.user.follow_list), 1)
        self.assertEqual(self.user.follow_list[0], self.depute._id)

    def test_user_follow_list_is_save(self):
        self.user.follow(self.depute)
        in_db_user = User.collection.find_one({"_id": self.user._id})
        self.assertEqual(len(in_db_user.follow_list), 1)
        self.assertEqual(in_db_user.follow_list[0], self.depute._id)

    def test_user_unfollow_raise_value_error(self):
        self.assertRaises(ValueError, self.user.unfollow, None)

    def test_user_unfollow_depute(self):
        self.user.follow(self.depute)
        self.assertEqual(len(self.user.follow_list), 1)
        self.assertEqual(self.user.follow_list[0], self.depute._id)
        self.user.unfollow(self.depute)
        self.assertEqual(len(self.user.follow_list), 0)
        self.assertTrue(self.depute._id not in self.user.follow_list)

    def test_user_unfollow_list_is_save(self):
        self.user.follow(self.depute)
        in_db_user = User.collection.find_one({"_id": self.user._id})
        self.assertEqual(len(in_db_user.follow_list), 1)
        self.assertEqual(in_db_user.follow_list[0], self.depute._id)
        self.user.unfollow(self.depute)
        in_db_user = User.collection.find_one({"_id": self.user._id})
        self.assertEqual(len(in_db_user.follow_list), 0)
        self.assertTrue(self.depute._id not in in_db_user.follow_list)

    def test_get_followed_deputies(self):
        self.assertEqual(self.user.get_followed_deputies(), [])
        self.user.follow(self.depute)
        self.assertEqual(self.user.get_followed_deputies()[0], self.depute)

    def test_is_following(self):
        self.assertFalse(self.user.is_following(self.depute))
        self.user.follow(self.depute)
        self.assertTrue(self.user.is_following(self.depute))

    def test_deputy_empty_followers(self):
        self.assertEqual(self.depute.extra.followers, [])

    def test_deputy_one_follower(self):
        self.user.follow(self.depute)
        self.assertEqual(self.depute.extra.followers, [self.user])
