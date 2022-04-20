library(mongolite)

mdb = mongo(
  collection = "hal_irisa_2021",
  url = "mongodb+srv://etudiant:ur2@clusterm1.0rm7t.mongodb.net/publications",
  verbose = TRUE
)
# 
# print(mdb$index())
# db.hal_irisa_2021.aggregate([
#   {$unwind : "$authors"}, 
#   {$group : {_id : "$authors.name", nb : {$sum : 1}}}, 
#   {$sort: {nb : -1}}, 
#   {$limit : 20}
# ])






