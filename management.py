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
from argparse import ArgumentParser, ArgumentTypeError

# GLOBAL data
community, version, ip = None, None, None


def ip_format(addr):
    ''' Check wether a IP address has a correct format '''
    octets = addr.split(".")

    if len(octets) != 4:
        raise ArgumentTypeError("Ip {} does not follow an ip format (e.g. 127.0.0.1)".format(addr))

    for oct in octets:
        if not 0 <= int(oct) <= 255:
            raise ArgumentTypeError("Ip {} not in range 0.0.0.0 to 255.255.255.255".format(addr))
    
    return addr


def main(argv=None):
    global community, version, ip

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

    print(community, version, ip)

if __name__ == '__main__':
    exit(main())