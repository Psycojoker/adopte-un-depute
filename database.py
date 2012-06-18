import unicodedata
from minimongo import Model, Index

class Depute(Model):
    class Meta:
        database = "adopteundepute"

        indices = (
            Index("nom_de_famille"),
        )

    @property
    def for_memopol(self):
        return unicodedata.normalize('NFKD', u"%s%s" % (self["prenom"], self["nom_de_famille"])).encode('ascii', 'ignore')
