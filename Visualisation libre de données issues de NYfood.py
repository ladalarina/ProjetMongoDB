from pymongo import MongoClient
from pandas import *
from bokeh.tile_providers import  get_provider, Vendors
from bokeh.models import HoverTool, ColumnDataSource, ColorPicker, Legend
from bokeh.plotting import figure, output_file, show, ColumnDataSource
import numpy as np


# connection a au serveur et à la bd
db_uri = "mongodb+srv://etudiant:ur2@clusterm1.0rm7t.mongodb.net/"
client = MongoClient(db_uri)
db = client["food"]
coll = db["NYfood"]
# print(coll.index_information())

# Première idée : histogramme des quartiers renseignant sur la proportion du type de cuisine

# Seconde idée : carte des restaurants avec code couleur selon la note moyenne et affichage du type de cuisine au survol
##Le nombre de restaurants étant élevé, on se limitera à 100 restaurants tirés au hasard ayant un grade de A
## J'ai voulu prendre les 100 premiers restaurants rangés par ordre décroissant de la note moyenne mais ils étaient quasiment tous avec une note moyenne de 13 donc peu pertinent à visualiser
cursor = coll.aggregate([
    {"$unwind": "$grades"},
    {"$group":
         {"_id": {"name" : "$name",
                "coord" : "$address.loc.coordinates",
                "grade": "$grades.grade",
                "note" : "$grades.score",
                "quartier" : "$borough"}}
    }, 
    {"$match" : {"_id.grade" : "A"}},
    {"$group": {"_id": {"name" : "$_id.name",
                    "coord" : "$_id.coord",
                    "quartier" : "$_id.quartier"},
              "note_moy": {"$avg": "$_id.note"},
             }
    },
    {"$limit" : 100}
])

data = list(cursor)
## Création d'un dictionnaire propre
new_data = {"nom" : [], "coord": [], "note_moy": [], "quartier" : []}
for i in range(len(data)) :
    new_data['note_moy'].append(data[i]['note_moy'])
    new_data['nom'].append(data[i]['_id']['name'])
    new_data['coord'].append(data[i]['_id']['coord'])
    new_data['quartier'].append(data[i]['_id']['quartier'])

## Ajout dans un dataframe
resto = DataFrame(columns = ["nom", "coord", "note_moy", "quartier"])
for key, val in new_data.items() :
    resto[key] = val

## Séparation coordonnées :
pointsX = []
pointsY = []
k = 6378137
for (x,y) in resto['coord'] :
    pointsX.append(float(x) * (k * np.pi/180.0))
    pointsY.append(np.log(np.tan((90 + float(y)) * np.pi/360.0)) * k)
resto['pointsX'] = pointsX
resto['pointsY'] = pointsY

##Taille points
taille_points = resto.iloc[:,2].apply(lambda x: x*1.3)
resto["taille_points"] = taille_points

## Couleur différente selon le quartier
quartiers= []
for q in resto["quartier"] :
    if q not in quartiers:
        quartiers.append(q)
Q1 = resto[resto["quartier"]==quartiers[0]]
Q2 = resto[resto["quartier"]==quartiers[1]]
Q3 = resto[resto["quartier"]==quartiers[2]]
Q4 = resto[resto["quartier"]==quartiers[3]]

## Création graphe :
Q1 = ColumnDataSource(Q1)
Q2 = ColumnDataSource(Q2)
Q3 = ColumnDataSource(Q3)
Q4 = ColumnDataSource(Q4)

p1 = figure(x_axis_type="mercator", y_axis_type="mercator", active_scroll="wheel_zoom",
            title="Restaurants de New York", plot_width=1400,plot_height=600)
tile_provider = get_provider(Vendors.CARTODBPOSITRON)
p1.add_tile(tile_provider)
q1 = p1.circle(x='pointsX', y='pointsY', size='taille_points', fill_alpha=0.5, source=Q1, fill_color='blue')
q2 = p1.circle(x='pointsX', y='pointsY', size='taille_points', fill_alpha=0.5, source=Q2, fill_color='turquoise')
q3 = p1.circle(x='pointsX', y='pointsY', size='taille_points', fill_alpha=0.5, source=Q3, fill_color='violet')
q4 = p1.circle(x='pointsX', y='pointsY', size='taille_points', fill_alpha=0.5, source=Q4, fill_color='steelblue')

# Ajout d'un widget au survol des points
hover_tool = HoverTool(tooltips=[('Nom', '@nom'),('Quartier', '@quartier'),('Note moyenne', '@note_moy')])
p1.add_tools(hover_tool)

#La légende
legend = Legend(items=[(quartiers[0], [q1]),
                       (quartiers[1], [q2]),
                       (quartiers[2], [q3]),
                       (quartiers[3], [q4]),], location = 'top')
p1.add_layout(legend,'left')

legend.click_policy="hide"
legend.title = "Cliquer sur les quartiers à afficher"
show(p1)
output_file("docs/NYfood_map.html")





















