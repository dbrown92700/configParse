import py_config_parse as c
import sys

# Creates a CSV file of switch interfaces and attributes
# Line, Interface, Shutdown, Description, Port-Channel, VRF, IP Address, VLAN/Trunk

filename = sys.argv[1]
outfile = filename.removesuffix('.txt') + '.csv'
f = open(outfile, 'w')
f.write('Line,Interface,Shutdown,Description,Port-Channel,VRF,IP Address,VLAN/Trunk\n')

config = c.Config(open(filename).read())
# config.print_section()

for line in config.list_of_lines(config.search_lines(['^interface'])):

	# Interface
	f.write(f"{line['number']},{line['command']},")

	# No config
	if not line['children']:
		f.write('\n')
		continue

	# Shutdown
	if config.list_of_lines(config.search_lines(search_command_list=['^shutdown'], source_lines=line['children'])):
		f.write('yes,')
	elif config.list_of_lines(config.search_lines(search_command_list=['^no shutdown'], source_lines=line['children'])):
		f.write('no,')
	else:
		f.write('no,')
	
	# Description
	for y in config.list_of_lines(config.search_lines(search_command_list=['^description'], source_lines=line['children'])):
		f.write(y['command'].removeprefix('description ').replace(',', ';'))
	f.write(',')

	# Port Channel
	for y in config.list_of_lines(config.search_lines(search_command_list=['^channel-group'], source_lines=line['children'])):
		f.write(y['command'].split(' ')[1])
	if 'port-channel' in line['command']:
		f.write(line['command'].removeprefix('interface port-channel').split('.')[0])
	f.write(',')

	# VRF
	for y in config.list_of_lines(config.search_lines(search_command_list=['^vrf member'], source_lines=line['children'])):
		f.write(y['command'].removeprefix('vrf member '))
	f.write(',')

	# IP Address
	for y in config.list_of_lines(config.search_lines(search_command_list=['^ip address'], source_lines=line['children'])):
		f.write(y['command'].removeprefix('ip address '))
		f.write(';')
	f.write(',')

	# VLAN / Trunk
	for y in config.list_of_lines(config.search_lines(search_command_list=['^switchport mode trunk'], source_lines=line['children'])):
		f.write('trunk')
	for y in config.list_of_lines(config.search_lines(search_command_list=['^switchport access vlan'], source_lines=line['children'])):
		f.write(y['command'].removeprefix('switchport access vlan'))
	if 'Vlan' in line['command']:
		f.write(line['command'].removeprefix('interface Vlan'))
	if '.' in line['command']:
		f.write(line['command'].split('.')[1])
	
	f.write('\n')

f.close()
