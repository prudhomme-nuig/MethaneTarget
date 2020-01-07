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
		$launch_python compute_methane_change.py
