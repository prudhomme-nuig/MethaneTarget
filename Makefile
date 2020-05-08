#To launch the Makefile:
#Read the README.md

#To be changed depending on the localization of your python folder
launch_python=/mnt/c/Users/remip/Anaconda3/python.exe

output:
		mkdir -p $@

Figs:
		mkdir -p $@

logs:
		mkdir -p $@

#---------------------------------------------------------------------------------------------------
#---------------- Main computation -----------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

#Description of the 1.5 database
#Plot global methane target in 2050 and
#2100 divided by the 2010 methane level
Figs/methane_index_bar_plot.png: Figs compute_methane_change.py
		${launch_python} compute_methane_change.py

#Compute national methane debt based on
# FAOSTAT data between 1961 and 2010
output/FAOSTAT_methane_debt.csv: output compute_methane_debt.py
				${launch_python} compute_methane_debt.py

#Compute national protein production based on
# FAOSTAT data in 2010 to have an allocation rule of methane
output/FAOSTAT_protein_production.csv: output compute_protein_production_ref.py
				${launch_python} compute_protein_production_ref.py

#Compute national methane quota for different rules:
#methane debt, protein production, gdp, population
output/methane_quota.csv:output compute_methane_quota.py output/production_2010.csv output/FAOSTAT_methane_debt.csv output/FAOSTAT_protein_production.csv
				${launch_python} compute_methane_quota.py

# Compute "model" country for intensificaiton pathways
# chosen among "temperate" and "tropical" countries
output/model_countries.csv:output compute_model_countries.py
				${launch_python} compute_model_countries.py

#Compute methane intensity per unit of production in 2050
# for each intensification pathway, with and without mitigation
output/emission_intensity_2050.csv:output compute_methane_intensity_2050.py output/model_countries.csv
				${launch_python} compute_methane_intensity_2050.py

#Without mitigation technologies applied
output/emission_intensity_2050_no_mitigation.csv:output compute_methane_intensity_2050.py output/model_countries.csv
				${launch_python} compute_methane_intensity_2050.py --no-mitigation

#Compute share of each crop whih is domestically produced
# and the share of feed in the total production
output/share_trade_feed.csv:compute_trade_share.py output
				${launch_python} compute_trade_share.py

#Compute national production compatible with national methane quotas
#defined in output/methane_quota.csv
output/activity_2050.csv:output compute_activity_2050.py output/methane_quota.csv output/emission_intensity_2050.csv
				${launch_python} compute_activity_2050.py

#Compute aggregate feed yield with national yield
output/feed_yield_aggregate.csv:compute_feed_yield.py output output/share_trade_feed.csv
					${launch_python} compute_feed_yield.py

#Compute mean grass yield at a national scale based on
# FAOSTAT data
output/grass_yield.csv: output compute_grass_yield.py
				${launch_python} compute_grass_yield.py

#Compute national nitrous oxyde intensity of manure
# and fertilization
output/emission_intensity_N2O.csv: output
				${launch_python} compute_N2O_intensity_2050.py

#Without mitigation technologies applied
output/emission_intensity_N2O_no_mitigation.csv:output compute_N2O_intensity_2050.py output/model_countries.csv
				${launch_python} compute_N2O_intensity_2050.py --no-mitigation

#Compute deforesattion emission factor based on IPCC methodology
# for countries with the highest agricultural exapnsion during these
# last 10 years
output/deforestation_factor.csv: output compute_deforestation_emission_factor.py
				${launch_python} compute_deforestation_emission_factor.py

#Compute impacts of national methane quotas
#on land-use change, CO2 and N2O emissions
output/impact_2050.csv: output compute_impact.py output/feed_yield_aggregate.csv output/activity_2050.csv output/grass_yield.csv output/emission_intensity_N2O.csv output/deforestation_factor.csv
				${launch_python} compute_impact.py

#Without mitigation technologies applied
output/impact_2050_no_mitigation.csv: output compute_impact.py output/feed_yield_aggregate.csv output/activity_2050_no_mitigation.csv output/grass_yield.csv output/emission_intensity_N2O_no_mitigation.csv output/deforestation_factor.csv
				${launch_python} compute_impact.py --no-mitigation

# PLot boxplot of national AFOLU balance following the national
#methane quota
Figs/AFOLU_balance_bar_plot_countries.png: Figs plot_box_plot.py output/impact_2050.csv
				${launch_python} plot_box_plot.py

# Figs/area_national_offset_quota.png: Figs plot_burden_sharing_offset.py compute_production.py output/production_2010.csv
# 				${launch_python} plot_burden_sharing_offset.py

#---------------------------------------------------------------------------------------------------
#---------------- Sensitivity analysis -------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

Figs/AFOLU_balance_bar_plot_countries_yield+50.png: output compute_impact.py plot_box_plot.py output/feed_yield_aggregate.csv output/activity_2050.csv output/grass_yield.csv output/emission_intensity_N2O.csv
				${launch_python} compute_impact.py --sensitivity-analysis=+50
				${launch_python} plot_box_plot.py --sensitivity-analysis=+50

Figs/AFOLU_balance_bar_plot_countries_yield-50.png: output compute_impact.py plot_box_plot.py output/feed_yield_aggregate.csv output/activity_2050.csv output/grass_yield.csv output/emission_intensity_N2O.csv
				${launch_python} compute_impact.py --sensitivity-analysis=-50
				${launch_python} plot_box_plot.py --sensitivity-analysis=-50
