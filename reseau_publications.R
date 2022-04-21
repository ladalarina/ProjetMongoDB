library(mongolite)
library(dplyr)

url="mongodb://etudiant:ur2@clusterm1-shard-00-00.0rm7t.mongodb.net:27017,clusterm1-shard-00-01.0rm7t.mongodb.net:27017,clusterm1-shard-00-02.0rm7t.mongodb.net:27017/?ssl=true&replicaSet=atlas-l4xi61-shard-0"

mdb = mongo(collection="hal_irisa_2021", db="publications",
            url=url,
            verbose=TRUE)

# R?cup?ration des 20 auteurs ayant ?crit le plus d'articles et cr?ation d'un df
req='[
  {"$unwind" : "$authors"}, 
  {"$group" : {"_id" : "$authors", "nb" : {"$sum" : 1}}}, 
  {"$sort": {"nb" : -1}}, 
  {"$limit" : 20}
]'

auteurs <- mdb$aggregate(pipeline=req)

auteurs <- as.data.frame(auteurs)
auteurs <- data.frame(
  nom = auteurs$"_id"$name, 
  prenom = auteurs$"_id"$firstname, 
  nb_articles = auteurs$nb
)

# R?cup?ration de la liste des articles pour chaque auteur 
q <-'{"authors" : {"$elemMatch" : {"name" : "Lef?vre","firstname" : "S?bastien" }}}'
article <- as.data.frame(mdb$find(q))

liste_noms = c()
liste_prenoms = c()
liste_articles = c()
liste_nb = c()
for (i in 1:nrow(auteurs)){
  articles = c()
  q <-paste0('{"authors" : {"$elemMatch" : {"name" : "',auteurs$nom[i], '","firstname" : "', auteurs$prenom[i],'" }}}')
  article <- as.data.frame(mdb$find(q))
  for (a in article$title){
    articles = c(articles, a)  
  }
  liste_noms = c(liste_noms,auteurs$nom[i])
  liste_prenoms = c(liste_prenoms,auteurs$prenom[i])
  liste_articles = c(liste_articles,as.character(list(articles)))
  liste_nb = c(liste_nb, auteurs$nb_articles[i])
  
}

auteurs_articles = tibble(
  nom = liste_noms, 
  prenom = liste_prenoms, 
  articles = liste_articles,
  nb_articles = liste_nb
)
auteurs_articles = as.data.frame(auteurs_articles)
#write.csv(auteurs_articles, "chemin/auteurs_articles.csv")

