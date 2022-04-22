from pymongo import MongoClient

# connection a au serveur et à la bd
db_uri = "mongodb+srv://etudiant:ur2@clusterm1.0rm7t.mongodb.net/"
client = MongoClient(db_uri)
db = client["food"]
coll = db["NYfood"]
# print(coll.index_information())

# Première idée : histogramme des quartiers renseignant sur la proportion du type de cuisine
