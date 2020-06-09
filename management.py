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
from easysnmp.exceptions import EasySNMPTimeoutError
from dataStructures import *
from argparse import ArgumentParser, ArgumentTypeError
from pyroute2 import IPRoute, NetlinkError
from ipaddress import IPv4Network

# GLOBAL data
community, version, ip, session = None, None, None, None
ipr = IPRoute()
routes = []

#Commands tap Interface
#ip tuntap add name tap0 mode tap
#ip link set tap0 up
#ip addr add 40.1.12.10/22 dev tap0
# snmp-server community public RO  


class NotRootUserException(Exception):
    """ Raised when a program not run as root """
    pass


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

    id, ifs, rt = get_identifier(), get_ifs(), get_route_table()
    init_node = Device(id=id, ifs=ifs, ip_table=rt)

    nodes, edges = iter_network(init_node)

    delete_routes()


def iter_network(node=None):
    """ Explore network with iterative BFS algorithm."""
    global session

    if not node: return
    fringe, nodes, edges = [node], [], {}
    
    
    while fringe:

        curr=fringe.pop(0)  #FIFO queue
        nodes.append(curr)
        add_edges(edges, curr) 

        neighbors = []
                
        for e in curr.ip_table:
            if e.next_hop.ip != "0.0.0.0" and e.next_hop not in neighbors:
                
                # Change session hostname.
                session = Session(hostname=e.next_hop.ip, community=community, version=version)

                mask = get_mask(curr, e.next_hop.ip)
                nw = Address.get_net_from_IP(e.next_hop.ip, mask[0])
                add_route(nw, mask[1])

                try:
                    id = get_identifier()
                except EasySNMPTimeoutError:
                    print("Cannot access device " + e.next_hop.ip+ ". Possible issues:\n* SNMP not active on device " + 
                            "\n* Device from another AS")
                    
                    # Not accessible next-hop, but we know is not end-point.
                    edges.setdefault((nw, mask[0]), []).append((e.next_hop.ip, "network"))

                if not in_fringe(fringe, id) and not is_expanded(nodes, id):
                    fringe.append(Device(id=id, ifs=get_ifs(), ip_table=get_route_table()))
                    
                neighbors.append(e.next_hop)

    return nodes, list(edges.values())

            
def is_expanded(nodes, id):
    for dev in nodes:
        if dev.id == id: return True

    return False


def in_fringe(fringe, id):
    for dev in fringe:
        if dev.id == id: return True

    return False


def add_route(ip_addr, mask):
    """ Function to add dinamically routes """
    global ipr, routes
    
    try:
        ipr.route("add", dst=ip_addr, mask=mask, gateway=ip)
        routes.append((ip_addr, mask))    # Deleted after program execution.
    
    except NetlinkError as e:
        """ Route already exists """
        if e.code == 17:
            pass

        elif e.code == 1:
            raise NotRootUserException("Must run program as root user.")

        else:
            raise e


def add_edges(edges, dev):
    """ Get each i/f on device and adds network as key and gateways as values """

    for iff in dev.ifs:
        if int(iff.type) != 6 or not iff.addr:
            continue
        
        nw = Address.get_net_from_IP(iff.addr.ip, iff.addr.mask)
        edges.setdefault((nw, iff.addr.mask), []).append((iff, dev))


def get_mask(dev, ip):
    """ Gets mask of a next-hop by interface information we have """

    for iff in dev.ifs:
        if int(iff.type) !=6: continue
        if Address.get_net_from_IP(iff.addr.ip, iff.addr.mask) == Address.get_net_from_IP(ip, iff.addr.mask):
            return iff.addr.mask, IPv4Network('0.0.0.0/' + iff.addr.mask).prefixlen # netmask, cdir

    return "0.0.0.0", 0


def delete_routes():
    for route in routes:
        try:
            ipr.route("del", dst=route[0], mask=route[1], gateway=ip)
        
        except NetlinkError:
            pass


def get_identifier():
    # Retrieve system statistics.

    name = session.get('sysName.0').value
    desc = session.get('sysDescr.0').value
    situation = session.get('sysORLastChange.0').value
    upTime = session.get('sysUpTime.0').value

    return Identifier(name, desc, situation, upTime)


def get_ifs():
    # Retrieve interfaces information

    total_entries = int(session.get('ifNumber.0').value)
    ifs = []

    
    for index in range(1,total_entries+1):
        ''' Note we save all type of ifs, but when exploring we shall only use,
         type 6 ifs (ethernet).'''
        status = session.get('ifOperStatus.' + str(index)).value
        iff_type = session.get('ifType.' + str(index)).value
        desc = session.get('ifDescr.' + str(index)).value
        speed = session.get('ifSpeed.' + str(index)).value
        addr_table = session.walk('ipAdEntIfIndex')
        addr = None

        for entry in addr_table:
            if entry.value == str(index):
                addr = Address(session.get('ipAdEntAddr.' + entry.oid_index).value,
                                session.get('ipAdEntNetMask.' + entry.oid_index).value)

        ifs.append(Interface(iff_type, desc, speed, addr))

    return ifs


def get_route_table():
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
