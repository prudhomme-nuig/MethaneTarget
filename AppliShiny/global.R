
# Formation R Shiny 14-16 octobre 2020
# CIRAD Montpellier
# Exercice proposé par Sylvain Falala (INRAE UMR ASTRE Montpellier)
# Application maladies
# V09_dashboard


# global.R se charge avant ui.R et server.R
# Il permet de partager des variables entre ui et server : les variables sont dans l'environnement global
# Il permet par exemple de paramétrer les inputs dans ui en fonction de données lues dans un fichier


#### Chargement des librairies ####

library(shiny)

# Le package shinydashboard permet de créer une interface utilisateur de type tableau de bord
# Le tableau de bord est constitué d'une en-tête, d'une barre latérale et d'un corps
# https://rstudio.github.io/shinydashboard/

library(shinydashboard)

# Le package ggplot2 permet de créer des graphiques
# https://ggplot2.tidyverse.org/reference/index.html

library(ggplot2)

# Le package plotly permet de créer des graphiques interactifs
# notamment à partir de graphiques ggplot2
# https://plot.ly/r/shiny-gallery/

library(plotly)

# Le package dplyr permet la manipulation de données
# On l'utilise ici pour la fonction count
# https://dplyr.tidyverse.org/reference/index.html

library(dplyr)

# Le package leaflet est une implémentation dans R de la librairie JavaScript leaflet
# Il permet de créer des cartes interactives
# https://rstudio.github.io/leaflet/

library(leaflet)

library(reshape)

library(plyr)

#### Chargement du fichier de données ####

# Fichier de données Empres-i sur les foyers de Peste Porcine Africaine (African Swine Fever en anglais)
# en Europe du 1er janvier 2020 au 30 septembre 2020
# Obtenu librement sur le site Empres-i : http://empres-i.fao.org/eipws3g/

asfDF <- read.csv(file = "../output/table_AFOLU_balance_impact_person_fed.csv", 
                  sep = ",", 
                  #dec = ".",
                  quote = "\"",
                  header = TRUE, 
                  row.names = 1, 
                  stringsAsFactors = FALSE,
                  fill=TRUE)
colnames(asfDF)[193]<-"Rice"
colnames(asfDF)[194]<-"Rice.2010"
asfDF$Rice[asfDF$Rice<0]<-NA
production_list<-c('Milk','Beef.and.Buffalo.Meat','Monogastric.Meat','Eggs','Rice')
variables<-c("Production","Methane target")
asfDF["National methane index"]=asfDF["National.quota"]/asfDF["National.2010"]
allocations<-sort(unique(asfDF$Allocation.rule))
IAMs<-sort(unique(asfDF$Model))
scenarios<-sort(unique(asfDF$Scenario))
asfDF["Intensification"]<-"Base"
asfDF[(asfDF$Mitigation=="MACC") & (asfDF$Pathways!="Intensified"),"Intensification"]<-"MACC 2050"
asfDF[(asfDF$Mitigation=="MACC") & (asfDF$Pathways=="Intensified"),"Intensification"]<-"SI 2050"
pathways<-sort(unique(asfDF$Intensification))
products<-c("Milk","Dairy cattle meat","Non-dairy cattle meat","Pig meat","Chicken meat","Eggs")
plants<-c("Grass","Feed","International feed","Rice")
quartiles<-c("1","2","3","4")
targets<-c("Methane target","AFOLU balance")
emission_sources<-c("enteric","manure")
ghgs<-c("CH4","N2O")
animals<-c("Cattle..dairy","Cattle..non.dairy","Swine","Chickens..layers","Poultry.Birds")

#Fix rice problem
asfDF$Rice.2010<-asfDF$Production.Rice..paddy.2010
asfDF$Rice<-asfDF$Production.Rice..paddy.change+asfDF$Production.Rice..paddy.2010

asfDF$Methane.Quartile = asfDF$Country
asfDF$AFOLU.Quartile = asfDF$Country
for (country in countries)
{
  asfDF[asfDF$Country==country,]$Methane.Quartile = cut(asfDF[asfDF$Country==country,]$National.quota, 
                         breaks=quantile(asfDF[asfDF$Country==country,]$National.quota, probs=seq(0,1, by=0.25), na.rm=TRUE), 
                         include.lowest=TRUE)
  asfDF[asfDF$Country==country,]$Methane.Quartile <- factor(asfDF[asfDF$Country==country,]$Methane.Quartile, levels=c("1","2","3","4") )
  asfDF[asfDF$Country==country,]$AFOLU.Quartile = cut(asfDF[asfDF$Country==country,]$AFOLU.balance..with.GWP100., 
                                                      breaks=quantile(asfDF[asfDF$Country==country,]$AFOLU.balance..with.GWP100., probs=seq(0,1, by=0.25), na.rm=TRUE), 
                                                      include.lowest=TRUE)
  asfDF[asfDF$Country==country,]$AFOLU.Quartile <- factor(asfDF[asfDF$Country==country,]$AFOLU.Quartile, levels=c("1","2","3","4") )
}
asfDF$Activity.manure.Chickens..layers<-asfDF$Activity.Chickens..layers
asfDF$Activity.manure.Swine<-asfDF$Activity.Swine
asfDF$Activity.manure.Poultry.Birds<-asfDF$Activity.Poultry.Birds

asfDF$Quota.manure.Chickens..layers<-asfDF$Quota.Chickens..layers
asfDF$Quota.manure.Swine<-asfDF$Quota.Swine
asfDF$Quota.manure.Poultry.Birds<-asfDF$Quota.Poultry.Birds

#### Récupération des noms de pays ####

# Colonne "country"
# Les noms de pays vont servir à paramétrer les cases à cocher dans ui
countries <- sort(unique(asfDF$Country))

#Colour palet for leaflet
pal <- colorNumeric("viridis", NULL)
