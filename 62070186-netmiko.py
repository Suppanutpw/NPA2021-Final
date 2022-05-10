import textfsm
from jinja2 import Template
from netmiko import ConnectHandler

# import jinja2 file template
student_code = '62070186'
template_file = open('manage_loopback.j2', 'r').read()
jinja_template = Template(template_file)

# device config to create ssh connect
device_params = {
  'device_type': 'cisco_ios',
  'ip': '10.0.15.113',
  'username': 'admin',
  'password': 'cisco'
}

# input selected method
method = input('Please Select Method (create|delete): ').lower()
if method not in ['create', 'delete']:
    # if selected method is not valid, will return error
    exit(f'Error: This program have no option {method}')

with ConnectHandler(**device_params) as ssh:
    with open('cisco_ios_show_interfaces.textfsm') as template_file:
        interface = ssh.send_command(f'show interfaces L{student_code}')
        textfsm_template = textfsm.TextFSM(template_file)
        interface = textfsm_template.ParseText(interface)
        if method == 'create' and interface:
            # if there already have interface with correct config, will not create again
            if interface[0][1] == 'up' and interface[0][7] == '192.168.1.1/24':
                exit(f'Warning: Loopback{student_code} already create!')
        elif method == 'delete' and not interface:
            # if there already have no interface, will not delete again
            exit(f'Warning: Loopback{student_code} not exist!')

    # generate set of command from jinja2
    commands = jinja_template.render(
        method = method,
        interface = f'Loopback {student_code}',
        ip = '192.168.1.1',
        subnet = '255.255.255.0'
    ).splitlines()

    # clean code for easy to read on output terminal
    commands = [ command.strip() for command in commands if command.strip() != '' ]
    print(ssh.send_config_set(commands)) # send list of commands from jinja2
    print(ssh.save_config()) # saving running configuration
