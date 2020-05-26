class Device():

    def __init__(self, id=None, ifs=[], ip_table=[]):
        self.id = id
        self.ifs = ifs
        self.ip_table = ip_table

    def add_interface(self, iff):
        self.ifs.append(iff)

    def add_entry(self, entry):
        self.ifs.append(entry)


class Identifier():

    def __init__(self, name="", description="", status="", time_on=""):
        self.name = name
        self.description = description
        self.status = status
        self.time_on = time_on



class Interface():

    def __init__(self, type, desc, speed, addr):
        self.type = type
        self.desc = desc
        self.speed = speed
        self.addr = addr


class Entry():

    def __init__(self, route_type, addr, next_hop):
        #TODO: check types in parameter
        self.route_type = route_type
        self.addr = addr
        self.next_hop = next_hop


class Address():

    def __init__(self, ip, mask=None):
        if mask:
            try:
                mask = self.cidr_to_netmask(int(mask))
            except ValueError:
                pass
        self.ip = ip
        self.mask = mask


    def cidr_to_netmask(self, cidr):
        cidr = int(cidr)
        mask = (0xffffffff >> (32 - cidr)) << (32 - cidr)
        return (str( (0xff000000 & mask) >> 24)   + '.' +
            str( (0x00ff0000 & mask) >> 16)   + '.' +
            str( (0x0000ff00 & mask) >> 8)    + '.' +
            str( (0x000000ff & mask)))



    def __str__(self):
        if self.mask:
            return self.ip + "/" + self.mask
        return self.ip
