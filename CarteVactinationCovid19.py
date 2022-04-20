"""System module."""
from distutils import core
from pymongo import MongoClient
from datetime import datetime
import folium
import pandas as pd

### connection a au serveur et à la bd
db_uri = "mongodb+srv://etudiant:ur2@clusterm1.0rm7t.mongodb.net/"
client = MongoClient(db_uri)
db = client["doctolib"]
coll = db["dump_Jan2022"]
# print(coll.index_information())

##definition des variables
lat = 48.117266
long = -1.6777926
chezMoi = {"type": "Point", "coordinates": [long, lat]}
date_deb = datetime.strptime("2022-01-26", "%Y-%m-%d")
date_fin = datetime.strptime("2022-01-29", "%Y-%m-%d")
#requete agregate
cursor = coll.aggregate(
    [
        {
            "$geoNear": {
                "distanceField": "distance",
                "maxDistance":50000,
                "near": chezMoi
            }
        },
        {"$unwind": "$visit_motives"},
        {"$unwind": "$visit_motives.slots"},
        {"$match":
            {
                "visit_motives.slots": {
                    "$gte": date_deb,
                    "$lte": date_fin
                }
            }
         },
        {
            "$group": {
                "_id": {
                    "nom": "$name",
                    "coord": "$location.coordinates",
                    "url": "$url_doctolib"
                },
                "nb": {"$sum": 1}
            }
         }
    ]
)
# print(len(list(cursor))) 
##--> 7
#creation de la carte

m = folium.Map(location=[lat, long], zoom_start=9,
               tiles='Stamen Toner', control_scale=True)

res = list(cursor)
nb_creneaux = []
for i in res:
    nb_creneaux.append(i["nb"])
tertile = max(nb_creneaux)/3
for i in res:
    coord = i["_id"]["coord"]
    if i["nb"] <= tertile:
        color='red'
    elif i["nb"] <= 2*tertile:
        color='orange'
    else:
        color='green'
    folium.Marker([coord[1], coord[0]], popup = i["_id"]["nom"]+ "\n Nombre de places: "+str(i["nb"]),
                 icon = folium.Icon(color=color, icon='medkit', prefix='fa')).add_to(m)
outfp="docs/base_map.html"
m.save(outfp)


