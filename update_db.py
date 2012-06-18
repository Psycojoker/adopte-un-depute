from json import load
from urllib import urlopen
from database import Depute

if __name__ == '__main__':
    for depute in load(urlopen("http://www.nosdeputes.fr/deputes/enmandat/json"))["deputes"]:
        dep = depute["depute"]
        if not Depute.collection.find_one({"id": dep["id"]}):
            print "add new dep:", dep["nom"]
            Depute(dep).save()
