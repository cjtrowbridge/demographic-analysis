from datetime import datetime, time
import random
import os.path
databaseFile = '2 - testDatabase.sqlite'
numberOfEntriesToCreate = 100000

#Enumerate the list of popssible values for each field
race        = ['Af. Am./ Black', 'Asian', 'Filipino', 'Hisp./Lat.', 'Multi',  'Pac. Is.', 'Unknown', 'White']
gender      = [ 'Female', 'Male']
disability  = [ 'Yes', 'No']
veteran     = ['Yes', 'No']
income      = ['Low', 'Not Low']
foster      = ['Yes', 'No']
orientation = ['Bi', 'Gay', 'Other', 'Straight', 'Declined']
transgender = ['Yes', 'No', 'Declined']

#Connect to database
import sqlite3
con = sqlite3.connect(databaseFile)
c = con.cursor()

#Create table if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS person (
      race text,
      gender text,
      disability text,
      veteran text,
      income text,
      foster text,
      orientation text,
      transgender text
    )''');


#Add the specified number of random demographic entries
print("Begining to write "+str(numberOfEntriesToCreate)+" new random entries to the test database...")
lastUpdated = datetime.now()
for x in range(0,numberOfEntriesToCreate):
    #Select a random value for each field from the list of options
    combinedInsertData = [(
        random.choice(race),
        random.choice(gender),
        random.choice(disability),
        random.choice(veteran),
        random.choice(income),
        random.choice(foster),
        random.choice(orientation),
        random.choice(transgender)
    )]
    
    #Put the random values together into an insert query
    insertQuery = "INSERT INTO person (race,gender,disability,veteran,income,foster,orientation,transgender)values(?,?,?,?,?,?,?,?)"
    try:
        c.executemany(insertQuery,combinedInsertData);
        con.commit()
    except sqlite3.Error as e:
        print("An error occurred: ",e.args[0])

    #Check how long since we updated the user on progress
    elapsed = (datetime.now() - lastUpdated).seconds
    if elapsed > 5:
        #Need to update the user
        percentDone = ((x/numberOfEntriesToCreate)*100);
        print(str(percentDone)+"% Done...")
        lastUpdated = datetime.now()

#Count the records in the database and display the value
c.execute("SELECT COUNT(*) as 'Count' FROM person")
print("Done! There are now "+str(c.fetchone()[0])+" records in the database.")

#Close the database
con.close()
