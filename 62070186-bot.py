import time
import json
import requests

interface_status_api_url = 'https://10.0.15.113/restconf/data/ietf-interfaces:interfaces/interface=Loopback62070186/enabled'

webex_room = 'NPA2021@ITKMITL'
webex_room = 'Webex space for Suppanut'
webex_apt_url = 'https://webexapis.com'
webex_api_token = 'ZGMwNjYyZDMtYjgwZC00MmEwLWEzMjctYWUxM2MzYWU4Nzc0YTVlYzFiNDctMTk1_P0A1_f1f3518a-8e80-4525-82c8-62356e77eae1'

def check_interface_status():
    requests.packages.urllib3.disable_warnings()

    headers = {
        'Accept': 'application/yang-data+json', 
        'Content-type':'application/yang-data+json'
    }
    basicauth = ('admin', 'cisco')
    response = requests.get(interface_status_api_url, auth=basicauth, headers=headers, verify=False)

    if(response.status_code < 200 or response.status_code >= 300):
        print('Error. Status Code: {} \nError message: {}'.format( response.status_code,json.dumps(response.json(), indent=4)))
        return

    response_json = response.json()
    return response_json['ietf-interfaces:enabled']

def webex_find_room():
    webex_list_rooms_url = webex_apt_url + '/v1/rooms'
    headers = {
        'Authorization': f'Bearer {webex_api_token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(webex_list_rooms_url, headers=headers)
    if(response.status_code < 200 or response.status_code >= 300):
        print('Error. Status Code: {} \nError message: {}'.format(response.status_code,json.dumps(response.json(), indent=4)))
        return
    rooms = response.json()

    for room in rooms['items']:
        if room['title'] == webex_room:
            return room['id']
    return None

def check_lastest_message(webex_room_id, webex_lastest_message_id):
    webex_lastest_message_url = webex_apt_url + f'/v1/messages?roomId={webex_room_id}&max=1'
    headers = {
        'Authorization': f'Bearer {webex_api_token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(webex_lastest_message_url, headers=headers)
    if(response.status_code < 200 or response.status_code >= 300):
        print('Error. Status Code: {} \nError message: {}'.format(response.status_code,json.dumps(response.json(), indent=4)))
        return
    message = response.json()

    if not message['items']:
        return ''

    if len(message['items']) and webex_lastest_message_id != message['items'][0]['id']:
        print('Received message: ' + message['items'][0]['text'])
    return message['items'][0]['id']



def main():
    webex_room_id = webex_find_room()

    if not webex_room_id:
        print('Webex Room Not Found')
        return

    webex_lastest_message_id = ''
    while True:
        webex_lastest_message_id = check_lastest_message(webex_room_id, webex_lastest_message_id)
        time.sleep(1)

main()
