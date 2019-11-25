import os
import sys
import ntpath
import json

#initialize a json array for the files in the current directory
jsonFiles = []

#initialize an array for the output values
output = {}

#initialize output file string so it has the right scope
outputFile = ""


for file in os.listdir():
    if file.endswith('.json'):
        jsonFiles.append(file)

print(jsonFiles)

#droppedFiles = [r"C:\Users\cj\Desktop\Internship\1 - Find Field Values\SexOrient.pretty.json"]

#loop through all json files in the same directory
for droppedFile in jsonFiles:

    file = ntpath.basename(droppedFile)
    field = file.replace(".pretty.json","")
    outputFile = "combinedFieldList.json"
    
    #initialize this field in the output object
    output[field]=[]

    print("Input File: "+str(file))
    print("Input Field: "+str(field))

    #Load File
    fileHandle = open(droppedFile, "r")
    fileContents = fileHandle.read()

    #Parse as JSON
    jsonObject = json.loads(fileContents)
    
    # the result is a Python dictionary:
    values = jsonObject["results"][0]['result']['data']['dsr']['DS'][0]['PH'][0]['DM0']
    for value in values:
            #output.append(value['G0'])
            output[field].append(value['G0'])

#if len(sys.argv) > 1:
#    with open(newFile, 'w') as outfile:
#        json.dump(output, outfile, indent=4)
#else:
#    print("drop files onto this script to extract their fields and values")


with open(outputFile, 'w') as outfile:
    json.dump(output, outfile, indent=4)

pause = input("Press the <ENTER> key to continue...")
