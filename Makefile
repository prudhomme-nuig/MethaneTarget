#To launch the Makefile:
#Read the README.md

#To be changed depending on the localization of your python folder
launch_python=python.exe

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

# #Compute national methane debt based on
# # FAOSTAT data between 1961 and 2010
# output/FAOSTAT_methane_debt.csv: output compute_methane_debt.py
# 				${launch_python} compute_methane_debt.py

#Compute national protein production based on
# FAOSTAT data in 2010 to have an allocation rule of methane
output/FAOSTAT_protein_production.csv: output compute_protein_production_ref.py
				${launch_python} compute_protein_production_ref.py

#Compute national methane quota for different rules:
#methane debt, protein production, gdp, population
output/methane_quota.csv:output compute_methane_quota.py output/production_2010.csv output/FAOSTAT_protein_production.csv
				${launch_python} compute_methane_quota.py

#Compute emission intensity and yield for intensification pathways
output/coefficients_milk_yield_concentrate_relation.csv:
				Rscript.exe fit_carcass_yield_intake_relation_non_dairy.R
				Rscript.exe fit_carcass_yield_intake_relation_poultry.R
				Rscript.exe fit_carcass_yield_poultry_relations.R
				Rscript.exe fit_carcass_yield_swine_relations.R
				Rscript.exe fit_methane_intensity_intake_relation_dairy.R
				Rscript.exe fit_methane_intensity_intake_relation_non_dairy.R
				Rscript.exe fit_milk_yield_relations.R

#Compute methane intensity per unit of production in 2050
# for each intensification pathway, with and without mitigation
output/emission_intensity_2050.csv:output compute_methane_intensity_2050.py
				${launch_python} compute_methane_intensity_2050.py

#Compute share of each crop whih is domestically produced
# and the share of feed in the total production
output/share_trade_feed.csv:compute_trade_share.py output
				${launch_python} compute_trade_share.py

#Compute national production compatible with national methane quotas
#defined in output/methane_quota.csv
output/activity_2050.csv:output compute_activity_2050.py output/methane_quota.csv output/emission_intensity_2050.csv output/emission_intensity_2050_no_mitigation.csv
				${launch_python} compute_activity_2050.py

#Compute aggregate feed yield with national yield
output/feed_yield_aggregate.csv:compute_feed_yield.py output output/share_trade_feed.csv logs
					${launch_python} compute_feed_yield.py > logs/compute_feed_yield.log

#Compute mean grass yield at a national scale based on
# FAOSTAT data
output/grass_yield.csv: output compute_grass_yield.py
				${launch_python} compute_grass_yield.py

#Compute national nitrous oxyde intensity of manure
# and fertilization
output/emission_intensity_N2O.csv: output
				${launch_python} compute_N2O_intensity_2050.py

#Compute deforesattion emission factor based on IPCC methodology
# for countries with the highest agricultural exapnsion during these
# last 10 years
output/deforestation_factor.csv: output compute_deforestation_emission_factor.py
				${launch_python} compute_deforestation_emission_factor.py

#Compute impacts of national methane quotas
#on land-use change, CO2 and N2O emissions
output/impact_2050.csv: output compute_impact.py output/feed_yield_aggregate.csv output/activity_2050.csv output/grass_yield.csv output/emission_intensity_N2O.csv output/deforestation_factor.csv common_methane.py check_area.py
				${launch_python} compute_impact.py --print-table
				${launch_python} check_area.py --print-table

#Compute AFOLU balance
output/AFOLU_balance_2050.csv: output compute_AFOLU_balance.py common_methane.py output/impact_2050.csv
				${launch_python} compute_AFOLU_balance.py --print-table

# PLot boxplot of national AFOLU balance following the national
#methane quota
Figs/AFOLU_bar_plot.png: Figs plot_box_plot.py output/AFOLU_balance_2050.csv
				${launch_python} plot_box_plot.py

# Figs/area_national_offset_quota.png: Figs plot_burden_sharing_offset.py compute_production.py output/production_2010.csv
# 				${launch_python} plot_burden_sharing_offset.py

#---------------------------------------------------------------------------------------------------
#---------------- Sensitivity analysis -------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

# #No mitigation
# output/AFOLU_balance_2050_no_mitigation.csv: output compute_impact.py compute_AFOLU_balance.py output/feed_yield_aggregate.csv output/grass_yield.csv output/deforestation_factor.csv common_methane.py
# 				${launch_python} compute_N2O_intensity_2050.py --no-mitigation
# 				${launch_python} compute_methane_intensity_2050.py --no-mitigation --print-table
# 				${launch_python} compute_activity_2050.py --no-mitigation
# 				${launch_python} compute_impact.py --no-mitigation --print-table
# 				${launch_python} check_area.py --no-mitigation --print-table
# 				${launch_python} compute_AFOLU_balance.py --no-mitigation --print-table

#+50% mitigation
output/AFOLU_balance_2050_mitigation-50.csv: output compute_impact.py output/feed_yield_aggregate.csv output/activity_2050_no_mitigation.csv output/grass_yield.csv output/emission_intensity_N2O_no_mitigation.csv output/deforestation_factor.csv common_methane.py
				${launch_python} compute_N2O_intensity_2050.py --mitigation=-50
				${launch_python} compute_methane_intensity_2050.py --mitigation=-50 --print-table
				${launch_python} compute_activity_2050.py --mitigation=-50
				${launch_python} compute_impact.py --mitigation=-50 --print-table
				${launch_python} check_area.py --mitigation=-50 --print-table
				${launch_python} compute_AFOLU_balance.py --mitigation=-50 --print-table

#Yield increase of 50%
output/AFOLU_balance_2050_yield+50.csv: output compute_impact.py compute_AFOLU_balance.py output/feed_yield_aggregate.csv output/activity_2050.csv output/grass_yield.csv output/emission_intensity_N2O.csv
				${launch_python} compute_impact.py --sensitivity-analysis=+50 --print-table
				${launch_python} check_area.py --sensitivity-analysis=+50 --print-table
				${launch_python} compute_AFOLU_balance.py --sensitivity-analysis=+50 --print-table

#Yield decrease of 50%
output/AFOLU_balance_2050_yield-50.csv: output compute_impact.py compute_AFOLU_balance.py output/feed_yield_aggregate.csv output/activity_2050.csv output/grass_yield.csv output/emission_intensity_N2O.csv
				${launch_python} compute_impact.py --sensitivity-analysis=-50 --print-table
				${launch_python} check_area.py --sensitivity-analysis=-50 --print-table
				${launch_python} compute_AFOLU_balance.py --sensitivity-analysis=-50 --print-table

#Forest growth rate decrease of 50%
output/AFOLU_balance_2050_carbon-50.csv: output compute_impact.py compute_AFOLU_balance.py output/activity_2050.csv
				${launch_python} compute_deforestation_emission_factor.py --sensitivity=-50
				${launch_python} compute_impact.py --carbon=-50 --print-table
				${launch_python} check_area.py --carbon=-50 --print-table
				${launch_python} compute_AFOLU_balance.py --carbon=-50 --print-table

#Forest growth rate increase of 50%
output/AFOLU_balance_2050_carbon+50.csv: output compute_impact.py compute_AFOLU_balance.py output/activity_2050.csv
				${launch_python} compute_deforestation_emission_factor.py --sensitivity=+50
				${launch_python} compute_impact.py --carbon=+50 --print-table
				${launch_python} check_area.py --carbon=+50 --print-table
				${launch_python} compute_AFOLU_balance.py --carbon=+50 --print-table

#Output table and perform statistical test
output/sensitivity_analysis.csv: output output/AFOLU_balance_2050_mitigation-50.csv output/AFOLU_balance_2050_yield+50.csv output/AFOLU_balance_2050_yield-50.csv output/AFOLU_balance_2050_carbon+50.csv output/AFOLU_balance_2050_carbon-50.csv
				${launch_python} sensitivity_analysis.py
