import os
import sys
import json
import sqlite3
    
def addState(state):
    global fields
    #Think of the list of combinations as a list of states.
    #Frist make sure it hasn't already been added
    selectQuery = "SELECT COUNT(*) AS Results FROM Population WHERE 1=1"
    for field in state:
        fieldValueIndex = state[field]
        value = fields[field][ fieldValueIndex ]
        selectQuery+=" AND "+str(field)+" = '"+str(value)+"'"
    c.execute(selectQuery)
    results = c.fetchone()
    if results[0]>0:
        return False
    #Prepare an insert with the state.
    populationQuery = " INSERT INTO Population("
    #Add all the fields from the dictionary
    for field in state:
        populationQuery+=field+", "
    #Remove the last comma
    populationQuery=populationQuery.rstrip(", ")
    populationQuery+=")VALUES("
    for field in state:
        fieldValueIndex = state[field]
        item = fields[field][ fieldValueIndex ]
        populationQuery+="'"+str(item)+"', "
    populationQuery=populationQuery.rstrip(", ")
    populationQuery+=");"
    c.execute(populationQuery)
    con.commit()


#Specify database file
databaseFile = '6 - Combinations.sqlite'

#Connect to database
import sqlite3
con = sqlite3.connect(databaseFile)
c = con.cursor()

#Load field list file
fileHandle = open("4 - combinedFieldList.json", "r")
fileContents = fileHandle.read()

#Parse field list file as JSON
jsonObject = json.loads(fileContents)

#Initialize a dictionary and set it to the field list and values from the file
fields = {}

#Populate the dictionary from the object
for k,v in jsonObject.items():
    #Add a null object at the begining of each list
    v.insert(0,'null')
    fields[k]=v

#Check if output tables exist
c.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='Population';")
outputTableExists = c.fetchone()[0]

if outputTableExists >0:
    #print("\nOutput Table Already Exists.")
    pass
else:
    #Make tables to track population sizes if they are not already there. This is our final output data.
    c.execute("CREATE TABLE IF NOT EXISTS Campus (CampusID INTEGER PRIMARY KEY, CampusName text);")
    c.execute("CREATE TABLE IF NOT EXISTS Census (CensusID INTEGER PRIMARY KEY, PopulationID INTEGER, CampusID INTEGER, Fall2014 INTEGER, Fall2015 INTEGER, Fall2016 INTEGER, Fall2017 INTEGER, Fall2018 INTEGER);")
    createPopulation="CREATE TABLE IF NOT EXISTS Population (PopulationID INTEGER PRIMARY KEY, "
    for field in fields:
        createPopulation+=field+" text, "
    createPopulation=createPopulation.rstrip(", ")
    createPopulation+=")";
    c.execute(createPopulation)
    
    #Think of the list of combinations as a list of states.
    #Prepare an initial insert with the first state.
    initialPopulationQuery = " INSERT INTO Population("
    #Add all the fields from the dictionary
    for field in fields:
        initialPopulationQuery+=field+", "
    #Remove the last comma
    initialPopulationQuery=initialPopulationQuery.rstrip(", ")
    initialPopulationQuery+=")VALUES("
    for field in fields:
        firstItem = fields[field][0]
        initialPopulationQuery+="'"+str(firstItem)+"', "
    initialPopulationQuery=initialPopulationQuery.rstrip(", ")
    initialPopulationQuery+=");"
    c.execute(initialPopulationQuery)
    print("\nCreated output table with initial state.")
    con.commit()


#Ok now we are ready to continue or begin the work of populating the list of combinations

#This factor determines how many intersections of identity each population should be limited to.
#Start with one here, then check population sizes using the script for that. 
#Repeat this process with progressively higher complexities until you are not getting any large enough population sizes. 
#This process could be automated, but it would mean making the workload on the scripts incredibly complex and difficult to monitor.
intersectionalComplexity = 1


#find the current state
selectQuery = "SELECT PopulationID,"
for field in fields:
    selectQuery+=str(field)+", "
selectQuery=selectQuery.rstrip(", ")
selectQuery+=" FROM Population ORDER BY 1 ASC LIMIT 1"
print(selectQuery)
c.execute(selectQuery)
results = c.fetchone()
popID = results[0]
i=1 # skip PopulationID
state = {}
for field in fields:
    state[field]=fields[field].index(results[i])
    i+=1


while True:

    #Increment the state
    increment = 1
    intersectionalSum = 0
    
    for field,values in fields.items():
        #If we haven't found a field to increment yet, then let's look for one...
        if(increment>0):
            #If this field is not full, then increment it. (The field counts include a zero-based index)
            if(state[field] < (len(fields[field])-1) ):
                state[field]+=increment
                increment=0
            else:
                state[field]=0

        #If the current field is not blank, then increment the intersectionality sum
        if(state[field] != 0):
            intersectionalSum+=1

    #If there was nothing to add the increment to, then we are done.
    if(increment==1):
        print("Done")
        break
        
    #Now check if this new state is the correct length as specified. If it is, then add it to the database.
    if(intersectionalComplexity == intersectionalSum):
        addState(state)
        print(state)

    
