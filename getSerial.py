import sys
import os
import argparse
import requests
import json
import urllib3

# Supress warnings since this script does not handle certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ovgdToken = None
# Login parameters
global ovgdHost
global ovgdUser
global ovgdPass
global serialNumber

# HTTP GET request
def getCall(headers, uri):
    resp = None
    try:
        resp = requests.get(uri,headers=headers, verify=False)
        #if (resp.status_code == 200):
        #    print("OVGD Get : {} ..... Passed".format(uri))            
        #else:
        #    print("OVGD Get call ..... Failed")
    except Exception as e:
            print("Unable to reach OVGD. Reason  - {}.".format(e))
            print("OVGD Get call ..... Failed")
    
    return resp.json()

# HTTP POST request
def postCall(headers, uri, body):
    resp = None 
    try:
        resp = requests.post(uri, headers=headers, data=json.dumps(body), verify=False)
        #if (resp.status_code == 200) or (resp.status_code == 201):
        #    print("OVGD POST ..... Passed")            
        #else:
        #    print("OVGD POST ..... Failed")
    except Exception as e:
            print("Unable to reach OVGD. Reason  - {}.".format(e))
            print("OVGD POST ..... Failed")
    
    return resp.json()

def obtainCreds():
    # Ensure that all the config variables are exported to env.   
    global ovgdHost
    global ovgdUser
    global ovgdPass 
          
    ovgdHost = os.environ.get('OVGD_HOST')
    ovgdUser = os.environ.get('OVGD_USER')
    ovgdPass = os.environ.get('OVGD_PASS')

    if ovgdHost is None or "":
        print('OVGD_HOST environment variable not set')
        return -1
        
    if ovgdUser is None or "":
        print('OVGD_USER environment variable not set')
        return -1
        
    if ovgdPass is None or "":
        print('OVGD_PASS environment variable not set')
        return -1

def getArgument():
    # Verify the arguments passed in    
    parser = argparse.ArgumentParser(add_help=True, description='Usage')
    parser.add_argument('-s', '--serialNumber', dest='vSerial', required=True, help='Virtual Serial Number')
    
    serialNo = parser.parse_args()   

    if serialNo.vSerial[0] != 'V':
        print("Serial Number is not Virtual")
        return None
    else:
        return serialNo.vSerial
  
# Main module
def main():
    global serialNumber
    global ovgdHost
    global ovgdUser
    global ovgdPass 

    serialNumber = ""

    if obtainCreds() == -1:
        print("Environment variables unavailable")
        return -1    

    vSerial = getArgument()

    if vSerial is None or "":
        #print("No Virtual serial number specified")
        return -1
    
    # Login to the OneView Global Dashboard environment
    req_url = "https://{}/rest/login-sessions".format(ovgdHost)    
    headers = { 'Content-Type': 'application/json', 'X-Api-Version': '2' }    
    body = { 'authLoginDomain': "local", 'userName': ovgdUser, 'password': ovgdPass }

    resp_dict = postCall(headers,req_url,body)
    ovgdToken = resp_dict["token"]

    # Query for the virtual serial number within Server Profiles
    headers_with_auth = { 'Content-Type': 'application/json', 'X-Api-Version': '2', 'auth': ovgdToken }
    alertURL = "https://{}/rest/server-profiles?query=\"serialNumber EQ '{}'\"".format(ovgdHost,vSerial)

    retResp = getCall(headers_with_auth,alertURL)
   
    if (('count' in retResp) and (retResp['count'] > 0)):
        #print(json.dumps(retResp,indent=4))        
        uri = retResp['members'][0]['serverHardwareUri']
        uuid = uri.partition('/rest/server-hardware/')[2]

        # Query for the server hardware tied to the server profile
        hwURL = "https://{}/rest/server-hardware?query=\"uuid EQ '{}'\"".format(ovgdHost,uuid)

        retResp = getCall(headers_with_auth,hwURL)

        if (('count' in retResp) and (retResp['count'] > 0)):
            serialNumber = retResp['members'][0]['serialNumber']
            #print ("H/W Serial Number : {} for Virtual serial : {}".format(serialNumber,vSerial))
        #else:
            #print("Serial Number NOT FOUND for virtual {}".format(vSerial))
    
    if serialNumber != "":
        return serialNumber
    else:
        print("Serial Number NOT FOUND")

# Startup
if __name__ == "__main__":
    sys.exit(main())