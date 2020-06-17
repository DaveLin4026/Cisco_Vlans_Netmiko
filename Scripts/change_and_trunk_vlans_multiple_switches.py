#!/usr/bin/env python
from netmiko import ConnectHandler
from getpass import getpass
import re

ip_addrs_file = open('ips.txt')
devices = ip_addrs_file.read().splitlines()

for ip in devices:
    device = {
        'device_type': 'cisco_ios',
        'ip': ip,
        'username': 'ansible',
        #'password': getpass(),
        'password': 'ansible'
    }
    net_connect = ConnectHandler(**device)
    net_connect.enable()
    #print(net_connect.find_prompt())

    print("Starting configuration on device " + device)
    source_vlan = "100"
    target_vlan = "200"
    target_vlan_name = "Test_VLAN"
    trunking_vlan = "4000"
    vlan_check = "none"


    #check for existance of target vlan
    vlan_status = net_connect.send_command("show vlan", use_textfsm=True)
    for vlan in vlan_status:
      if vlan['vlan_id'] == target_vlan:
        vlan_check = "exists"
        #print("Vlan " + target_vlan + " exists. No need to create")
        break
      else:
        vlan_check = "not-exist"
        #print("Vlan " + target_vlan + " does not exist. Need to create")

    #create target vlan if it doesn't exist
    if vlan_check == "not-exist":
      vlan_commands = [
        'vlan ' + target_vlan,
        'name ' + target_vlan_name,
        'end'
      ]
      print("Need to create vlan " + target_vlan)
      net_connect.send_config_set(vlan_commands)



    #change access ports from source vlan to target vlan
    inter_status = net_connect.send_command("show interface status", use_textfsm=True)
    for iface in inter_status:
      access_config_commands = [
        'interface ' + iface['port'],
        'switchport mode access',
        'switchport access vlan ' + target_vlan,
        'end'
      ]
      if iface['vlan'] == source_vlan:
        print("Need to change vlan on " + iface['port'])
        net_connect.send_config_set(access_config_commands)
      else:
        #print("Do NOT need to change vlan on " + iface['port'])

    #trunk target vlan
    trunk_status = net_connect.send_command("show spanning-tree vlan " + trunking_vlan, use_textfsm=True)
    for iface in trunk_status:
      if iface['type'] == "Shr " or iface['type'] == "P2p ":
        trunk_config_commands = [
          'interface ' + iface['interface'],
          'switchport trunk allowed vlan add ' + target_vlan,
          'end'
        ]
        print("Need to trunk vlan on " + iface['interface'])
        net_connect.send_config_set(trunk_config_commands)
      else:
        #print("Do NOT need to trunk vlan on " + iface['interface'])
