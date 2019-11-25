# demographic-analysis
This tool produces ferpa-compliant analyses of demographic data.

This document explains the pieces and steps involved in the example provided. The first script will 
generate a test database full of random demographics data. The second script will analyze that data
and create a report of all demographic permutations where the population size is greater than ten.

1 - populateTestDatabase.py
	This script will create a new sqlite database in the same directory if none exists. Each time the 
	script is run, it will populate the database with random demographics data using the selectable 
	fields and values shown on the equity dashboard.
	
2 - testDatabase.sqlite
	This file will be created by the "1 - populateTestDatabase.py" script. It contains rows of random 
	demographics data with the fields and values shown on the equity dashboard.
	
3 - analyzePopulations.py
	This script will examine the database and determine all unique demographic combinations it contains, 
	then it will count the population size of each combination. Where that population size is greater than 
	ten, that combination will be added to "4 - reportablePopulations.csv"
	
4 - reportablePopulations.csv
	This file contains a list of all demographic permutations where the population size is greater than 
	ten, along with the population size.
	
	
SQLiteDatabaseBrowser.exe
	A portable tool for browsing and exploring the database.
