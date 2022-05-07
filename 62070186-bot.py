import json
import requests

interface_status_api_url = 'https://10.0.15.113/restconf/data/ietf-interfaces:interfaces/interface=Loopback62070186/enabled'

def check_interface_status():
	requests.packages.urllib3.disable_warnings()

	headers = {
		'Accept': 'application/yang-data+json', 
	    'Content-type':'application/yang-data+json'
	}
	basicauth = ('admin', 'cisco')
	resp = requests.get(interface_status_api_url, auth=basicauth, headers=headers, verify=False)

	if(resp.status_code < 200 or resp.status_code >= 300):
	    print('Error. Status Code: {} \nError message: {}'.format( resp.status_code,json.dumps(resp.json(), indent=4)))
	    return
	print("STATUS OK: {}".format(resp.status_code))

	response_json = resp.json()
	return response_json['ietf-interfaces:enabled']

print(check_interface_status())
