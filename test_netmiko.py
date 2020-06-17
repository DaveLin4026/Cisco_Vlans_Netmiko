from netmiko import ConnectHandler

S1 = {
    'device_type': 'cisco_ios',
    'host':   '172.0.0.10',
    'username': 'ansible',
    'password': 'ansible',
    'port' : 22,          # optional, defaults to 22
    'secret': 'secret',     # optional enable password, defaults to ''
}

net_connect = ConnectHandler(**S1)
output = net_connect.send_command('show interface status')
print(output)

config_commands = [
  'interface g0/1',
  'switchport mode access',
  'switchport access vlan 300',
  'end'
]
output = net_connect.send_config_set(config_commands)
print(output)
