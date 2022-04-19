from distutils import core
from pymongo import MongoClient
from datetime import datetime
import folium
import pandas as pd

db_uri = "mongodb+srv://etudiant:ur2@clusterm1.0rm7t.mongodb.net/"
client = MongoClient(db_uri)
db = client["doctolib"]
coll = db["dump_Jan2022"]
# print(coll.index_information())
lat = 48.117266
long = -1.6777926
chezMoi = {"type": "Point", "coordinates": [long, lat]}
date_deb = datetime.strptime("2022-01-26", "%Y-%m-%d")
date_fin = datetime.strptime("2022-01-29", "%Y-%m-%d")

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

m = folium.Map(location=[lat, long], zoom_start=10,
               tiles='Stamen Toner', control_scale=True)

for i in cursor:
    coord = i["_id"]["coord"]
    color = "red"
    if i["nb"] > 20:
        color='darkblue'
    folium.Marker([coord[1], coord[0]], popup = "",
                 icon = folium.Icon(color=color, icon='university', prefix='fa')).add_to(m)
outfp="base_map.html"
m.save(outfp)
# print(len(list(cursor))) --> 7


# générer une carte des centres de vaccination situés à moins de 50km de Rennes.
#  1)centres de vactination geo < 50km  rennes
#  2)nb de creneaux vaccin ouvert
# f 3)ilter periode 26 - 29 janvier inclu 2022
#  4)L’icône associée au nb de creneaux vaccin ouvert par centre de vaccination sera de couleur rouge, orange ou vert
