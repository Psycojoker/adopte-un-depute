import re
import unicodedata
from minimongo import Model, Index


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
