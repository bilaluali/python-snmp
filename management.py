#! /usr/bin/env python3

'''---------------------------------------------------------------
    * Created on Sat May 23 2020
    *
    * GNU License
    *
    * Authors:
    *   - Bilal Uali - https://github.com/bilaluali
    *   - Aleks Genov Draganova - https://github.com/AleksSG
    *
-------------------------------------------------------------------- '''

import sys
import graphviz
from easysnmp import Session
from dataStructures import *
from argparse import ArgumentParser, ArgumentTypeError

# GLOBAL data
community, version, ip, session = None, None, None, None
devices = {}

#Commands tap Interface
#ip tuntap add name tap0 mode tap
#ip link set tap0 up
#ip addr add 40.1.12.10/22 dev tap0
# snmp-server community public RO  


def ip_format(addr):
    ''' Check wether a IP address has a correct format '''
    octets = addr.split(".")

    if len(octets) != 4:
        raise ArgumentTypeError("Ip {} does not follow an ip format (e.g. 127.0.0.1)".format(addr))

    for oct in octets:
        if not 0 <= int(oct) <= 255:
            raise ArgumentTypeError("Ip {} not in range 0.0.0.0 to 255.255.255.255".format(addr))

    return addr


def parse_args():
    global community, version, ip, session

    parser = ArgumentParser()

    parser.add_argument('-c', '--community', default='public', dest='community',
                                help="set string is sent along each SNMP request and allows (or denies) to devices statistics")

    parser.add_argument('-v', '--version', default=2, type=int, choices=[1, 2, 3], dest='version',
                                help="specify SNMP version to use. Note 2 (equivalent to 2c)")

    parser.add_argument('-i', '--ip', required=True, dest='ip', type=ip_format,
                                help="set IP address as a start point, to get other devices information (e.g. 127.0.0.1)")

    namespace = parser.parse_args()

    community = namespace.community
    version = namespace.version
    ip = namespace.ip
    session = Session(hostname=ip, community=community, version=version)


def main(argv=None):
    parse_args()
    init()

    return 0


def init():

    id, ifs, rt = getIdentifier(), getIfs(), getRouteTable()

    init_node = Device(id=id, ifs=ifs, ip_table=rt)

    for e in rt:
        print(e.addr, "--> ", e.next_hop)


# def iter_network(node=None):

#     if not Node: pass

#     sets, expanded = [node], []

#     while len(sets):
#         curr=sets.pop(0) #BFS.FIFO queue
#         expanded.append(curr)

#         for iff in node.ifs:
#             if int(iff.type) != 6:
#                 continue

#             sets.append()





def getIdentifier():
    # Retrieve system statistics.

    name = session.get('sysName.0').value
    desc = session.get('sysDescr.0').value
    situation = session.get('sysORLastChange.0').value  # TODO
    upTime = session.get('sysUpTime.0').value

    return Identifier(name, desc, situation, upTime)


def getIfs():
    # Retrieve interfaces information

    total_entries = int(session.get('ifNumber.0').value)
    ifs = []

    
    for index in range(1,total_entries+1):
        ''' Note we save all type of ifs, but when exploring we shall only use,
         type 6 ifs (ethernet).'''
        status = session.get('ifOperStatus.' + str(index)).value
        type = session.get('ifType.' + str(index)).value
        desc = session.get('ifDescr.' + str(index)).value
        speed = session.get('ifSpeed.' + str(index)).value
        addr_table = session.walk('ipAdEntIfIndex')
        addr = None

        for entry in addr_table:
            if entry.value == str(index):
                addr = Address(session.get('ipAdEntAddr.' + entry.oid_index).value,
                                session.get('ipAdEntNetMask.' + entry.oid_index).value)

        ifs.append(Interface(type, desc, speed, addr))

    return ifs


def getRouteTable():

    routes = []

    for entry in session.walk('ipCidrRouteDest'):
        oid_index = entry.oid_index
        
        route_type = session.get('ipCidrRouteType.' + oid_index).value
        addr = Address(session.get('ipCidrRouteDest.' + oid_index).value,
                       session.get('ipCidrRouteMask.' + oid_index).value)     
        next_hop = Address(session.get('ipCidrRouteNextHop.' + oid_index).value)


        routes.append(Entry(route_type, addr, next_hop))

    return routes

if __name__ == '__main__':
    exit(main())
