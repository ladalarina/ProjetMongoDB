import pandas
from pymongo import MongoClient
import pandas as pd
db_uri = "mongodb+srv://etudiant:ur2@clusterm1.0rm7t.mongodb.net/"
client = MongoClient(db_uri)
db = client["doctolib"]
coll = db["dump_Jan2022"]
print(coll.index_information())

# générer une carte des centres de vaccination situés à moins de 50km de Rennes.
#  1)centres de vactination geo < 50km  rennes
#  2)nb de creneaux vaccin ouvert
#f 3)ilter periode 26 - 29 janvier inclu 2022
#  4)L’icône associée au nb de creneaux vaccin ouvert par centre de vaccination sera de couleur rouge, orange ou vert 
