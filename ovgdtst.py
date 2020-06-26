# Author : Vikram Fernandes

import requests
import json
from tabulate import tabulate

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ovgdToken = None

# Login parameters -- PLEASE ADD YOUR CREDS TO OVGD HERE
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

# Get the list of appliances
headers_with_auth = { 'Content-Type': 'application/json', 'X-Api-Version': '2', 'auth': ovgdToken }
alertURL = "https://{}/rest/appliances".format(ovgdHost)

retResp = getCall(headers_with_auth,alertURL)

appliances = []

for appliance in retResp['members']:
    #print("{} - {} - {} - {}".format(appliance['name'],appliance['applianceLocation'],appliance['id'],appliance['applianceUri']))
    dataDict = None
    dataDict = {
        'name' : appliance['name'],
        'applianceLocation' : appliance['applianceLocation'],
        'applianceUri' : appliance['applianceUri']
        }
    appliances.append(dataDict)

index = 0
for app in appliances:
    req_url = "https://{}{}/sso".format(ovgdHost,app['applianceUri'])

    retRespSso = getCall(headers_with_auth,req_url)    

    if 'sessionId' in retRespSso:
        if retRespSso['sessionId'] != None:
            appliances[index]['sessionId'] = retRespSso['sessionId']
    
    index = index + 1

#print(json.dumps(appliances, indent=4))
print('\n',tabulate(appliances,headers='keys',showindex=True),'\n')

alerts = []
for ov in appliances:
    req_url = "https://{}/rest/version".format(ov['applianceLocation'])
    headers_without_auth = { 'Content-Type': 'application/json' }

    retResp = getCall(headers_without_auth, req_url)

    version = retResp['currentVersion']

    req_url = "https://{}/rest/alerts".format(ov['applianceLocation']) + "?query=\"severity NE 'Critical'\""
    headers = { 'Content-Type': 'application/json', 'X-Api-Version': str(version), 'auth': ov['sessionId'] }

    retResp = getCall(headers, req_url)

    for resp in retResp['members']:
        alert = { 
            'severity' : resp['severity'],
            'description' : resp['description'],
            'correctiveAction' : resp['correctiveAction'],
            'alertState' : resp['alertState'],
            'healthCategory' : resp['healthCategory'],
            'uri' : resp['uri']
        }
        alerts.append(alert)

print ("\nAlerts found : {}".format(len(alerts)))
print('\n',tabulate(alerts,headers='keys',showindex=True))
#print(json.dumps(alerts, indent=4))       








    










