# Author : Vikram Fernandes

import requests
import json

ovgdToken = None
# Login parameters
ovgdHost = ''
ovgdUser = ''
ovgdPass = ''


def getCall(headers, uri):
    resp = None
    try:
        resp = requests.get(uri,headers=headers, verify=False)
        if (resp.status_code == 200):
            print("OVGD Get : {} ..... Passed".format(uri))            
        else:
            print("OVGD Get call ..... Failed")
    except Exception as e:
            print("Unable to reach OVGD. Reason  - {}.".format(e))
            print("OVGD Get call ..... Failed")
    
    return resp.json()


def postCall(headers, uri, body):
    resp = None 
    try:
        resp = requests.post(uri, headers=headers, data=json.dumps(body), verify=False)
        if (resp.status_code == 200) or (resp.status_code == 201):
            print("OVGD Connection ..... Passed")            
        else:
            print("OVGD Connection ..... Failed")
    except Exception as e:
            print("Unable to reach OVGD. Reason  - {}.".format(e))
            print("OVGD Connection ..... Failed")
    
    return resp.json()


req_url = "https://{}/rest/login-sessions".format(ovgdHost)    
headers = { 'Content-Type': 'application/json', 'X-Api-Version': '2' }    
body = { 'authLoginDomain': "local", 'userName': ovgdUser, 'password': ovgdPass }

resp_dict = postCall(headers,req_url,body)
ovgdToken = resp_dict["token"]

# Get the list of report templates
headers_with_auth = { 'Content-Type': 'application/json', 'X-Api-Version': '2', 'auth': ovgdToken }
alertURL = "https://{}/rest/global/reporttemplates".format(ovgdHost)

retResp = getCall(headers_with_auth,alertURL)

reportUri = None
for resp in retResp['members']:
    if resp['label'] == 'Remote Support Service Events':
        print("{} : {}".format(resp['label'],resp['uri']))    
        reportUri = resp['uri']
        break
    else:
        continue

# Perform POST to execute the report
reportBody= { 'templateid' : reportUri }
print ("POST {}".format(reportBody))
postReportUrl = "https://{}/rest/global/reportresults".format(ovgdHost)
retResp = postCall(headers_with_auth,postReportUrl,reportBody)

# Perform a Get on the report results - previous call will return a 201
print ("Result set = {}".format(retResp['uri']))
respReportResultsUrl = "https://{}{}".format(ovgdHost,retResp['uri'])
# final Get to get the results from the report results
finalResp = getCall(headers_with_auth,respReportResultsUrl)

# Obtain the report section within the Report
dataDict = None
for rowsResp in finalResp['reportresult']['results']:
    if len(rowsResp['columnSize']) > 2:
        # process the data column
        dataDict = rowsResp['data']
        break

# Process Data set
print("Number of Rows : {}".format(len(dataDict)))

# Process header and data rows
index = 0
finalArray = []
columnArray = []
columnCount = 0
for dataRow in dataDict:
    # Processing header row
    if index == 0:
        columnCount = len(dataRow)
        for column in dataRow:
            col = column['value'].replace(' ','')
            columnArray.append(col)
        index = index + 1
    else:
        # Processing data rows      
        idx = 0
        tmpDict = {}
        tmpArray = []
        for data in dataRow:            
            tmpDict[columnArray[idx]] = data['value']
            idx = idx + 1            
        finalArray.append(tmpDict)

# print just the column
print ("Processed rows : {}".format(len(finalArray)))
print(json.dumps(finalArray,indent=4))

# Process further - This time traverse through the dict to 
# return identifying URI data for additional information that is needed
for rows in finalArray:
    uri = "https://{}/rest/{}?query=name='{}'".format(ovgdHost,rows['ResourceType'],rows['ResourceName'])
    print("URI : {}".format(uri))
    # perform a get to get a unique row for additional details
    # to correlate with URI for mapping










