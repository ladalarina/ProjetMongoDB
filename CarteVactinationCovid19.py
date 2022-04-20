"""System module."""
from distutils import core
from pymongo import MongoClient
from datetime import datetime
import folium
from branca.element import Template, MacroElement
from math import *

from sympy import li

# connection a au serveur et à la bd
db_uri = "mongodb+srv://etudiant:ur2@clusterm1.0rm7t.mongodb.net/"
client = MongoClient(db_uri)
db = client["doctolib"]
coll = db["dump_Jan2022"]
# print(coll.index_information())

# definition des variables
lat = 48.117266
long = -1.6777926
chezMoi = {"type": "Point", "coordinates": [long, lat]}
date_deb = datetime.strptime("2022-01-26", "%Y-%m-%d")
date_fin = datetime.strptime("2022-01-29", "%Y-%m-%d")
# requete agregate
cursor = coll.aggregate(
    [
        {
            "$geoNear": {
                "distanceField": "distance",
                "maxDistance": 50000,
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
# --> 7
# creation de la carte

m = folium.Map(location=[lat, long], zoom_start=9,
               tiles='Stamen Toner', control_scale=True)

res = list(cursor)
nb_creneaux = []
for i in res:
    nb_creneaux.append(i["nb"])
max = max(nb_creneaux)
tertile = floor(max/3)
tertile2 = tertile * 2
for i in res:
    coord = i["_id"]["coord"]
    if i["nb"] <= tertile:
        color = 'red'
    elif i["nb"] <= 2*tertile:
        color = 'orange'
    else:
        color = 'green'
    folium.Marker([coord[1], coord[0]], popup=i["_id"]["nom"] + "\n Nombre de places: "+str(i["nb"]),
                  icon=folium.Icon(color=color, icon='medkit', prefix='fa')).add_to(m)
outfp = "docs/base_map.html"
# légende
template = """
{% macro html(this, kwargs) %}
<div
    style='position: absolute; z-index:9999; border:2px solid grey; background-color:rgba(255, 255, 255, 0.8);
     border-radius:6px; padding: 10px; font-size:14px; right: 20px; bottom: 20px;'>
<div class='legend-scale'>
  <ul class='legend-labels'>
    <li>
        <div style="padding: 10px; color: white; width: 35px;height: 35px; background-color: green;">
            <i class="fa-rotate-0 fa fa-medkit"></i>
        </div>
        Entre """ + str(tertile2) + """ et """ + str(max) + """</li>
    <li>
        <div style="padding: 10px; color: white; width: 35px;height: 35px; background-color: orange;">
            <i class="fa-rotate-0 fa fa-medkit"></i>
        </div>
        Entre """ + str(tertile) + """ et """ + str(tertile2) + """</li>
    <li>
        <div style="padding: 10px; color: white; width: 35px;height: 35px; background-color: red;">
            <i class="fa-rotate-0 fa fa-medkit"></i>
        </div>
        Entre 0 et """ + str(tertile) + """</li>
  </ul>
</div>
</div>
{% endmacro %}"""

macro = MacroElement()
macro._template = Template(template)
m.get_root().add_child(macro)
m.save(outfp)


# Visualisation 2

date_deb1 = datetime.strptime("2022-01-01", "%Y-%m-%d")
date_fin1 = datetime.strptime("2022-06-01", "%Y-%m-%d")
# requete agregate
# db.users.findOne({"username" : {$regex : "son"}});
cursor1 = coll.aggregate(
    [

        {"$unwind": "$visit_motives"},
        {"$unwind": "$visit_motives.name"},
        {"$unwind": "$visit_motives.slots"},
        {"$match":
            {
                "visit_motives.slots": {
                    "$gte": date_deb1,
                    "$lte": date_fin1
                },
                "visit_motives.name": {
                    "$regex": "1re injection"
                }
            }
         },
        {
            "$group": {
                "_id": {
                    "nom": "$name",
                    "coord": "$location.coordinates",
                    "url": "$url_doctolib",
                    "visit_motives" :  "$visit_motives.name" ,
                },
                
                "nb": {"$sum": 1}
                
            }
        }
    ]
)
#print(len(list(cursor1)))

## carte 2
m1 = folium.Map(location=[lat, long], zoom_start=9,
               tiles='Stamen Toner', control_scale=True)

res1 = list(cursor1)

libelles = []
for i in res1:
    libelles.append(i["_id"]["visit_motives"])
unique_libelle = list(set(libelles))
colors = [
    "green",
    "blue",
    "purple",
    "yellow",
    "red",
    "pink"
]
for i in res1:
    coord = i["_id"]["coord"]
    injection = i["_id"]["visit_motives"]
    print(injection)
    color = colors[unique_libelle.index(injection) % (len(color) - 1)]
    folium.Marker([coord[1], coord[0]], popup=i["_id"]["nom"] + i["_id"]["visit_motives"],
        icon=folium.Icon(color=color, icon='medkit', prefix='fa')).add_to(m1)

lis = []
for lib in unique_libelle:
    lis.append("<li><div style=\"width: 25px; height: 25px; background-color: " + colors[unique_libelle.index(lib) % (len(color) - 1)] + " \"></div>" + lib + "</li>")
template1 = """
{% macro html(this, kwargs) %}
<div id="lada"
    style='position: absolute; z-index:9999; border:2px solid grey; background-color:rgba(255, 255, 255, 0.8);
     border-radius:6px; padding: 10px; font-size:14px; right: 20px; bottom: 20px;'>
    <div class='legend-scale'>
    <ul class='legend-labels'>
        """ + "".join(lis) + """
    </ul>
    </div>
</div>
{% endmacro %}"""

outfp = "docs/base_map1.html"
macro = MacroElement()
macro._template = Template(template1)
m1.get_root().add_child(macro)
m1.save(outfp)