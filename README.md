# How to run
Data should be formatted as a table where the columns are the individual time series and the rows are time points. The time points should be equidistant.
The data can have an arbitrary number of initial columns, which should not be taken into consideration (e.g. for labels). These are specified when calling the program.

To call the ordering algorithms, use:
python3 [two_opt.py, upwards_opt.py] <data_file> <number_of_initial_cols> <target_file>

For example:
python3 two_opt.py datasets/covid.csv 1 datasets/ranks.csv
python3 upwards_opt.py datasets/covid.csv 1 datasets/ranks.csv

The programs will output the ranking as a list to use in software like Tableau. A Tableau file is supplied as an example, using the covid dataset. For converting the table file to a file more suitable for Tableau, a tool for unpivoting the data is also supplied. Usage example:
python3 unpivot.py datasets/covid.csv 1

The weights and variables can be changed in settings.py.
