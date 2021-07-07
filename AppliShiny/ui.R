
# CIRAD Montpellier
# Auteur: Rémi Prudhomme basé sur formation donné par Sylvain Falafa
# Application sur définition de cible de méthane biogénique
# V1

# Fichier de définition de l'interface utilisateur pour l'application Shiny

#### Définition de l'en-tête ####

header <- dashboardHeader(title = "Methane target")


#### Définition de la barre latérale ####


sidebar <- dashboardSidebar(

  # Slider temporel avec double curseur pour définir une période
  # min et max doivent être des dates pour que le slider soit temporel et défile par jour
  # L'option value doit avoir un vecteur de 2 dates pour disposer du double curseur

  # sliderInput(inputId = "sliderPeriod",
  #             label = "Choisissez la période",
  #             min = minDate, # minDate définie dans global.R
  #             max = maxDate, # maxDate définie dans global.R
  #             value = c(minDate, maxDate)
  #             ),

  # Menu avec 3 onglets :
  # - Informations : affiche une page avec 3 boites : histogramme, tableau et résumé
  # - Carte : affiche la carte leaflet
  # - A propos de : affiche le texte html sur l'auteur

  sidebarMenu(
    menuItem(text = "Home", tabName = "Home"),

    menuItem(text = "Data", #tabName = "infoTab"),
      menuSubItem(text = "Global scenarios",tabName = "methaneTab"),
      menuSubItem(text = "Animal emission factors",tabName = "mitigationTab"),
      menuSubItem(text = "Rice emission factors",tabName = "ricemitigationTab"),
      menuSubItem(text = "Plant yields",tabName = "yieldvegTab"),
      menuSubItem(text = "Animal yields",tabName = "yieldTab")
      ),

    menuItem(text = "Results",
             menuSubItem(text = "Direct impacts",tabName = "resultsTab"),
             menuSubItem(text = "Back-casting",tabName = "BackTab"),
             menuSubItem(text = "Define your methane target",tabName = "BackTab2")
             ),

    menuItem(text = "About", tabName = "aboutTab")

  )
)



#### Définition du corps ####

body <- dashboardBody(

  # Pour faire correspondre un menuItem avec un tabItem,
  # assurez-vous qu'ils ont des valeurs correspondantes pour tabName

  tabItems(

    # Page Informations avec 3 boites : histogramme, tableau et résumé

    tabItem(tabName = "methaneTab",

            fluidRow(

              column(width = 4,

                     box(title = "variables",
                         status = "danger", # couleur rouge
                         solidHeader = TRUE,
                         width = NULL,

                         # Tableau du nombre de cas par zone administrative

                         checkboxGroupInput(inputId = "MethaneIAM",
                                            label = "Choose the IAM",
                                            choices = IAMs, # countries = noms des pays définis dans global.R
                                            selected = IAMs # tous les pays sont sélectionnés
                         ),

                         checkboxGroupInput(inputId = "MethaneScenario",
                                            label = "Choose the scenario",
                                            choices = scenarios, # countries = noms des pays définis dans global.R
                                            selected = scenarios # tous les pays sont sélectionnés
                         )

                         #dataTableOutput(outputId = "tableAdmin")

                         #Cases à cocher avec les noms des pays définis dans global.R

                         # checkboxGroupInput(inputId = "cbCountry",
                         #                    label = "Choisissez le pays",
                         #                    choices = countries, # countries = noms des pays définis dans global.R
                         #                    selected = countries # tous les pays sont sélectionnés
                         # ),
                         #
                         # radioButtons(inputId = "variable",
                         #              label = "Choisissez la variable",
                         #              choices = variables, # countries = noms des pays définis dans global.R
                         #              selected = "Production" # tous les pays sont sélectionnés
                         # )

                     )

              ),

              column(width = 8, # largeur que prend la colonne sur la ligne, sur une échelle de 12

                # Définition d'une boite

                box(title = "Global methane target", # en-tête titre
                    status = "primary", # couleur pour l'en-tête et le cadre de la boite, ici bleu foncé
                    solidHeader = TRUE, # colorie l'en-tête et le cadre avec la couleur status
                    width = NULL, # prend toute la largeur de la colonne

                    # Affichage de l'histogramme du nombre de cas par mois

                    plotOutput(outputId = "plotmethane")

                )
              )
            )

    ),
    tabItem(tabName = "mitigationTab",

            fluidRow(

              column(width = 4,

                     box(title = "Variables",
                         status = "danger", # couleur rouge
                         solidHeader = TRUE,
                         width = NULL,

                         # Tableau du nombre de cas par zone administrative
                         checkboxGroupInput(inputId = "EICountry",
                                            label = "Choose the country",
                                            choices = countries, # countries = noms des pays définis dans global.R
                                            selected = countries # tous les pays sont sélectionnés
                         ),

                         checkboxGroupInput(inputId = "EIPathway",
                                            label = "Choose the intensification pathway",
                                            choices = pathways, # countries = noms des pays définis dans global.R
                                            selected = pathways # tous les pays sont sélectionnés
                         ),
                         radioButtons(inputId = "EIAnim",
                                            label = "Choose the animal",
                                            choices = animals, # countries = noms des pays définis dans global.R
                                            selected = animals[1] # tous les pays sont sélectionnés
                         ),

                         radioButtons(inputId = "EIsource",
                                            label = "Choose the emission source",
                                            choices = emission_sources, # countries = noms des pays définis dans global.R
                                            selected = emission_sources[1] # tous les pays sont sélectionnés
                         ),
                         radioButtons(inputId = "EIGaz",
                                      label = "Choose the GHG",
                                      choices = ghgs, # countries = noms des pays définis dans global.R
                                      selected = ghgs[1] # tous les pays sont sélectionnés
                         )

                         #dataTableOutput(outputId = "tableAdmin")

                         #Cases à cocher avec les noms des pays définis dans global.R

                         # checkboxGroupInput(inputId = "cbCountry",
                         #                    label = "Choisissez le pays",
                         #                    choices = countries, # countries = noms des pays définis dans global.R
                         #                    selected = countries # tous les pays sont sélectionnés
                         # ),
                         #
                         # radioButtons(inputId = "variable",
                         #              label = "Choisissez la variable",
                         #              choices = variables, # countries = noms des pays définis dans global.R
                         #              selected = "Production" # tous les pays sont sélectionnés
                         # )

                     )

              ),

              column(width = 8, # largeur que prend la colonne sur la ligne, sur une échelle de 12

                     # Définition d'une boite

                     box(title = "Emission Factors", # en-tête titre
                         status = "primary", # couleur pour l'en-tête et le cadre de la boite, ici bleu foncé
                         solidHeader = TRUE, # colorie l'en-tête et le cadre avec la couleur status
                         width = NULL, # prend toute la largeur de la colonne

                         # Affichage de l'histogramme du nombre de cas par mois

                         plotOutput(outputId = "plotEI")

                     )
              )
            )

    ),
    tabItem(tabName = "ricemitigationTab",
            
            fluidRow(
              
              column(width = 4,
                     
                     box(title = "Variables",
                         status = "danger", # couleur rouge
                         solidHeader = TRUE,
                         width = NULL,
                         
                         # Tableau du nombre de cas par zone administrative
                         checkboxGroupInput(inputId = "EI_rice_Country",
                                            label = "Choose the country",
                                            choices = countries, # countries = noms des pays définis dans global.R
                                            selected = countries # tous les pays sont sélectionnés
                         ),
                         
                         checkboxGroupInput(inputId = "EI_rice_Pathway",
                                            label = "Choose the intensification pathway",
                                            choices = pathways, # countries = noms des pays définis dans global.R
                                            selected = pathways # tous les pays sont sélectionnés
                         )
                         
                     )
                     
              ),
              
              column(width = 8, # largeur que prend la colonne sur la ligne, sur une échelle de 12
                     
                     # Définition d'une boite
                     
                     box(title = "Emission Factors", # en-tête titre
                         status = "primary", # couleur pour l'en-tête et le cadre de la boite, ici bleu foncé
                         solidHeader = TRUE, # colorie l'en-tête et le cadre avec la couleur status
                         width = NULL, # prend toute la largeur de la colonne
                         
                         # Affichage de l'histogramme du nombre de cas par mois
                         
                         plotOutput(outputId = "plotEI_rice")
                         
                     )
              )
            )
            
    ),
    tabItem(tabName = "yieldvegTab",

            fluidRow(

              column(width = 2,

                     box(title = "variables",
                         status = "danger", # couleur rouge
                         solidHeader = TRUE,
                         width = NULL,

                         # Tableau du nombre de cas par zone administrative

                         checkboxGroupInput(inputId = "VegCountry",
                                            label = "Choose the country",
                                            choices = countries, # countries = noms des pays définis dans global.R
                                            selected = countries # tous les pays sont sélectionnés
                         ),

                         checkboxGroupInput(inputId = "VegPathway",
                                            label = "Choose the intensification pathway",
                                            choices = pathways, # countries = noms des pays définis dans global.R
                                            selected = pathways # tous les pays sont sélectionnés
                         ),
                         radioButtons(inputId = "VegProduct",
                                      label = "Choose the plant product",
                                      choices = plants, # countries = noms des pays définis dans global.R
                                      selected = "Grass" # tous les pays sont sélectionnés
                         )

                         #dataTableOutput(outputId = "tableAdmin")

                         #Cases à cocher avec les noms des pays définis dans global.R

                         # checkboxGroupInput(inputId = "cbCountry",
                         #                    label = "Choisissez le pays",
                         #                    choices = countries, # countries = noms des pays définis dans global.R
                         #                    selected = countries # tous les pays sont sélectionnés
                         # ),
                         #
                         # radioButtons(inputId = "variable",
                         #              label = "Choisissez la variable",
                         #              choices = variables, # countries = noms des pays définis dans global.R
                         #              selected = "Production" # tous les pays sont sélectionnés
                         # )

                     )

              ),

              column(width = 10, # largeur que prend la colonne sur la ligne, sur une échelle de 12

                     # Définition d'une boite

                     box(title = "Boxplot", # en-tête titre
                         status = "primary", # couleur pour l'en-tête et le cadre de la boite, ici bleu foncé
                         solidHeader = TRUE, # colorie l'en-tête et le cadre avec la couleur status
                         width = NULL, # prend toute la largeur de la colonne

                         # Affichage de l'histogramme du nombre de cas par mois

                         plotOutput(outputId = "plotVeg")

                     )
              )
            )

    ),

    tabItem(tabName = "yieldTab",

            fluidRow(

              column(width = 2,

                     box(title = "variables",
                         status = "danger", # couleur rouge
                         solidHeader = TRUE,
                         width = NULL,

                         # Tableau du nombre de cas par zone administrative

                         checkboxGroupInput(inputId = "AnimCountry",
                                            label = "Choose the country",
                                            choices = countries, # countries = noms des pays définis dans global.R
                                            selected = countries # tous les pays sont sélectionnés
                         ),

                         checkboxGroupInput(inputId = "AnimPathway",
                                            label = "Choose the intensification pathway",
                                            choices = pathways, # countries = noms des pays définis dans global.R
                                            selected = pathways # tous les pays sont sélectionnés
                         ),
                         radioButtons(inputId = "AnimProduct",
                                            label = "Choose the animal",
                                            choices = products, # countries = noms des pays définis dans global.R
                                            selected = products[1] # tous les pays sont sélectionnés
                         ),

                         #dataTableOutput(outputId = "tableAdmin")

                         #Cases à cocher avec les noms des pays définis dans global.R

                         # checkboxGroupInput(inputId = "cbCountry",
                         #                    label = "Choisissez le pays",
                         #                    choices = countries, # countries = noms des pays définis dans global.R
                         #                    selected = countries # tous les pays sont sélectionnés
                         # ),
                         #
                         # radioButtons(inputId = "variable",
                         #              label = "Choisissez la variable",
                         #              choices = variables, # countries = noms des pays définis dans global.R
                         #              selected = "Production" # tous les pays sont sélectionnés
                         # )

                     )

              ),

              column(width = 10, # largeur que prend la colonne sur la ligne, sur une échelle de 12

                     # Définition d'une boite

                     box(title = "Boxplot", # en-tête titre
                         status = "primary", # couleur pour l'en-tête et le cadre de la boite, ici bleu foncé
                         solidHeader = TRUE, # colorie l'en-tête et le cadre avec la couleur status
                         width = NULL, # prend toute la largeur de la colonne

                         # Affichage de l'histogramme du nombre de cas par mois

                         plotOutput(outputId = "plotAnim")

                     )
              )
            )

    ),


    # Page avec la carte leaflet

    tabItem(tabName = "resultsTab",

            fluidRow(

              column(width = 2,

                     box(title = "variables",
                         status = "danger", # couleur rouge
                         solidHeader = TRUE,
                         width = NULL,

                         # Tableau du nombre de cas par zone administrative

                         #dataTableOutput(outputId = "tableAdmin")

                         #Cases à cocher avec les noms des pays définis dans global.R

                         checkboxGroupInput(inputId = "cbCountry",
                                            label = "Select the country",
                                            choices = countries, # countries = noms des pays définis dans global.R
                                            selected = countries # tous les pays sont sélectionnés
                         ),

                         radioButtons(inputId = "variable",
                                      label = "Select the variable",
                                      choices = variables, # countries = noms des pays définis dans global.R
                                      selected = "Production" # tous les pays sont sélectionnés
                         ),

                         checkboxGroupInput(inputId = "allocation",
                                            label = "Select the allocation rule",
                                            choices = allocations, # countries = noms des pays définis dans global.R
                                            selected = allocations # tous les pays sont sélectionnés
                         )

                     )

              ),

              column(width =10, # largeur que prend la colonne sur la ligne, sur une échelle de 12

                     # Définition d'une boite

                     box(title = "Results", # en-tête titre
                         status = "primary", # couleur pour l'en-tête et le cadre de la boite, ici bleu foncé
                         solidHeader = TRUE, # colorie l'en-tête et le cadre avec la couleur status
                         width = NULL, # prend toute la largeur de la colonne

                         # Affichage de l'histogramme du nombre de cas par mois

                         plotOutput(outputId = "plotHisto")

                     )
              )
            )

    ),

    tabItem(tabName = "BackTab",

            fluidRow(

              column(width = 2,

                     box(title = "variables",
                         status = "danger", # couleur rouge
                         solidHeader = TRUE,
                         width = NULL,

                         # Tableau du nombre de cas par zone administrative

                         #dataTableOutput(outputId = "tableAdmin")

                         #Cases à cocher avec les noms des pays définis dans global.R

                         radioButtons(inputId = "BackCountry",
                                            label = "Select the country",
                                            choices = countries, # countries = noms des pays définis dans global.R
                                            selected = countries[1] # tous les pays sont sélectionnés
                         ),

                         radioButtons(inputId = "BackSelect",
                                      label = "Select the target",
                                      choices = targets, # countries = noms des pays définis dans global.R
                                      selected = targets[1] # tous les pays sont sélectionnés
                         )

                     )

              ),

              column(width = 10, # largeur que prend la colonne sur la ligne, sur une échelle de 12

                     # Définition d'une boite

                     box(title = "Results", # en-tête titre
                         status = "primary", # couleur pour l'en-tête et le cadre de la boite, ici bleu foncé
                         solidHeader = TRUE, # colorie l'en-tête et le cadre avec la couleur status
                         width = NULL, # prend toute la largeur de la colonne

                         # Affichage de l'histogramme du nombre de cas par mois

                         plotOutput(outputId = "plotback")

                     )
              ),
              column(width = 12, # largeur que prend la colonne sur la ligne, sur une échelle de 12

                     # Définition d'une boite

                     box(title = "Tableau de valeurs", # en-tête titre
                         status = "primary", # couleur pour l'en-tête et le cadre de la boite, ici bleu foncé
                         solidHeader = TRUE, # colorie l'en-tête et le cadre avec la couleur status
                         width = NULL, # prend toute la largeur de la colonne
                         #tags$head(tags$style(HTML(".tab-pane { height: 70vh; overflow-y: auto; }" ))),

                         # Affichage de l'histogramme du nombre de cas par mois

                         #dataTableOutput(outputId = "tableAdmin")

                     )
              )
            )

    ),

    tabItem(tabName = "BackTab2",

            fluidRow(

              column(width = 2,

                     box(title = "Methane target",
                         status = "danger", # couleur rouge
                         solidHeader = TRUE,
                         width = NULL,

                         radioButtons(inputId = "Back2Country",
                                      label = "Select the country",
                                      choices = countries, # countries = noms des pays définis dans global.R
                                      selected = countries[1] # tous les pays sont sélectionnés
                         ),

                         numericInput(inputId="MethaneTargetInput",
                                      label="Methane target in tCH4/yr",
                                      value=550000,
                                      min = NA, max = NA, step = NA),
                         actionButton(inputId = "EnterTarget", label = "Enter CH4 Target")

                     )

              ),

              column(width = 10, # largeur que prend la colonne sur la ligne, sur une échelle de 12

                     # Définition d'une boite

                     box(title = "Results", # en-tête titre
                         status = "primary", # couleur pour l'en-tête et le cadre de la boite, ici bleu foncé
                         solidHeader = TRUE, # colorie l'en-tête et le cadre avec la couleur status
                         width = NULL, # prend toute la largeur de la colonne

                         # Affichage de l'histogramme du nombre de cas par mois

                         plotOutput(outputId = "plotback2")

                     )
              ),
              column(width = 12, # largeur que prend la colonne sur la ligne, sur une échelle de 12

                     # Définition d'une boite

                     box(title = "Tableau de valeurs", # en-tête titre
                         status = "primary", # couleur pour l'en-tête et le cadre de la boite, ici bleu foncé
                         solidHeader = TRUE, # colorie l'en-tête et le cadre avec la couleur status
                         width = NULL, # prend toute la largeur de la colonne
                         #tags$head(tags$style(HTML(".tab-pane { height: 70vh; overflow-y: auto; }" ))),

                         # Affichage de l'histogramme du nombre de cas par mois

                         #dataTableOutput(outputId = "tableAdmin")

                     )
              )
            )

    ),

    # Page avec les informations sur l'auteur

    tabItem(tabName = "aboutTab",

            uiOutput(outputId = "uiAbout")

            ),
    tabItem(tabName = "Home",

            includeMarkdown("www/home.md")

    )


  )

)


#### Définition de la page principale ####

dashboardPage(
  header,
  sidebar,
  body
)
