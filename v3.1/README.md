# Version 3.1
## Final Version
  
1 - Scrape.sh  
This file scrapes the list of possible values for the fields on the dashboard.  
  
3 - Extract Field Values.py  
This file extracts the values from the scrapes and puts them into a pretty json file for later use.  
  
4 - combinedFieldList.json  
This file contains the list of fields and their possible values.  
  
5 - Find Combinations.py  
This file combines the list of possible field values to the degree of complexity specified in the file. (Start with 1)  
  
6 - Combinations.sqlite  
This database file contains the combinations, the census values, and the success data.  
  
7 - Fetch Population Sizes.py  
This file fetches the population size for each combination in the database. It also attempts to estimate when sizes will fall below ten, and skip those. This greatly reduces the amount of work that needs to be done to compile the data.  
  
8 - Fetch Success Data.py  
This file fetches the success metrics for each population once its size is confirmed as greater than ten.  
  
9 - Build Report.py  
This file will extract all the values from the database and create a final report file which contains the results of the project.  
  
Report.html  
This file is the final report of the project, containing all the success data for all the populations in a searchable, sortable format.  
