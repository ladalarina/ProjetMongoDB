# Réseau de publications scientifiques

<iframe src="graph.html" class="is-fullwidth" height="600px" width="100%" title="Graphe social du top 20 des auteurs"></iframe>

Sur ce graphe, il est possible de visualiser les liens qu'ont les auteurs entre eux. Ces liens représentent les articles co-écrits. 
Pour construire ce graphe, il a été sélectionné les 20 auteurs ayant publié le plus d'articles sur la base de données HAL de 2021 puis pour chacun d'entre eux une liste d'article a été généré. Ces deux première étapes ont été réalisé à l'aide de deux requêtes :
- extraction de la table des 20 artistes ayant écrits le plus d'articles contenant leur nom, leur prénom et le nombre d'articles écrits, table *auteurs*;
- extraction pour chaque auteur de la précédente table (à l'aide d'une boucle) du titre de l'article écrit, table *auteurs_articles*. 
De ces deux requêtes on obtient un data frame avec une ligne pour un article, son auteur (nom et prénom) ainsi que le nombre d'articles écrits. 

Ensuite, un autre data frame est construit sur R pour obtenir les liens des auteurs dans le but de construire un graphe social. Cette table contient pour chaque ligne un auteur, son collaborateur et le titre de l'article écrit ainsi que le nombre d'articles écrits pour le premier auteur. Ce dernier élément permettra de définir la couleur du noeud sur le graphe (qui sera développé après). Ensuite il est construit une autre table qui pour chaque couple d'auteurs est renseigné le nombre d'articles en commun qui définira la taille des arêtes entre les noeuds. 

Avec ces deux tables, il est possible de définir la base du graphe qui sera construit à l'aide du package *visNetwork* :
- table nodes qui contient un id (chiffre généré dans l'ordre d'apparition d'un auteur dans la table *auteurs*), le label de l'auteur (nom et prénom) ainsi que le groupe dans lequel il appartient. Un auteur ayant écrit moins de 10 articles est du groupe C, entre 10 et 15 articles du groupe B et plus de 15 articles du groupe A. 
- tables edges qui contient les paires d'auteurs (from, to) et le nombre d'articles en communs qui définit la taille des arêtes. 

