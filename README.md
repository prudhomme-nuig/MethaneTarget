# The Methane tool to compute the impact of national biogenic methane quota on the AFOLU sector

This tool support the following scientific article:
http://www.scientific-article-methane

A complete documentation of the computation is provide in this article.
When you use this code, please cite the above mentioned article.

This tool is mainly built on FAOSTAT data. They area provided in the data folder but can be updated at this adress:
http://www.fao.org/faostat/en/#home

This tool will set a quota for methane biogenic emissions from:
1. Enteric fermentation of cattle, sheep and goats
2. Manure management of cattle, sheep and goats, swine and poultry
3. Rice production

## User guide

This tool can be launched from Python3 or an Unix environment

### Python3

This tool can be launched in python. Make sure that the following folders are created in the working directory:
1. Figs/
2. output/

Run the following python files in that order:
1. compute_methane_change.py
2. compute_methane_debt.py
3. compute_protein_production_ref.py
4. compute_methane_quota.py
5. compute_methane_intensity_2050.py
6. compute_activity_2050.py
7. compute_feed_yield.py
8. compute_grass_yield.py
9. compute_N2O_intensity_2050.py
10. compute_impact.py
11. plot_box_plot.py
12. print_table_results.py

A description of the purposes of each python file is provided at the beginning of the file and in the paper.

A virtual environment is provided with the requirement.txt to have the version of the package. To install it, please run:
pip install -r requirements.txt

See documentation for more information about virtual environment:
https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/

### Unix environment

The previous python file can be run in one command line in the shell:

make Figs/AFOLU_balance_bar_plot_countries.png

See Makefile documentation for more information:
https://fr.wikipedia.org/wiki/Make
