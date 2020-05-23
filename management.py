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

    id = getIdentifier('.1.3.6.1.2.1.1.')

    ifs = getIfs('.1.3.6.1.2.1.2')


def getIdentifier(oid):
    name = session.get(oid+'5.0').value
    desc = session.get(oid+'1.0').value
    situation = session.get(oid+'1.0').value
    upTime = session.get(oid+'3.0').value

    return Identifier(name, desc, situation, upTime)


def getIfs(oid):
    total_entries = int(session.get(oid+'.1.0').value)
    oid += '.2.1'

    for row in range(1,total_entries+1):

        desc = session.get(oid+'.2.'+str(row)).value
        type = session.get(oid+'.3.'+str(row)).value
        speed = session.get(oid+'.5.'+str(row)).value
        addr = session.get(oid+'.6.'+str(row)).value
        print('desc entry ['+str(row)+']: '+ desc )
        print('type entry ['+str(row)+']: '+ type )
        print('Speed entry ['+str(row)+']: '+ speed )
        print('Addr entry ['+str(row)+']: '+ addr )
        #print(len(addr))
        print('#'*50)




if __name__ == '__main__':
    exit(main())
