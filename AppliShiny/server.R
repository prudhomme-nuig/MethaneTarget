
# CIRAD Montpellier
# Auteur: Rémi Prudhomme basé sur formation donné par Sylvain Falafa
# Application sur définition de cible de méthane biogénique
# V1


# Fichier pour gérer les interactions de l'application Shiny


# Paramètres d'entrée :
# input : liste de boutons, menus déroulants, curseurs... définis dans UI
# output : liste des affichages (tableaux, graphes, cartes...) définis dans UI


server <- function(input, output) {
  
  
  #### Expression réactive qui va renvoyer un nouveau data frame en fonction des différents inputs ####
  
  # Il suffit ensuite d'appeler tempDF() dans les différents render pour qu'ils disposent du data frame
  
  tempDF <- reactive({
    
    # input$sliderPeriod[1] : date renvoyée par le bouton gauche du slider temporel
    # input$sliderPeriod[2] : date renvoyée par le bouton droit du slider temporel
    # input$cbCountry : vecteur avec les noms de pays sélectionnés
    
    countryDF <- asfDF[asfDF$Country %in% input$cbCountry, ]
    
    countryDF <- countryDF[countryDF$Allocation.rule %in% input$allocation,]
    
    if (input$variable=="Production")
      {
      df_with_all_prod_to_plot<-data.frame()
      for (production in production_list)
        {
         countryDF[paste(production,'index',sep=".")]<-countryDF[production]/countryDF[paste(production,'2010',sep=".")]
         countryDF[countryDF[paste(production,'2010',sep=".")]==0,paste(production,'index',sep=".")]<-0
         itemDF<-data.frame('Item'=rep(production,length(countryDF$Country)))
         df_to_concat<-cbind(countryDF[c('Country','Intensification',paste(production,'2010',sep="."),paste(production,'index',sep="."),production,"Allocation.rule")],itemDF)
         names(df_to_concat)[3]="Production in 2010 (Mt)"
         names(df_to_concat)[4]="Production index"
         names(df_to_concat)[5]="Production"
         df_with_all_prod_to_plot<-rbind(df_with_all_prod_to_plot,df_to_concat)
      }
      df_with_all_prod_to_plot$Item <- as.factor(df_with_all_prod_to_plot$Item)
      df_with_all_prod_to_plot
    }
    else if (input$variable=="Methane target")
    {
      countryDF
    }
  })
  
  dataMethaneDF <- reactive({
    
    # input$sliderPeriod[1] : date renvoyée par le bouton gauche du slider temporel
    # input$sliderPeriod[2] : date renvoyée par le bouton droit du slider temporel
    # input$cbCountry : vecteur avec les noms de pays sélectionnés
    
    countryDF<-asfDF[asfDF$Model %in% input$MethaneIAM, ]
    
    countryDF<-countryDF[countryDF$Scenario %in% input$MethaneScenario, ]
    
    countryDF["Methane reduction"] <- 100 - countryDF["X2050"]/countryDF["X2010"]*100
    
    countryDF["World"]<-"World"
    
    countryDF
    
  })
  
  dataEIDF <- reactive({
    
    # input$sliderPeriod[1] : date renvoyée par le bouton gauche du slider temporel
    # input$sliderPeriod[2] : date renvoyée par le bouton droit du slider temporel
    # input$cbCountry : vecteur avec les noms de pays sélectionnés
    
    countryDF<-asfDF[asfDF$Country %in% input$EICountry, ]
    
    countryDF<-countryDF[countryDF$Intensification %in% input$EIPathway, ]
    
    if (input$EIGaz=="CH4") {
      header_emission<-paste("Quota",input$EIsource,input$EIAnim,sep=".")
      header_activity<-paste("Activity",input$EIsource,input$EIAnim,sep=".")
        
      }
      if (input$EIGaz=="N2O"){
        header_emission<-paste("N2O",input$EIsource,input$EIAnim,sep=".")
        header_activity<-paste("Activity",input$EIsource,input$EIAnim,sep=".")
      }

    dataEIDF <- countryDF[c("Country","Intensification",header_emission,header_activity)]
    dataEIDF["EI"]<-dataEIDF[header_emission]/dataEIDF[header_activity]
    dataEIDF <- dataEIDF[c("Country","Intensification","EI")]
    dataEIDF<-dataEIDF[!duplicated(dataEIDF[c("Country","Intensification")]),]
    dataEIDF
  })
  
  dataVegDF <- reactive({
    
    # input$sliderPeriod[1] : date renvoyée par le bouton gauche du slider temporel
    # input$sliderPeriod[2] : date renvoyée par le bouton droit du slider temporel
    # input$cbCountry : vecteur avec les noms de pays sélectionnés
    
    countryDF<-asfDF[asfDF$Country %in% input$VegCountry, ]
    
    countryDF<-countryDF[countryDF$Intensification %in% input$VegPathway, ]
    
    if (input$VegProduct=="Grass") {
      product_list<-c("Country",'Intensification',"National.Grass.yield.Cattle..dairy")
      name_list<-c("Country",'Pathway',"Grass yield")
    }
    else if (input$VegProduct=="Feed"){
      product_list<-c("Country",'Intensification',"National.Feed.yield.Cattle..dairy")
      name_list<-c("Country",'Pathway',"Feed yield")
    }
    else if (input$VegProduct=="International feed"){
      product_list<-c("Country",'Intensification',"International.Feed.yield.Cattle..dairy")
      name_list<-c("Country",'Pathway',"International feed yield")
    }
    else if (input$VegProduct=="Rice"){
      product_list<-c("Country",'Intensification',"Yield.Rice..paddy")
      name_list<-c("Country",'Pathway',"Rice yield")
    }
    
    dataVegDF <- countryDF[product_list]
    
    colnames(dataVegDF) <- name_list
    
    measure_name_list<-name_list[-1]
    measure_name_list<-measure_name_list[-1]
    
    dataVeg<-melt(dataVegDF,id.vars=c('Country',"Pathway"), measure.vars=measure_name_list)
    
    dataVeg<-dataVeg[!duplicated(dataVeg),]
    #dataVeg[(dataVeg$variable=="Grass yield") & (dataVeg$Country=="India"),"value"]=dataVeg[(dataVeg$variable=="Grass yield") & (dataVeg$Country=="Brazil"),"value"]
    colnames(dataVeg)<-c("Country",'Pathway',"Yields","Yield (t/ha)")
    dataVeg
    
  })
  
  dataAnimDF <- reactive({
    
    # input$sliderPeriod[1] : date renvoyée par le bouton gauche du slider temporel
    # input$sliderPeriod[2] : date renvoyée par le bouton droit du slider temporel
    # input$cbCountry : vecteur avec les noms de pays sélectionnés
    
    countryDF<-asfDF[asfDF$Country %in% input$AnimCountry, ]
    
    countryDF<-countryDF[countryDF$Intensification %in% input$AnimPathway, ]
    
    if (input$AnimProduct=="Milk") {
      product_list<-c("Country",'Intensification',"Milk..Total.Cattle..dairy.yield")
      name_list<-c("Country",'Pathway',"Milk yield")
    }
    else if (input$AnimProduct=="Dairy cattle meat"){
      product_list<-c("Country",'Intensification',"Beef.and.Buffalo.Meat.Cattle..dairy.yield")
      name_list<-c("Country",'Pathway',"Dairy cattle meat yield")
    }
    else if (input$AnimProduct=="Non-dairy cattle meat"){
      product_list<-c("Country",'Intensification',"Beef.and.Buffalo.Meat.Cattle..non.dairy.yield")
      name_list<-c("Country",'Pathway',"Non-dairy cattle meat yield")
    }
    else if (input$AnimProduct=="Pig meat"){
      product_list<-c("Country",'Intensification',"Meat..pig.Swine.yield")
      name_list<-c("Country",'Pathway',"Pig meat yield")
    }
    else if (input$AnimProduct=="Chicken meat"){
      product_list<-c("Country",'Intensification',"Meat..Poultry.Poultry.Birds.yield")
      name_list<-c("Country",'Pathway',"Poultry meat yield")
    }
    
    else if (input$AnimProduct=="Eggs"){
      product_list<-c("Country",'Intensification',"Eggs.Primary.Chickens..layers.yield")
      name_list<-c("Country",'Pathway',"Eggs yield")
    }
    
    dataAnimDF <- countryDF[product_list]
    
    colnames(dataAnimDF) <- name_list
    
    measure_name_list<-name_list[-1]
    measure_name_list<-measure_name_list[-1]
    
    dataAnimDF<-melt(dataAnimDF,id.vars=c('Country','Pathway'), measure.vars=measure_name_list)
    
    dataAnimDF<-dataAnimDF[!duplicated(dataAnimDF),]
    colnames(dataAnimDF)<-c("Country","Pathway","Yields","Yield (t/ha)")
    dataAnimDF
    
  })
  
  dataBack <- reactive({
    
    # input$sliderPeriod[1] : date renvoyée par le bouton gauche du slider temporel
    # input$sliderPeriod[2] : date renvoyée par le bouton droit du slider temporel
    # input$cbCountry : vecteur avec les noms de pays sélectionnés
    
    countryDF<-asfDF[asfDF$Country %in% input$BackCountry, ]
    
    if (input$BackSelect == "Methane target") {
      column_list<-c("Country","Methane.Quartile","National.quota","AFOLU.balance..with.GWP100.","CO2.offset..MtCO2.","Person.fed.in.energy..Mio.heads.","Person.fed.in.protein..Mio.heads.")
    }
    
    else if (input$BackSelect == "AFOLU balance") {
      column_list<-c("Country","AFOLU.Quartile","National.quota","AFOLU.balance..with.GWP100.","CO2.offset..MtCO2.","Person.fed.in.energy..Mio.heads.","Person.fed.in.protein..Mio.heads.")
    }
    
    dataBackDF <- countryDF[column_list]
    measure_name_list<-column_list[-1]
    measure_name_list<-measure_name_list[-1]

    colnames(dataBackDF)[2]<-"Quartiles"
    
    dataBack<-melt(dataBackDF,id.vars=c('Country',colnames(dataBackDF)[2]), measure.vars=measure_name_list)
    
    dataBack
    
  })
  
  dataBack2 <- reactive({
    
    # input$sliderPeriod[1] : date renvoyée par le bouton gauche du slider temporel
    # input$sliderPeriod[2] : date renvoyée par le bouton droit du slider temporel
    # input$cbCountry : vecteur avec les noms de pays sélectionnés
    
    input$EnterTarget
    
    input$Back2Country
    
    countryDF<-asfDF[asfDF$Country == input$Back2Country, ]
    
    countryDF<-countryDF[countryDF$National.quota <= input$MethaneTargetInput+0.05*input$MethaneTargetInput, ]
    
    countryDF<-countryDF[countryDF$National.quota >= input$MethaneTargetInput-0.05*input$MethaneTargetInput, ]
    
    column_list<-c("Country","National.quota","AFOLU.balance..with.GWP100.","CO2.offset..MtCO2.","Person.fed.in.energy..Mio.heads.","Person.fed.in.protein..Mio.heads.")
    
    dataBac2kDF <- countryDF[column_list]
    measure_name_list<-column_list[-1]

    dataBack2<-melt(dataBackDF,id.vars=c('Country'), measure.vars=measure_name_list)
    
    dataBack2
    
  })
  
  #### Affichage interactif avec plotly de l'histogramme du nombre de cas par mois ####
  
  output$plotHisto <- renderPlot({
    
    # Le render observe le data frame renvoyé par l'expression réactive tempDF
    # NE PAS OUBLIER LES PARENTHESES de tempDF()
    
    if (input$variable=="Production"){
      ggplot(tempDF(), aes(x = Item, y = `Production index`,fill=Allocation.rule))+
        geom_boxplot(outline=FALSE)+ 
        facet_wrap(~Country, scales = "free") +
        theme(axis.text.x = element_text(angle = 30, hjust = 1),
              axis.title.x=element_blank())
      #scale_y_continuous(limits = quantile(df_with_all_prod_to_plot$`Production index`, c(0.1, 0.9)))
    }
    else if (input$variable=="Methane target"){
      ggplot(tempDF(), aes(x = Country, y = `National methane index`,fill=Allocation.rule))+
        geom_boxplot(outline=FALSE)+ 
        #geom_hline(yintercept=ref_value(), linetype="dashed", color = "red")+
        #facet_wrap(~Country, scales = "free") + 
        theme(axis.text.x = element_text(angle = 30, hjust = 1),
              axis.title.x=element_blank())
      #scale_y_continuous(limits = quantile(df_with_all_prod_to_plot$`Production index`, c(0.1, 0.9)))
    }
    
  })
  
  output$plotmethane <- renderPlot({
    
    # Le render observe le data frame renvoyé par l'expression réactive tempDF
    # NE PAS OUBLIER LES PARENTHESES de tempDF()
    
    ggplot(dataMethaneDF(), aes(x = World, y = `Methane reduction`))+
      geom_boxplot(outline=FALSE)+ 
      #facet_wrap(~Country, scales = "free") + 
      theme(axis.text.x = element_text(angle = 30, hjust = 1),
            axis.title.x=element_blank())
    
  })
  
  output$plotVeg <- renderPlot({
    
    # Le render observe le data frame renvoyé par l'expression réactive tempDF
    # NE PAS OUBLIER LES PARENTHESES de tempDF()
    
    ggplot(dataVegDF(), aes(x = Country, y = `Yield (t/ha)`,fill=Pathway))+
      geom_bar(stat="identity",position=position_dodge())+ 
      #facet_wrap(~Country, scales = "free") + 
      theme(axis.text.x = element_text(angle = 30, hjust = 1),
            axis.title.x=element_blank())
    
  })
  
  output$plotAnim <- renderPlot({
    
    # Le render observe le data frame renvoyé par l'expression réactive tempDF
    # NE PAS OUBLIER LES PARENTHESES de tempDF()
    
    ggplot(dataAnimDF(), aes(x = Country, y = `Yield (t/ha)`,fill=Pathway))+
      geom_bar(stat="identity",position=position_dodge())+ 
      #facet_wrap(~Country, scales = "free") + 
      theme(axis.text.x = element_text(angle = 30, hjust = 1),
            axis.title.x=element_blank())
    
  })
  
  output$plotEI <- renderPlot({
    
    # Le render observe le data frame renvoyé par l'expression réactive tempDF
    # NE PAS OUBLIER LES PARENTHESES de tempDF()
    
    ggplot(dataEIDF(), aes(x = Country, y = EI,fill=Intensification))+
      geom_bar(stat="identity",position=position_dodge())+ 
      #facet_wrap(~Country, scales = "free") + 
      theme(axis.text.x = element_text(angle = 30, hjust = 1),
            axis.title.x=element_blank())
    
  })
  
  
  
  output$plotback <- renderPlot({
    
    # Le render observe le data frame renvoyé par l'expression réactive tempDF
    # NE PAS OUBLIER LES PARENTHESES de tempDF()
    
    ggplot(dataBack(), aes(x = Quartiles, y = value,fill=Quartiles))+
      geom_boxplot(outline=FALSE)+
      facet_wrap(~variable, scales = "free")+
      #facet_wrap(~Country, scales = "free") + 
      theme(axis.text.x = element_text(angle = 30, hjust = 1),
            axis.title.x=element_blank())
    
  })
  
  output$plotback2 <- renderPlot({
    input$EnterTarget
    ggplot(dataBack2(), aes(x = variable, y = value,fill=variable))+
      geom_boxplot(outline=FALSE)+
      facet_wrap(~variable, scales = "free")+
      #facet_wrap(~Country, scales = "free") + 
      theme(axis.text.x = element_text(angle = 30, hjust = 1),
            axis.title.x=element_blank())
    })
  
 
  #### Affichage du tableau du nombre de cas par zone administrative ####
  
  output$tableAdmin <- renderDataTable({
    
    # Le render observe le data frame renvoyé par l'expression réactive tempDF
    
    # Compte le nombre de cas par zone administrative par pays
    
    tempDF()[c("Country","Index","Production index")]
    
  }, options = list(pageLength = 10)) # nombre de lignes par page
  
  
  
  #### Affichage du résumé statistique ####
  
  output$verbTextSummary <- renderPrint({
    
    # Le render observe le data frame renvoyé par l'expression réactive tempDF
    
    summary(tempDF()[, c("sumCases", "sumDeaths", "sumDestroyed")])
    
  })
  
  
  #### Initialisation de la carte leaflet à partir du data frame complet ####
  
  # output$outbreakMap <- renderLeaflet({
  #   
  #   # Le render est ici non réactif car il n'observe rien
  #   # Il va juste servir à initialiser la carte leaflet, notamment charger le fond de carte
  #   # La mise à jour de la carte se fera avec le proxy (cf ci-dessous)
  #   
  #   
  #   leaflet(asfDF$Country) %>%
  #     addTiles() %>%
  #     addPolygons(stroke = FALSE, smoothFactor = 0.3, fillOpacity = 1,
  #                 fillColor = "red")
  #   
  #   # leaflet(data = asfDF) %>% # le data frame complet va être utilisé
  #   #   addProviderTiles("OpenStreetMap.Mapnik") %>% # charge le fond de carte OpenStreetMap
  #   #   addMarkers(lng = ~longitude, lat = ~latitude,
  #   #              clusterOptions = markerClusterOptions()) %>% # ajoute les points de foyers et affiche par cluster
  #   #   fitBounds(~min(longitude), ~min(latitude), ~max(longitude), ~max(latitude)) # bornes de la carte
  # 
  # })
  
  
  # #### Mise à jour de la carte leaflet avec le proxy ####
  # 
  # observe({
  #   
  #   # L'observateur observe le data frame renvoyé par l'expression réactive tempDF
  #   
  #   # leafletProxy va faire une mise à jour de l'objet leaflet existant, 
  #   # SANS le ré-initialiser (contrairement au render)
  #   # Ainsi le fond de carte n'est pas rechargé à nouveau et le zoom n'est pas ré-initialisé
  #   
  #   # Pour les clusters, passez la souris sur le cercle pour afficher la zone concernée
  #   
  #   leafletProxy(mapId = "outbreakMap", data = tempDF()) %>% 
  #     clearMarkerClusters() %>% # efface tous les clusters
  #     addMarkers(lng = ~longitude, lat = ~latitude, 
  #                clusterOptions = markerClusterOptions()) # ajoute les points de foyers et affiche par cluster
  #   
  # })
  
  
  #### Affichage des informations sur l'auteur ####
  
  output$uiAbout <- renderUI({
    
    # Le render observe le data frame renvoyé par l'expression réactive tempDF
    
    p(
      
      p(h3("Cette application Shiny a été développée par Rémi Prudhomme")),
      
      p(h4("Les données de rendement, les facteurs d'émissions, le surfaces herbagère et de culture, les niveaux de productions sont extrait de la base de données FAOSTAT:",
           a(href = "http://www.fao.org/faostat/en", title = "Aller sur le site FAOSTAT", target = "_blank", "FAOSTAT")))
      
      
      
    )
    
  })
  
  
}

