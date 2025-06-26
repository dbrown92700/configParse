from vmanage_api import VmanageRestApi
from py_config_parse import Config
import csv

password = input('Password: ')
v = VmanageRestApi("thd-ol4-vmanage.sdwan.cisco.com:8443", "cxadmin", password)
d = v.get_request('/device')['data']
columns = ['hostname', 'status', 'total bandwidth']
edges = []

for edge in d:

    # Iterate through all the devices.  If it's a reachable edge, pull and parse the configuration

    edge_data = {'hostname': edge['host-name'], 'status': edge['reachability']}
    print(edge['host-name'], edge['reachability'])
    total_bandwidth = 0
    if edge['device-type'] == 'vedge' and edge['reachability'] == 'reachable':
        t = v.get_request(f'/template/config/running/{edge["uuid"]}')
        c = Config(t['config'])

        # Iterate through all the SDWAN interfaces. Parse 'tunnel-interface' ints

        ints = c.search_lines(['^sdwan$', '^interface'])
        for i in ints:

            # Is this a tunnel interface?
            sdwan_config = ints[i]
            tunnel = c.search_lines(['^tunnel-interface$'], sdwan_config['children'])
            if not tunnel:
                continue

            # Tunnel color
            tunnel_config = list(tunnel.values())[0]
            search_color = c.search_lines(['^color '], tunnel_config['children'])
            color = c.list_of_lines(search_color)[0]['command'].removeprefix('color ').removesuffix(' restrict')
            if f'{color}_int' not in columns:
                for var in ['int', 'shut', 'downstream', 'upstream']:
                    columns.append(f'{color}_{var}')

            # Interface name
            interface = sdwan_config['command']
            edge_data[f'{color}_int'] = interface.removeprefix('interface ')

            # Shutdown
            int_config = c.list_of_lines(c.search_lines([f"^{interface}$"]))[0]
            shutdown = c.list_of_lines(c.search_lines(['shutdown'], int_config['children']))[0]['command']
            edge_data[f'{color}_shut'] = shutdown

            # Look for a downstream bandwidth configured on the tunnel interface.
            # This is the edge part of per-tunnel QOS configuration
            downstream = ''
            search_down = c.search_lines(['^bandwidth-downstream '], ints[i]['children'])
            if search_down:
                downstream = int(c.list_of_lines(search_down)[0]['command'].removeprefix('bandwidth-downstream '))
            edge_data[f'{color}_downstream'] = downstream

            # Look for an upstream shaping policy configured on the interface for upstream bandwidth
            upstream = ''
            search_policy = c.search_lines(['^service-policy output'], int_config['children'])
            if search_policy:
                policy_name = c.list_of_lines(search_policy)[0]['command'].removeprefix('service-policy output ')
                policy = c.search_lines([f'^policy-map {policy_name}$'])
                search_shape = c.search_lines([f'^policy-map {policy_name}$', '^class class-default$', '^shape'])
                if search_shape:
                    upstream = int(c.list_of_lines(search_shape)[0]['command'].removeprefix('shape average '))/1000
            edge_data[f'{color}_upstream'] = upstream

            if shutdown == 'no shutdown':
                total_bandwidth += int(upstream or 0) + int(downstream or 0)
            print(f'{interface}, {shutdown}, {color}, {downstream}, {upstream}')

        print(total_bandwidth)
        edge_data['total bandwidth'] = total_bandwidth

    edges.append(edge_data)

csvfile = open('output1.csv', 'w', newline='')
writer = csv.DictWriter(csvfile, fieldnames=columns)
writer.writeheader()
for row in edges:
    writer.writerow(row)

v.logout()
