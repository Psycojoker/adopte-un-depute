from minimongo import Model, Index

class Depute(Model):
    class Meta:
        database = "adopteundepute"

        indices = (
            Index("nom_de_famille"),
        )
