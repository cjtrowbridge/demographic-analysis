#Note this is a proof of concept so I am assuming the field names and distinct field values are safe.
#An actual implementation will need to take this into account.

databaseFile = '2 - testDatabase.sqlite'

#Connect to database
import sqlite3
con = sqlite3.connect(databaseFile)
c = con.cursor()

#Specficy the table or view name which we are analyzing and where to put the results
inputTable = "person";
outputTable = "populations";

#Create a dictionary containing all the database fields we will look at, as well as an indexed list.

fields = dict()
fieldNames = []
fieldCounts = dict()

#Query the table for a list of fields. This will be different depending on the database engine
print("\nFinding Fields...")
c.execute("PRAGMA table_info("+inputTable+")")
for result in c.fetchall():
    #We need to initialize and empty list for each field, but we also need to include a false or "skip" value.
    #This way, when we calculate combinations, we can calculate partial combinations as well.
    field = result[1]
    fields[field]=['null']
    fieldNames.append(result[1])
    print("Added Field: "+field)


#For each field, find all distinct values in the database and add them to the list for that field.
print("\nFinding Distinct Values For Each Field...")
for field in fields:
    c.execute("SELECT DISTINCT "+field+" FROM person")
    for result in c.fetchall():
        #add the distinct value into the list for this field
        fields[field].append(result[0])
    fieldCounts[field] = len(fields[field])

#Output the results
for field in fields:
    print(field+": ",fields[field])

#Find out how many combinations there are
combinations = 1
for field in fields:
    combinations = combinations * fieldCounts[field]

#Output the data
print("\nCalculating Combinations...\nThere are "+str(combinations)+ " combinations.")

#Check if table exists
c.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='"+outputTable+"';")
outputTableExists = c.fetchone()[0]

if outputTableExists >0:
    print("\nOutput Table Already Exists.")
else:
    #Make a table to track population sizes if there is not already one. This is our final output data.
    print("\nCreated output table with initial state.")
    createQuery="CREATE TABLE IF NOT EXISTS "+outputTable+" ("
    for field in fieldNames:
        createQuery+=field+" text, "
    createQuery+=" populationSize int)";
    
    c.execute(createQuery)
    
    #Think of the list of combinations as a list of states.
    #Prepare an initial insert with the first state.
    initialQuery = " INSERT INTO "+outputTable+"("
    #Add all the fields from the dictionary
    for field in fields:
        initialQuery+=field+", "
    #Remove the last comma
    initialQuery=initialQuery.rstrip(", ")
    initialQuery+=")VALUES("
    for field in fields:
        firstItem = fields[field][0]
        initialQuery+="'"+str(firstItem)+"', "
    initialQuery=initialQuery.rstrip(", ")
    initialQuery+=");"
    print(initialQuery)
    c.execute(initialQuery)
    con.commit()

    #Keep in mind this initial state will be "skip everything." so we don't need to run any queries for the initial state.


#This loop controls the actual workload.
while True:

    print("\nFinding State...")
        
    #The work now has a state. Find it.
    #Query the database for its most recent row.
    #In order to be certain that we are matching values to the correct field, we have to use the indexed list of
    # field names to create the query, and then again to parse the query. This would be less complex in a language
    # which uses associative arrays to return query results.

    query = "SELECT "
    for field in fieldNames:
        query+=field+", "
    #Remove the last comma
    query=query.rstrip(", ")
    query+= " FROM "+outputTable+" ORDER BY rowid DESC LIMIT 1"
    c.execute(query)
        
    lastRow = c.fetchone()

    #Create an object to hold the state
    state = dict()
    for field in fieldNames:
        #Find which result column from the query relates to this field
        fieldPosition = fieldNames.index(field)
        #Find the value from the row of results matches this field
        value = lastRow[fieldPosition]
        #If the value returned from the database is null, python will report it as "None" so change it back.
        if value==None:
            value="null"
        #Find the index of the list of distinct values which matches this value
        valueIndex = fields[field].index(value)
        #Now assign that index to the state object under this field name.
        state[field]= valueIndex

    #Print the output, showing the last completed state
    print("\nLast Completed State")
    for field in state:
        print(str(field)+": "+str(state[field]+1)+"/"+str(fieldCounts[field]))
        
    #Now that we know the last state, we need to increment it to find what we need to work on next.
    print("Increment the state...")
    increment = 1
    for field in state:
        #If we haven't found something to increment yet then keep going
        if increment > 0:
            #If this field is not full, then add one to it (The field counts include a zero-based index)
            if state[field] < (fieldCounts[field]-1):
                state[field]+=increment
                increment = 0
            else:
                #If it is full, then set it to zero and move on to the next field
                state[field]=0
    if increment == 1:
        #If none of the fields could be incremented, then we are done.
        print('Done')
        exit()
        
    print("\nNew State")
    for field in state:
        print(str(field)+": "+str(state[field])+"/"+str(fieldCounts[field]))
        
    #Build a query to find the size of the population for the combination which reflects the new state.
    query = "SELECT COUNT(*) FROM "+inputTable+" WHERE \n"
    for field in state:
        value = fields[field][state[field]]
        if value != 'null':
            query+= " "+field+" LIKE '"+value+"' AND "
    #Remove the last comma
    query=query.rstrip("AND ")
    #Execute the query to find the size of this population
    c.execute(query)
    result = c.fetchone()
    populationSize = result[0]

    print("\nFound "+str(populationSize))

    #Now we need to insert this into the output table
    query = "INSERT INTO "+outputTable+" ("
    for field in state:
        query+=field+", "
    query+="populationSize)values("
    for field in state:
        value = fields[field][state[field]]
        if value=='null':
            query+= "null,"
        else:
            query+= "'"+value+"',"
    query+=str(populationSize)
    query+=")"
    c.execute(query)
    con.commit()
