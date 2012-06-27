import re
import bcrypt
import unicodedata
from minimongo import Model, Index


class DuplicatedUser(Exception): pass


class User(Model):
    class Meta:
        database = "adopteundepute"

    def test_password(self, password):
        return bcrypt.hashpw(password, self.password) == self.password

    def is_active(self):
        return True

    def get_id(self):
        return self._id

    def is_anonymous(self):
        return False

    @property
    def follow_list(self):
        if self.get("follow_list", None) is None:
            self["follow_list"] = []
            self.save()
        return self["follow_list"]

    def follow(self, depute):
        if not isinstance(depute, Depute):
            raise ValueError
        self.follow_list.append(depute._id)
        self.save()

    def unfollow(self, depute):
        if not isinstance(depute, Depute):
            raise ValueError
        self.follow_list.remove(depute._id)
        self.save()

    def get_followed_deputies(self):
        return [Depute.collection.find_one({"_id": x}) for x in self.follow_list]

    def is_following(self, depute):
        return depute._id in self.follow_list


def create_user(username, password):
    if not username or not password:
        raise ValueError
    if User.collection.find_one({"username": username}):
        raise DuplicatedUser
    return User({"username": username, "password": bcrypt.hashpw(password, bcrypt.gensalt())}).save()


class Extra(Model):
    class Meta:
        database = "adopteundepute"


class Depute(Model):
    class Meta:
        database = "adopteundepute"

        indices = (
            Index("nom_de_famille"),
        )

    @property
    def for_memopol(self):
        return unicodedata.normalize('NFKD', u"%s%s" % (self["prenom"], self["nom_de_famille"])).encode('ascii', 'ignore')

    @property
    def an_id(self):
        return re.sub(".*/", "", self.url_an[:-4])

    @property
    def extra(self):
        in_db_extra = Extra.collection.find_one({"depute_id": self.an_id})
        if not in_db_extra:
            return Extra({"depute_id": self.an_id}).save()
        return in_db_extra
