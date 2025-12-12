#!/usr/bin/env python3
import py_config_parse as c
import sys

# Creates a CSV file of switch acls and attributes
# ACL, Line, Protocol, Source, Dest, Port, Log, Count

filename = sys.argv[1]
outfile = filename.removesuffix('.txt') + '.csv'
f = open(outfile, 'w')
f.write('ACL,Applied,Line,Action,Protocol,Source,SPort,Dest,DPort,Log,Count\n')

config = c.Config(open(filename).read())
# config.print_section()

groups = config.search_lines(['^interface ', '^apply access-list ip '])
ints = {}
for group in groups:
    a = groups[group]['command'].split(' ')[-2]
    int = config.lines[groups[group]['parent']]['command'].removeprefix('interface ')
    try:
        ints[a].append(int)
    except KeyError:
        ints[a] = [int]

acl = config.search_lines('^access-list ip')
for line in config.list_of_lines(acl):
    acl_name = line['command'].removeprefix('access-list ip ')
    int_apply = ''
    if acl_name in ints:
        int_apply = ';'.join(ints[acl_name])
    count = 'no'
    log = 'no'
    for ace in line['children']:
        a = config.lines[ace]['command'].split(' ')
        line_number = a.pop(0)
        if a[0] == 'comment':
            f.write(f'{acl_name},{int_apply},{line_number},{" ".join(a)}\n')
            continue
        if a[-1] == 'count':
            count = 'yes'
            a.pop()
        if a[-1] == 'log':
            log = 'yes'
            a.pop()
        action = a.pop(0)
        protocol = a.pop(0)
        source = a.pop(0)
        sport = ''
        if a[0] in ['eq', 'gt', 'gte', 'lt', 'lte', 'group', 'range']:
            sport = ' '.join([a.pop(0), a.pop(0)])
        destination = a.pop(0)
        dport = ' '.join(a)
        f.write(f'{acl_name},{int_apply},{line_number},{action},{protocol},{source},{sport},{destination},{dport},{log},{count}\n')
f.close()


