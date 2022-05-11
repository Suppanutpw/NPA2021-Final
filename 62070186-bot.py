import time
import json
import requests
requests.packages.urllib3.disable_warnings()

student_code = '62070186'
interface_status_api_url = f'https://10.0.15.113/restconf/data/ietf-interfaces:interfaces-state/interface=Loopback{student_code}/oper-status'
interface_noshut_api_url = f'https://10.0.15.113/restconf/data/ietf-interfaces:interfaces/interface=Loopback{student_code}'

webex_room = 'Webex space for Suppanut' # change room name here for testing
webex_apt_url = 'https://webexapis.com'
webex_api_token = 'NTAxYmQ4NTUtMzg1NS00MGYzLTg2MTAtYjMxM2JhMDZmNjc3ZTNkZjQwY2MtNjdl_P0A1_f1f3518a-8e80-4525-82c8-62356e77eae1' # please use your api token

# RESTCONF to CSR1000v packet header
device_headers = {
    'Accept': 'application/yang-data+json',
    'Content-type':'application/yang-data+json'
}
basicauth = ('admin', 'cisco')

# WebEX RestAPI Service packet header
webex_headers = {
    'Authorization': 'Bearer ' + webex_api_token,
    'Content-Type': 'application/json'
}

def check_interface_status():
    """ check interface status when lastest message is student_code """
    response = requests.get(interface_status_api_url, auth=basicauth, headers=device_headers, verify=False)

    if not response.ok:
        print(f'Error Status Code ({response.status_code}): Device api url error or interface not found')
        return 'down'

    response_json = response.json()
    return response_json['ietf-interfaces:oper-status']

def webex_post_message(webex_room_id, text):
    """ post interface status to webex room """
    webex_post_message_url = webex_apt_url + '/v1/messages'
    msg = {
        'roomId': webex_room_id,
        'text': text
    }
    response = requests.post(webex_post_message_url, headers=webex_headers, json=msg)

    if not response.ok:
        print(f'Error Status Code ({response.status_code}): {json.dumps(response.json(), indent=4)}')

def webex_find_room():
    """ find room id via room name """
    webex_list_rooms_url = webex_apt_url + '/v1/rooms'
    response = requests.get(webex_list_rooms_url, headers=webex_headers)
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
    response = requests.get(webex_lastest_message_url, headers=webex_headers)
    if not response.ok:
        print(f'Error Status Code ({response.status_code}): {json.dumps(response.json(), indent=4)}')
        return ''
    message = response.json()

    if not message['items']:
        return ''

    if len(message['items']) and webex_lastest_message_id != message['items'][0]['id']:
        print('Received message: ' + message['items'][0]['text'])
        if message['items'][0]['text'] == student_code:
            status = check_interface_status()
            webex_post_message(webex_room_id, f'Loopback{student_code} - Operational status is {status}')
            if status == 'down':
                """ check interface status when lastest message is student_code """
                yang_config = {
                    "ietf-interfaces:interface": {
                        "name": f"Loopback{student_code}",
                        "type": "iana-if-type:softwareLoopback",
                        "enabled": True,
                        "ietf-ip:ipv4": {
                            "address": [
                                {
                                    "ip": "192.168.1.1",
                                    "netmask": "255.255.255.0"
                                }
                            ]
                        },
                        "ietf-ip:ipv6": {}
                    }
                }
                response = requests.put(interface_noshut_api_url, data=json.dumps(yang_config), auth=basicauth, headers=device_headers, verify=False)

                if not response.ok:
                    print(f'Error Status Code ({response.status_code}): Device api url error or interface not found')
                    return 'down'

                webex_post_message(webex_room_id, f'Loopback{student_code} - Operational status is {check_interface_status()}')

    return message['items'][0]['id']


def main():
    """ main code here """
    webex_room_id = webex_find_room()
    webex_lastest_message_id = ''

    if not webex_room_id:
        exit('Error: Webex Room Not Found')

    while True:
        webex_lastest_message_id = check_lastest_message(webex_room_id, webex_lastest_message_id)
        time.sleep(1)

main()
