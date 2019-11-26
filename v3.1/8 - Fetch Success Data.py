import requests
import os
import sys
import json
import sqlite3

def getSuccessData(censusFields, PopulationID):
    global c
    global con
    global fields
    #Fetch the census data for the specified demographic fields.
    
    description = 'Population Description: '

    headers = {
        'Connection': 'keep-alive',
        'Origin': 'https://app.powerbi.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
        'ActivityId': '7f0bfb26-bc30-4995-acc7-c3dc832fa108',
        'Accept': 'application/json, text/plain, */*',
        'RequestId': 'a3065ccb-cc0b-1c17-8b19-f92bf3772cb1',
        'X-PowerBI-ResourceKey': '7a6b0034-25a2-46da-93e0-b6538eb8d447',
        'Content-Type': 'application/json;charset=UTF-8',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'cors',
        'Referer': 'https://app.powerbi.com/view?r=eyJrIjoiN2E2YjAwMzQtMjVhMi00NmRhLTkzZTAtYjY1MzhlYjhkNDQ3IiwidCI6ImI4Mjc1Yzg0LWFkOGEtNGViYi04MzZhLWM5ZDdkNDI1NGUzMyIsImMiOjZ9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    data = '{"version":"1.0.0","queries":[{"Query":{"Commands":[{"SemanticQueryDataShapeCommand":{"Query":{"Version":2,"From":[{"Name":"e","Entity":"Enchilada"}],"Select":[{"Column":{"Expression":{"SourceRef":{"Source":"e"}},"Property":"TERM_DESC"},"Name":"Enchilada.TERM_DESC"},{"Measure":{"Expression":{"SourceRef":{"Source":"e"}},"Property":"GPA"},"Name":"Enchilada.GPA"},{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"e"}},"Property":"Success"}},"Function":1},"Name":"Avg(Enchilada.Success)"},{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"e"}},"Property":"Retention"}},"Function":1},"Name":"Sum(Enchilada.Retention)"}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"e"}},"Property":"TERM_DESC"}}],"Values":[[{"Literal":{"Value":"\'Fall 2013\'"}}],[{"Literal":{"Value":"\'Fall 2015\'"}}],[{"Literal":{"Value":"\'Fall 2016\'"}}],[{"Literal":{"Value":"\'Fall 2017\'"}}],[{"Literal":{"Value":"\'Fall 2018\'"}}]]}}},{"Condition":{"Comparison":{"ComparisonKind":2,"Left":{"Measure":{"Expression":{"SourceRef":{"Source":"e"}},"Property":"ThresholdCheck"}},"Right":{"Literal":{"Value":"10D"}}}},"Target":[{"Column":{"Expression":{"SourceRef":{"Source":"e"}},"Property":"TERM_DESC"}}]},'
    
    for k,v in censusFields.items():
        v = fields[k][v]
        if v != "null":
            description+=str(" "+str(k)+"="+str(v)+", ")
            data+='{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"e"}},"Property":"'+str(k)+'"}}],"Values":[[{"Literal":{"Value":"\''+str(v)+'\'"}}]]}}},'
    data += '{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"e"}},"Property":"Enrolled"}}],"Values":[[{"Literal":{"Value":"1L"}}]]}}}],"OrderBy":[{"Direction":1,"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"e"}},"Property":"TERM_DESC"}}},{"Direction":1,"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"e"}},"Property":"TERM_DESC"}}}]},"Binding":{"Primary":{"Groupings":[{"Projections":[0,1,2,3]}]},"DataReduction":{"DataVolume":4,"Primary":{"Window":{"Count":1000}}},"Version":1}}}]},"QueryId":"","ApplicationContext":{"DatasetId":"072ba346-ab3e-4a37-9d00-7312faf0be1e","Sources":[{"ReportId":"d5637877-1964-4f87-9ac1-9014a97fd913"}]}}],"cancelQueries":[],"modelId":2812002}'

    response = requests.post('https://wabi-west-us-api.analysis.windows.net/public/reports/querydata', headers=headers, data=data)
    results = response.json()
    
    values = results['results'][0]['result']['data']['dsr']['DS'][0]['PH'][0]['DM0']

    output = {}
    tableFields = {}

    print(description)
    #print(results)
    
    if(len(values)==0) or not('ValueDicts' in results['results'][0]['result']['data']['dsr']['DS'][0]):
        GInsertQuery = "INSERT INTO SuccessGPA       (PopulationID, Fall2013, Fall2015, Fall2016, Fall2017, Fall2018) VALUES ('"+str(PopulationID)+"', null, null, null, null, null)"
        CInsertQuery = "INSERT INTO SuccessCourse    (PopulationID, Fall2013, Fall2015, Fall2016, Fall2017, Fall2018) VALUES ('"+str(PopulationID)+"', null, null, null, null, null)"
        RInsertQuery = "INSERT INTO SuccessRetention (PopulationID, Fall2013, Fall2015, Fall2016, Fall2017, Fall2018) VALUES ('"+str(PopulationID)+"', null, null, null, null, null)"
        
        c.execute(GInsertQuery)
        c.execute(CInsertQuery)
        c.execute(RInsertQuery)
        con.commit()
        return False


    fieldResults = results['results'][0]['result']['data']['dsr']['DS'][0]['ValueDicts']['D0']
    i = 0
    for value in fieldResults:
        tableFields[i] = value.replace(" ","")
        i+=1


    #print(fields)
    
    SuccessG = {'Fall2013': 'null', 'Fall2015': 'null', 'Fall2016': 'null', 'Fall2017': 'null', 'Fall2018': 'null'} #GPA
    SuccessC = {'Fall2013': 'null', 'Fall2015': 'null', 'Fall2016': 'null', 'Fall2017': 'null', 'Fall2018': 'null'} #Course Success
    SuccessR = {'Fall2013': 'null', 'Fall2015': 'null', 'Fall2016': 'null', 'Fall2017': 'null', 'Fall2018': 'null'} #Retention

    
    

    i = 0
    for item in values:
        item = item['C']
        index = tableFields[i]
        if(len(item)>1):
            SuccessG[index] = item[1]
        if(len(item)>2):
            SuccessC[index] = item[2]
        if(len(item)>3):
            SuccessR[index] = item[3]
        i+=1

    #print(SuccessG)
    #print(SuccessC)
    #print(SuccessR)

    GInsertQuery = "INSERT INTO SuccessGPA       (PopulationID, Fall2013, Fall2015, Fall2016, Fall2017, Fall2018) VALUES ('"+str(PopulationID)+"', '"+str(SuccessG['Fall2013'])+"', '"+str(SuccessG['Fall2015'])+"', '"+str(SuccessG['Fall2016'])+"', '"+str(SuccessG['Fall2017'])+"', '"+str(SuccessG['Fall2018'])+"')"
    CInsertQuery = "INSERT INTO SuccessCourse    (PopulationID, Fall2013, Fall2015, Fall2016, Fall2017, Fall2018) VALUES ('"+str(PopulationID)+"', '"+str(SuccessC['Fall2013'])+"', '"+str(SuccessC['Fall2015'])+"', '"+str(SuccessC['Fall2016'])+"', '"+str(SuccessC['Fall2017'])+"', '"+str(SuccessC['Fall2018'])+"')"
    RInsertQuery = "INSERT INTO SuccessRetention (PopulationID, Fall2013, Fall2015, Fall2016, Fall2017, Fall2018) VALUES ('"+str(PopulationID)+"', '"+str(SuccessR['Fall2013'])+"', '"+str(SuccessR['Fall2015'])+"', '"+str(SuccessR['Fall2016'])+"', '"+str(SuccessR['Fall2017'])+"', '"+str(SuccessR['Fall2018'])+"')"

    GInsertQuery = GInsertQuery.replace("'null'","null")
    CInsertQuery = CInsertQuery.replace("'null'","null")
    RInsertQuery = RInsertQuery.replace("'null'","null")

    print(GInsertQuery)
    print(CInsertQuery)
    print(RInsertQuery)
    
    c.execute(GInsertQuery)
    c.execute(CInsertQuery)
    c.execute(RInsertQuery)
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

#Make sure the success table exists in the database
#c.execute('CREATE TABLE IF NOT EXISTS "Success" ("SuccessID" INTEGER PRIMARY KEY AUTOINCREMENT, "PopulationID" INTEGER, "EarnedDegree" INTEGER, "Transfers" INTEGER, "CompleteMathEng" INTEGER, "Complete30Units" INTEGER);')
c.execute('CREATE TABLE IF NOT EXISTS "SuccessGPA" ("SuccessGPAID" INTEGER PRIMARY KEY AUTOINCREMENT,"PopulationID" INTEGER,"Fall2013" REAL,"Fall2014" REAL,"Fall2015" REAL,"Fall2016" REAL,"Fall2017" REAL,"Fall2018" REAL);')
c.execute('CREATE TABLE IF NOT EXISTS "SuccessRetention" ("SuccessRetentionID" INTEGER PRIMARY KEY AUTOINCREMENT,"PopulationID" INTEGER,"Fall2013" REAL,"Fall2014" REAL,"Fall2015" REAL,"Fall2016" REAL,"Fall2017" REAL,"Fall2018" REAL);')
c.execute('CREATE TABLE IF NOT EXISTS "SuccessCourse" ("SuccessCourseID" INTEGER PRIMARY KEY AUTOINCREMENT,"PopulationID" INTEGER,"Fall2013" REAL,"Fall2014" REAL,"Fall2015" REAL,"Fall2016" REAL,"Fall2017" REAL,"Fall2018" REAL);')
c.execute('CREATE INDEX IF NOT EXISTS "SuccessGPAPopulation" ON "SuccessGPA" ("PopulationID");')
c.execute('CREATE INDEX IF NOT EXISTS "SuccessRetentionPopulation" ON "SuccessRetention" ("PopulationID");')
c.execute('CREATE INDEX IF NOT EXISTS "SuccessCoursePopulation" ON "SuccessCourse" ("PopulationID");')

con.commit()

while True:
    remainingTasks = "SELECT COUNT(*) AS Uncompleted FROM Population WHERE NOT EXISTS(SELECT SuccessGPAID FROM SuccessGPA WHERE SuccessGPA.PopulationID = Population.PopulationID) ORDER BY 1 ASC LIMIT 1"
    c.execute(remainingTasks)
    results = c.fetchone()
    print("Remaining Tasks: "+str(results[0]))

    #find something to work on
    selectQuery = "SELECT PopulationID, "
    for field in fields:
        selectQuery+=str(field)+", "
    selectQuery=selectQuery.rstrip(", ")
    selectQuery+=" FROM Population WHERE NOT EXISTS(SELECT SuccessGPAID FROM SuccessGPA WHERE SuccessGPA.PopulationID = Population.PopulationID) ORDER BY 1 ASC LIMIT 1"
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

    #fetch and store the success data for the current population
    results = getSuccessData(state,popID)    
