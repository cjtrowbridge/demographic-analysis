#Declare an array variable containing the name of all the fields on the dashboard
#I got this list from the public website
declare -a arr=( \
"Ethnic" \
"Gender" \
"Disabilities" \
"VeteranStatus" \
"LowInc" \
"FFY" \
"SexOrient" \
"Transgender" \
"GSP" \
"CAFYES" \
"EOPS" \
"CARE" \
"CalWorks" \
"TRIO" \
"RISE" \
"Puente" \
"Umoja"
)

## loop through the above array
for i in "${arr[@]}"
do
	
	#Request the list of values for each field. save them each in their own file

	curl 'https://wabi-west-us-api.analysis.windows.net/public/reports/querydata' \
		-H 'Connection: keep-alive' \
		-H 'Origin: https://app.powerbi.com' \
		-H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36' \
		-H 'ActivityId: 0a88ef7b-922f-4ca6-aa02-acb83dc8ce5e' \
		-H 'Accept: application/json, text/plain, */*' \
		-H 'RequestId: 3c7dda7a-eaea-c1cc-bfa3-e645158a9a75' \
		-H 'X-PowerBI-ResourceKey: 7a6b0034-25a2-46da-93e0-b6538eb8d447' \
		-H 'Content-Type: application/json;charset=UTF-8' \
		-H 'Sec-Fetch-Site: cross-site' \
		-H 'Sec-Fetch-Mode: cors' \
		-H 'Referer: https://app.powerbi.com/view?r=eyJrIjoiN2E2YjAwMzQtMjVhMi00NmRhLTkzZTAtYjY1MzhlYjhkNDQ3IiwidCI6ImI4Mjc1Yzg0LWFkOGEtNGViYi04MzZhLWM5ZDdkNDI1NGUzMyIsImMiOjZ9' \
		-H 'Accept-Encoding: gzip, deflate, br' \
		-H 'Accept-Language: en-US,en;q=0.9' \
		--data-binary '{"version":"1.0.0","queries":[{"Query":{"Commands":[{"SemanticQueryDataShapeCommand":{"Query":{"Version":2,"From":[{"Name":"e","Entity":"Enchilada"}],"Select":[{"Column":{"Expression":{"SourceRef":{"Source":"e"}},"Property":"'"$i"'"},"Name":"Enchilada.'"$i"'"}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"e"}},"Property":"Enrolled"}}],"Values":[[{"Literal":{"Value":"1L"}}]]}}}]},"Binding":{"Primary":{"Groupings":[{"Projections":[0]}]},"DataReduction":{"DataVolume":3,"Primary":{"Window":{}}},"IncludeEmptyGroups":true,"Version":1}}}]},"QueryId":"","ApplicationContext":{"DatasetId":"072ba346-ab3e-4a37-9d00-7312faf0be1e","Sources":[{"ReportId":"d5637877-1964-4f87-9ac1-9014a97fd913"}]}}],"cancelQueries":[],"modelId":2812002}' \
		--compressed > "$i.ugly.json"
		
	#Now make a readable version of each response
	cat "$i.ugly.json" | json_pp > "$i.pretty.json"

done
