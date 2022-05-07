import time
import json
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

student_code = '62070186'
interface_status_api_url = f'https://10.0.15.113/restconf/data/ietf-interfaces:interfaces/interface=Loopback{student_code}/enabled'

webex_room = 'NPA2021@ITKMITL'
webex_apt_url = 'https://webexapis.com'
webex_api_token = 'ZGMwNjYyZDMtYjgwZC00MmEwLWEzMjctYWUxM2MzYWU4Nzc0YTVlYzFiNDctMTk1_P0A1_f1f3518a-8e80-4525-82c8-62356e77eae1'

def check_interface_status():
    """ check interface status when lastest message is student_code """
    requests.packages.urllib3.disable_warnings()

    headers = {
        'Accept': 'application/yang-data+json', 
        'Content-type':'application/yang-data+json'
    }
    basicauth = ('admin', 'cisco')
    response = requests.get(interface_status_api_url, auth=basicauth, headers=headers, verify=False)

    if not response.ok:
        print(f'Error Status Code ({response.status_code}): Device api url error or interface not found')
        return []

    response_json = response.json()
    return response_json['ietf-interfaces:enabled']

def webex_post_message(webex_room_id, text):
    """ post interface status to webex room """
    webex_post_message_url = webex_apt_url + '/v1/messages'
    msg = MultipartEncoder({
        'roomId': webex_room_id,
        'text': text
    })
    headers = {
        'Authorization': f'Bearer {webex_api_token}',
        'Content-Type': msg.content_type,
    }
    response = requests.post(webex_post_message_url, data=msg, headers=headers, verify=False)

    if not response.ok:
        print(f'Error Status Code ({response.status_code}): {json.dumps(response.json(), indent=4)}')

def webex_find_room():
    """ find room id via room name """
    webex_list_rooms_url = webex_apt_url + '/v1/rooms'
    headers = {
        'Authorization': f'Bearer {webex_api_token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(webex_list_rooms_url, headers=headers)
    if not response.ok:
        print(f'Error Status Code ({response.status_code}): {json.dumps(response.json(), indent=4)}')
        return None
    rooms = response.json()

    for room in rooms['items']:
        if room['title'] == webex_room:
            return room['id']
    return None

def check_lastest_message(webex_room_id, webex_lastest_message_id):
    """ get lastest message and check that message is not query yet """
    webex_lastest_message_url = webex_apt_url + f'/v1/messages?roomId={webex_room_id}&max=1'
    headers = {
        'Authorization': f'Bearer {webex_api_token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(webex_lastest_message_url, headers=headers)
    if not response.ok:
        print(f'Error Status Code ({response.status_code}): {json.dumps(response.json(), indent=4)}')
        return ''
    message = response.json()

    if not message['items']:
        return ''

    if len(message['items']) and webex_lastest_message_id != message['items'][0]['id']:
        print('Received message: ' + message['items'][0]['text'])
        if message['items'][0]['text'] == student_code:
            if check_interface_status():
                webex_post_message(webex_room_id, f'Loopback{student_code} - Operational status is up')
            else:
                webex_post_message(webex_room_id, f'Loopback{student_code} - Operational status is down')
    return message['items'][0]['id']


def main():
    """ main code here """
    webex_room_id = webex_find_room()

    if not webex_room_id:
        print('Error: Webex Room Not Found')
        return

    webex_lastest_message_id = ''
    while True:
        webex_lastest_message_id = check_lastest_message(webex_room_id, webex_lastest_message_id)
        time.sleep(1)

main()
