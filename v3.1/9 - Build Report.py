import requests
import os
import sys
import json
import sqlite3

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

#Specify database file
databaseFile = '6 - Combinations.sqlite'

#Connect to database
import sqlite3
con = sqlite3.connect(databaseFile)
con.row_factory = dict_factory
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


reportFile = "Report.html"

#Delete the report file if it exists
if os.path.exists(reportFile):
  os.remove(reportFile)
  
#Open a new file for the report
f = open(reportFile,"w+")

#add the header stuff
headers='''<!DOCTYPE html>
<head>
  <title>CJ Trowbridge's Demographic Analysis of the Sierra College Student Body and Its Disparately Impacted Success</title>
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js" integrity="sha384-3ceskX3iaEnIogmQchP8opvBy3Mi7Ce34nWjpBIwVTHfGYWQS9jwHDVRnpKKHJg7" crossorigin="anonymous"></script>
  <script src="https://cdn.datatables.net/1.10.20/js/jquery.dataTables.min.js"></script>
  <link rel="stylesheet" href="https://cdn.datatables.net/1.10.20/css/jquery.dataTables.min.css">
  <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.2.1/css/bootstrap.min.css" integrity="sha384-GJzZqFGwb1QTTN6wy59ffF1BuGJpLSa9DkKMp0DgiMDm4iYMj70gZWKYbI706tWS" crossorigin="anonymous">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.6/umd/popper.min.js" integrity="sha384-wHAiFfRlMFy6i5SRaxvfOCifBUQy1xHdJ/yoi7FRNXMRBu5WHdZYu1hA6ZOblgut" crossorigin="anonymous"></script>
  <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.2.1/js/bootstrap.min.js" integrity="sha384-B0UglyR+jN6CkvvICOB2joaf5I4l3gm9GU6Hc1og6Ls7i6U/mkkaduKaBhlAXv9k" crossorigin="anonymous"></script>
</head>
<body>

<div class="container-fluid">
  <div class="row">
    <div class="col-12">
      <h1 style="white-space: nowrap;"><a style="color: #000; href="https://cjtrowbridge.com">CJ Trowbridge</a></h1>
      <h5><i>Demographic analysis of the Sierra College student body and disparately impacted success.</i></h5>

      <div class="card mb-4">
        <div class="card-body">
          <h5 class="card-title">The Project</h5>
          <div class="card-text">
            
            <p>This project came about as a sociology internship conducted at Sierra College. I had the idea to pursue this analysis after discussing disparately impacted populations in several classes. Professors were aware that some groups are disparately impacted. At some point, I asked what groups are most impacted. Everyone had theories but no one knew the answer. Further investigation led me to realize that there was actually no way to even find the answer because nowhere was the data available in a sortable format.</p>
            <p>The main goal of this project was to create a sortable list which shows demographics and success data. This way, we can see which groups are most impacted, and take appropriate action to support the success of those groups.</p>
          </div><!--End Card-text-->
        </div><!--End Card-body-->
      </div><!--End Card-->

      <div class="card mb-4">
        <div class="card-body">
          <h5 class="card-title">The Data</h5>
          <div class="card-text">
            <p>Success data is shown in green, and for the most recent semester only. The metrics shown are the ones specified by the <a href="https://www.cccco.edu/About-Us/Chancellors-Office/Divisions/College-Finance-and-Facilities-Planning/Student-Centered-Funding-Formula" target="_blank">California Community Colleges Student Centered Funding Formula</a>. (Not all of the CCC-SCFF metrics are currently being reported on the Sierra College website, but all the ones that are being reported have been included in this report.) Previous semesters are also included in the attached database and can be queried. Demographics data is shown in blue, and more data may potentially become available in the future. By default, the data here is sorted by Course Success ascending. This means you are seeing a first page of all the populations with the lowest course success. You may notice trends which already jump out. Several factors are highly significant. All ten of the most impacted groups for this success metric have the same ethnicity, and almost all of them are Former Foster Youth.</p>
            <p>All of this data was pulled directly from the Sierra College public website, and it is accessible <a href="https://www.sierracollege.edu/equity.php" target="_blank">here</a> if you want to look through it in the non-sortable format.</p>
            <p>Data is shown for the Fall 2018 semester. This is the most recent data available at the time this internship project was completed. The data can be updated later by using the <a href="https://github.com/cjtrowbridge/demographic-analysis" target="_blank">published tools</a> which I built in order to create this analysis.</p>
          </div><!--End Card-text-->
        </div><!--End Card-body-->
      </div><!--End Card-->

<div class="table-responsive">
  <table id="populations" class="table">
'''
f.write(headers)

#Create View with final report results
viewQuery = '''
CREATE VIEW IF NOT EXISTS FinalReport AS

SELECT
	`PopulationID`,
	`Ethnicity`,
	`Foster Youth`,
	`Gender`,
	`Low Income`,
	`Disabilities`,
	`Transgender`,
	`Orientation`,
	`Veteran`,
	`Population 17`,
	`Population 18`,
	(`Population 18` - `Population 17`) as 'Population Change',
	`GPA 17`,
	`GPA 18`,
	round(`GPA 18` - `GPA 17`,2) as 'GPA Change',
	`First-Year Eng/Math Completion 17`,
	`First-Year Eng/Math Completion 18`,
	(`First-Year Eng/Math Completion 18` - `First-Year Eng/Math Completion 17`)||"%" as 'Eng/Math Change',
	`Course Success 17`,
	`Course Success 18`,
	(`Course Success 18` - `Course Success 17`)||"%" as 'Course Success Change',
	`Retention 17`,
	`Retention 18`,
	(`Retention 18` - `Retention 17`)||"%" as 'Retention Change'
	
FROM (
    SELECT
        Population.PopulationID,
        Ethnic as 'Ethnicity',
        FFY as 'Foster Youth',
        Gender,
        LowInc as 'Low Income',
        Disabilities,
        Transgender,
        SexOrient as 'Orientation',
        VeteranStatus as Veteran,
        Sum(Census.Fall2017) as 'Population 17',
        Sum(Census.Fall2018) as 'Population 18',
        round(avg(SuccessGPA.Fall2017),2) as 'GPA 17',
        round(avg(SuccessGPA.Fall2018),2) as 'GPA 18',
        (cast(
            round(
                avg(
                    ifnull(SuccessEngMath.Fall2018,0)
                ),0
            ) as int)
            ||"%"
        ) as 'First-Year Eng/Math Completion 17',
        (cast(
            round(
                avg(
                    ifnull(SuccessEngMath.Fall2018,0)
                ),0
            ) as int)
            ||"%"
        ) as 'First-Year Eng/Math Completion 18',
        (cast(
            round(
                avg(
                    ifnull(SuccessCourse.Fall2017,0)
                ),0
            ) as int)
            ||"%"
        ) as 'Course Success 17',
        (cast(
            round(
                avg(
                    ifnull(SuccessCourse.Fall2018,0)
                ),0
            ) as int)
            ||"%"
        ) as 'Course Success 18',
        (cast(
            round(
                avg(
                    ifnull(SuccessRetention.Fall2017,0)
                ),0)
            as int)
            ||"%"
        ) as 'Retention 17',
        (cast(
            round(
                avg(
                    ifnull(SuccessRetention.Fall2018,0)
                ),0)
            as int)
            ||"%"
        ) as 'Retention 18'
        
    FROM Population
    LEFT JOIN Census ON Census.PopulationID = Population.PopulationID
    LEFT JOIN SuccessGPA ON SuccessGPA.PopulationID = Population.PopulationID
    LEFT JOIN SuccessCourse ON SuccessCourse.PopulationID = Population.PopulationID
    LEFT JOIN SuccessRetention ON SuccessRetention.PopulationID = Population.PopulationID
    LEFT JOIN SuccessEngMath ON SuccessEngMath.PopulationID = Population.PopulationID

    WHERE
		SuccessGPA.Fall2017 IS NOT NULL AND
		SuccessGPA.Fall2018 IS NOT NULL /*AND
		SuccessCourse.Fall2017 IS NOT NULL AND
		SuccessCourse.Fall2018 IS NOT NULL AND
		SuccessRetention.Fall2017 IS NOT NULL AND
		SuccessRetention.Fall2018 IS NOT NULL*/

    GROUP BY Population.PopulationID
) x
WHERE 
	x.`Population 18` > 10 AND
	x.`Population 17` > 10
ORDER BY x.`Course Success 18` ASC
'''
c.execute(viewQuery)
con.commit()

reportQuery="SELECT * FROM FinalReport"
columns={}
headersShown = False
c.execute(reportQuery)
for row in c:
    if(headersShown==False):
        headersShown = True
        f.write("    <thead>\n")
        f.write("      <tr>\n")
        i = 0
        for k,v in row.items():
            f.write("        <th>"+str(k)+"</th>\n")
            columns[i]=k
            i+=1
        f.write("      </tr>\n")
        f.write("    </thead>\n")
        f.write("    <tbody>\n")
    f.write("      <tr>\n")
    for k,v in row.items():
        if(v=='null') or (v=='None'):
            value='(blank)'
        else:
            value=v
        f.write("        <td>"+str(value)+"</td>\n")
    f.write("      </tr>\n")

footers='''    </tbody>
    <tfoot>
      <tr>
'''
for k,v in columns.items():
    footers+="        <td>"+str(columns[k])+"</td>\n"
footers+='''
      </tr>
    </tfoot>
  </table>
</div><!--/table-responsive-->
    </div><!--/col-12-->
  </div><!--/row-->
</div><!--/container-->
</body>
<script>
  $(document).ready(function(){
    $('#populations').DataTable({
        "order": [[ 19, "asc" ]],
        columnDefs: [
            {  className: "demographicMetrics", targets: [1,2,3,4,5,6,7,8] },
            {  className: "successMetricsA", targets: [9,10,11,15,16,17,21,22,23] },
            {  className: "successMetricsB", targets: [12,13,14,18,19,20] }
            
        ],
    });
  });
</script>
<style>
    .demographicMetrics{
        background-color: #85e3ff;
    }
    .successMetricsA{
        background-color: #BFFCC6;
    }
    .successMetricsB{
        background-color: #d7fcbf;
    }
</style>
'''

f.write(footers)
f.close()
