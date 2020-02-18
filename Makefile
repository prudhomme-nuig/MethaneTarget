#To launch the Makefile:
#Read the README.txt !

launch_python=/mnt/c/Users/remip/Anaconda3/python.exe

output:
		mkdir -p $@

Figs:
		mkdir -p $@

logs:
		mkdir -p $@

Figs/methane_index_bar_plot: Figs compute_methane_change.py
		${launch_python} compute_methane_change.py

Figs/area_national_offset_quota.png: Figs plot_burden_sharing_offset.py compute_production.py output/production_2010.csv
				${launch_python} plot_burden_sharing_offset.py

output/production_2010.csv: output compute_production.py
				${launch_python} compute_production.py

output/feed_yield_aggregate.csv:compute_feed_yield.py output
					${launch_python} compute_feed_yield.py

output/emission_intensity_N2O.csv: output
				${launch_python} compute_N2O_intensity_2050.py

output/methane_quota.csv:output compute_methane_quota.py output/production_2010.csv
				${launch_python} compute_methane_quota.py

output/emission_intensity_2050.csv:output compute_methane_intensity_2050.py
				${launch_python} compute_methane_intensity_2050.py

output/density_cattle.csv:output compute_livestock_density_from_FAO.py
				${launch_python} compute_livestock_density_from_FAO.py

output/activity_2050.csv:output compute_activity_2050.py output/methane_quota.csv output/emission_intensity_2050.csv
				${launch_python} compute_activity_2050.py

output/impact_2050.csv: output compute_impact.py output/feed_yield_aggregate.csv output/activity_2050.csv output/grass_yield.csv
				${launch_python} compute_impact.py

Figs/AFOLU_balance_bar_plot_countries.png: Figs plot_box_plot.py output/impact_2050.csv
				${launch_python} plot_box_plot.py

Figs/AFOLU_balance_bar_plot_countries_yield+50.png: output compute_impact.py plot_box_plot.py output/feed_yield_aggregate.csv output/activity_2050.csv output/grass_yield.csv
				${launch_python} compute_impact.py --sensitivity-analysis=+50
				${launch_python} plot_box_plot.py --sensitivity-analysis=+50

Figs/AFOLU_balance_bar_plot_countries_yield-50.png: output compute_impact.py plot_box_plot.py output/feed_yield_aggregate.csv output/activity_2050.csv output/grass_yield.csv
				${launch_python} compute_impact.py --sensitivity-analysis=-50
				${launch_python} plot_box_plot.py --sensitivity-analysis=-50

output/grass_yield.csv: output compute_grass_yield.py
				${launch_python} compute_grass_yield.py
