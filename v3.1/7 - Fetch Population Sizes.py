import requests
import os
import sys
import json
import sqlite3

def verifyCampus(campus):
    #Check to make sure the given campus is already in the database, otherwise add it and refresh the local list of campuses.
    global campuses
    if campus in campuses.keys():
        return
    else:
        global c
        global con
        sql = "INSERT INTO Campus (CampusName)VALUES('"+str(campus)+"');"
        c.execute(sql)
        con.commit()
        updateCampusList()
        return

def updateCampusList():
    #Refresh the local list of campuses from the database.
    global campuses
    global c
    campuses = {}
    c.execute("SELECT * FROM Campus")
    rows = c.fetchall()
    for row in rows:
        campusID   = row[0]
        campusName = row[1]
        campuses[campusName] = campusID
        campuses[campusID] = campusName

def estimateParentSize(state):
    global fields
    #First make a list of any fields which are not null in this state
    relevant={}
    for k,v in state.items():
        if(v>0):
            relevant[k]=v
    print(relevant)
    population = 0
    #Now recombine them excluding one each time, and find the one with the smallest population.
    for item in relevant:
        sublist = {}
        for k,v in relevant.items():
            if(item!=k):
                sublist[k]=fields[k][v]
        
        estimateQuery='''
            SELECT 
            SUM(
                    IFNULL(Fall2014,0)+
                    IFNULL(Fall2015,0)+
                    IFNULL(Fall2016,0)+
                    IFNULL(Fall2017,0)+
                    IFNULL(Fall2018,0)
            )/5 as 'AveragePopulation'
            FROM Population
            LEFT JOIN Census ON Census.PopulationID = Population.PopulationID
            WHERE
            '''
        for k,v in sublist.items():
            estimateQuery+=str(k)+" LIKE '"+v+"' AND "
        estimateQuery=estimateQuery.rstrip("AND ")
        estimateQuery+='''
            GROUP BY Population.PopulationID
            ORDER BY AveragePopulation DESC
            LIMIT 1
            '''
        c.execute(estimateQuery)
        results = c.fetchone()[0]
        return results

def getCensusData(censusFields, PopulationID):
    global c
    global con
    global fields
    #Fetch the census data for the specified demographic fields.
    ActivityID = 'b5ee06c7-4052-4a59-864e-743f478c3cd5'
    RequestID = '8969ca02-d6c9-bf0c-eac1-75fa922a0ac9'
    
    DatasetID = '"072ba346-ab3e-4a37-9d00-7312faf0be1e"'
    ReportID = '"d5637877-1964-4f87-9ac1-9014a97fd913"'
    ResourceKey = '7a6b0034-25a2-46da-93e0-b6538eb8d447'

    description = ''
    
    headers = {
        'Connection': 'keep-alive',
        'Origin': 'https://app.powerbi.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
        'ActivityId': ActivityID,
        'Accept': 'application/json, text/plain, */*',
        'RequestId': RequestID,
        'X-PowerBI-ResourceKey': ResourceKey,
        'Content-Type': 'application/json;charset=UTF-8',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'cors',
        'Referer': 'https://app.powerbi.com/view?r=eyJrIjoiN2E2YjAwMzQtMjVhMi00NmRhLTkzZTAtYjY1MzhlYjhkNDQ3IiwidCI6ImI4Mjc1Yzg0LWFkOGEtNGViYi04MzZhLWM5ZDdkNDI1NGUzMyIsImMiOjZ9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    data = '{"version":"1.0.0","queries":[{"Query":{"Commands":[{"SemanticQueryDataShapeCommand":{"Query":{"Version":2,"From":[{"Name":"e","Entity":"Enchilada"}],"Select":[{"Column":{"Expression":{"SourceRef":{"Source":"e"}},"Property":"CAMPUS_DESC"},"Name":"Enchilada.CAMPUS_DESC"},{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"e"}},"Property":"UnID"}},"Function":2},"Name":"Count(Enchilada.UnID)"},{"Column":{"Expression":{"SourceRef":{"Source":"e"}},"Property":"TERM_DESC"},"Name":"Enchilada.TERM_DESC"}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"e"}},"Property":"TERM_DESC"}}],"Values":[[{"Literal":{"Value":"\'Fall 2014\'"}}],[{"Literal":{"Value":"\'Fall 2015\'"}}],[{"Literal":{"Value":"\'Fall 2016\'"}}],[{"Literal":{"Value":"\'Fall 2017\'"}}],[{"Literal":{"Value":"\'Fall 2018\'"}}]]}}},{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"e"}},"Property":"CNT_Ret_Den"}}],"Values":[[{"Literal":{"Value":"\'1\'"}}]]}}},'
    for k,v in censusFields.items():
        v = fields[k][v]
        if v != "null":
            description+=str(" "+str(k)+"="+str(v)+", ")
            data+='{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"e"}},"Property":"'+str(k)+'"}}],"Values":[[{"Literal":{"Value":"\''+str(v)+'\'"}}]]}}},'
    data += '{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"e"}},"Property":"Enrolled"}}],"Values":[[{"Literal":{"Value":"1L"}}]]}}}],"OrderBy":[{"Direction":2,"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"e"}},"Property":"CAMPUS_DESC"}}}]},"Binding":{"Primary":{"Groupings":[{"Projections":[0],"Subtotal":1}]},"Secondary":{"Groupings":[{"Projections":[1,2]}]},"DataReduction":{"DataVolume":3,"Primary":{"Window":{"Count":100}},"Secondary":{"Top":{"Count":100}}},"Version":1}}}]},"QueryId":"","ApplicationContext":{"DatasetId":'+DatasetID+',"Sources":[{"ReportId":'+ReportID+'}]}}],"cancelQueries":[],"modelId":2812002}'
    response = requests.post('https://wabi-west-us-api.analysis.windows.net/public/reports/querydata', headers=headers, data=data)
    results = response.json()
    
    values = results['results'][0]['result']['data']['dsr']['DS'][0]['PH'][1]['DM1']

    output = {}

    if(len(values)==0):
        insertQuery = "INSERT INTO Census (PopulationID) VALUES ("+str(PopulationID)+")"
        print(insertQuery)
        c.execute(insertQuery)
        con.commit()
    
    for item in values:
        campus = item['G0']
        
        #verify that the campus is already in the database
        verifyCampus(campus)
        global campuses
        
        terms = item['X']
        insertFields = "PopulationID,CampusID,"
        insertValues = "'"+str(PopulationID)+"','"+str(campuses[campus])+"',"

        print(description)

        if('ValueDicts' in results['results'][0]['result']['data']['dsr']['DS'][0]):
            tableFields = results['results'][0]['result']['data']['dsr']['DS'][0]['ValueDicts']['D0']
            for x in range(len(terms)):
                term = tableFields[x]
                term = term.replace(" ","")
                val = 'null'
                #check if there is a value for this field
                if('M0' in terms[x]):
                    val = terms[x]['M0']

                    insertFields+="'"+str(term)+"',"
                    insertValues+="'"+str(val)+"',"
                print(str(campus)+"/ "+str(term)+": "+str(val))

        insertFields=insertFields.rstrip(",")
        insertValues=insertValues.rstrip(",")
        insertQuery = "INSERT INTO Census ("+insertFields+") VALUES ("+insertValues+")"
        print(insertQuery)
        c.execute(insertQuery)
        con.commit()
        print("")


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

#Declare a dictionary for the campuses and populate it
campuses = {}
updateCampusList()


while True:
    remainingTasks = "SELECT COUNT(*) AS Uncompleted FROM Population WHERE NOT EXISTS(SELECT CensusID FROM Census WHERE Census.PopulationID = Population.PopulationID) ORDER BY 1 ASC LIMIT 1"
    c.execute(remainingTasks)
    results = c.fetchone()
    print("Remaining Tasks: "+str(results[0]))

    #find something to work on
    selectQuery = "SELECT PopulationID, "
    for field in fields:
        selectQuery+=str(field)+", "
    selectQuery=selectQuery.rstrip(", ")
    selectQuery+=" FROM Population WHERE NOT EXISTS(SELECT CensusID FROM Census WHERE Census.PopulationID = Population.PopulationID) ORDER BY 1 ASC LIMIT 1"
    #print(selectQuery)
    c.execute(selectQuery)
    results = c.fetchone()
    if(results is None):
        print("\nDone")
        break

    popID = results[0]
    i=1 # skip PopulationID
    state = {}
    for field in fields:
        state[field]=fields[field].index(results[i])
        i+=1

    #Try to determine if we don't need to check this population, because a less complex version of it is already too small.
    estimateSize = estimateParentSize(state)
    print("Parent size estimated at "+str(estimateSize))
    if(estimateSize>10):
        print("Need to fetch data.")
        #fetch and store the census data for the current state

        try:
            getCensusData(state,popID)
        except:
            print("Caught an error!")
        
    else:
        #Otherwise remove this population from the database
        print("Terminating this line since the population is too small.")
        c.execute("DELETE FROM Population WHERE PopulationID = "+str(popID))
        con.commit()

    
