library(mongolite)
library(dplyr)
library(visNetwork)

# Connexion a la BDD
url="mongodb://etudiant:ur2@clusterm1-shard-00-00.0rm7t.mongodb.net:27017,clusterm1-shard-00-01.0rm7t.mongodb.net:27017,clusterm1-shard-00-02.0rm7t.mongodb.net:27017/?ssl=true&replicaSet=atlas-l4xi61-shard-0"

mdb = mongo(collection="hal_irisa_2021", db="publications",
            url=url,
            verbose=TRUE)

# Recuperation des 20 auteurs ayant ecrit le plus d'articles
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

# Création d'un df avec une ligne pour un article écrit

auteurs_articles <-  data.frame(matrix(vector(), 0, 3, dimnames=list(c(), c("nom_prenom","nb_articles","article"))),stringsAsFactors=F)

for (i in 1:nrow(auteurs)){
  q <-paste0('{"authors" : {"$elemMatch" : {"name" : "',auteurs$nom[i], '","firstname" : "', auteurs$prenom[i],'" }}}')
  article <- as.data.frame(mdb$find(q))
  for (a in article$title){
    ligne <- c(paste(auteurs$nom[i],auteurs$prenom[i]," "),auteurs$nb_articles[i], a )
    auteurs_articles <- rbind(auteurs_articles, ligne)
  }
}
colnames(auteurs_articles) <- c("nom_prenom", "nb_articles", "titre_article")

# Creation d'un graphe social

## Creation d'une table regroupant les liens sociaux
liens_auteurs <-  data.frame(matrix(vector(), 0, 4, dimnames=list(c(), c("nom_prenom1","nom_prenom2","article", "nb_articles"))),stringsAsFactors=F)

for (i in 1:nrow(auteurs_articles)){
  for (j in 1:nrow(auteurs_articles)){
    if (auteurs_articles[i,3]==auteurs_articles[j,3]){
      if (auteurs_articles[i,1]!=auteurs_articles[j,1]){
        ligne <- c(auteurs_articles[i,1],auteurs_articles[j,1], auteurs_articles[j,3],as.numeric(auteurs_articles[j,2]))
        liens_auteurs <- rbind(liens_auteurs, ligne)
      }
    }
  }
}
colnames(liens_auteurs) <- c("nom_prenom1","nom_prenom2","article", "nb_articles")
# BONUS : Calcul du nombre d'articles en commun 
nb_article_commun <- data.frame(matrix(vector(), 0, 3, dimnames=list(c(), c("nom_prenom1","nom_prenom2","nb_article_commun"))),stringsAsFactors=F)

data <- data.frame(liens_auteurs$nom_prenom1,liens_auteurs$nom_prenom2)
for (i in 1:nrow(data)){
  ligne <- c(liens_auteurs[i,1],liens_auteurs[i,2],sum((data$liens_auteurs.nom_prenom1 == data[i, 1])&(data$liens_auteurs.nom_prenom2 == data[i, 2])))
  nb_article_commun <- rbind(nb_article_commun, ligne)
  
}
colnames(nb_article_commun) <- c("nom_prenom1","nom_prenom2","nb_articles_communs")
liens_auteurs <- merge(liens_auteurs, nb_article_commun, by=c("nom_prenom1","nom_prenom2"))

## Creation du graphe

### Création d'un df des aretes representant les liens entre auteurs

auteurs_chiffres <- as.data.frame(cbind(unique(auteurs_articles$nom_prenom), 1:20))
colnames(auteurs_chiffres) <- c("nom_prenom1", "num1")
edges <- liens_auteurs %>% select(nom_prenom1, nom_prenom2,nb_articles_communs )
edges <- unique(edges)
edges <- merge(edges, auteurs_chiffres, by="nom_prenom1")
colnames(auteurs_chiffres) <- c("nom_prenom2", "num2")
edges <- merge(edges, auteurs_chiffres, by="nom_prenom2")
edges <- edges[,3:5]
colnames(edges) <- c("value","from", "to")


### Creation d'un df des noeuds pour définir la couleur des noeuds selon le nb d'articles écrits
nodes <- auteurs_articles %>% select(nom_prenom, nb_articles) 
nodes <- unique(nodes)
nodes$nb_articles <- as.numeric(nodes$nb_articles)
nodes <- nodes %>% mutate(groupe = case_when(nodes$nb_articles>=20 ~ "A", 
                                             (nodes$nb_articles<=15)&(nodes$nb_articles>10) ~ "B",
                                             nodes$nb_articles<=10 ~ "C"))
nodes <- nodes[-2]
colnames(auteurs_chiffres) <- c("nom_prenom", "num")
nodes <- merge(auteurs_chiffres, nodes, by="nom_prenom")
colnames(nodes) <- c("label", "id", "group")
graph <- visNetwork(nodes,edges)%>% visLegend(main="Groupes", position = "right", width = 0.1) #Nombre d'articles écrits : A = plus de 20, B = entre 10 et 15, C = moins de 10
visSave(graph, "docs/graph.htm", selfcontainded=TRUE, bacground="white")