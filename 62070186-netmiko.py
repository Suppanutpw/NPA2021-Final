import textfsm
from jinja2 import Template
from netmiko import ConnectHandler

# import jinja2 file template
template_file = open('manage_loopback.j2', 'r').read()
jinja_template = Template(template_file)

# device config to create ssh connect
device_params = {
  'device_type': 'cisco_ios',
  'ip': '10.0.15.113',
  'username': 'admin',
  'password': 'cisco'
}

with ConnectHandler(**device_params) as ssh:

    # default method will be create loopback interface
    method = 'create'
    with open('cisco_ios_show_interfaces.textfsm') as template_file:
        interface = ssh.send_command('show interfaces L62070186')
        textfsm_template = textfsm.TextFSM(template_file)
        interface = textfsm_template.ParseText(interface)
        if interface:
            # if there already have interface, will change method to delete interface
            method = 'delete'

    # generate set of command from jinja2
    commands = jinja_template.render(
        method = method,
        interface = 'Loopback 62070186',
        ip = '192.168.1.1',
        subnet = '255.255.255.0'
    ).splitlines()

    # clean code for easy to read on output terminal
    commands = [ command.strip() for command in commands if command.strip() != '' ]
    print(ssh.send_config_set(commands)) # send list of commands from jinja2
    print(ssh.save_config()) # saving running configuration
