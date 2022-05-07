from jinja2 import Template
from netmiko import ConnectHandler

templateFile = open('add_loopback.j2', 'r').read()
jinja_template = Template(templateFile)

device_params = {
  'device_type': 'cisco_ios',
  'ip': '10.0.15.113',
  'username': 'admin',
  'password': 'cisco'
}

with ConnectHandler(**device_params) as ssh:
    commands = jinja_template.render(
        interface = 'Loopback 62070186',
        ip = '192.168.1.1',
        subnet = '255.255.255.0'
    ).splitlines()

    commands = [ command.strip() for command in commands if command.strip() != '' ]
    result = ssh.send_config_set(commands)
    print(result)
