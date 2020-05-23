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

    def __init__(self, name="", description="", status="", time_on=0):
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
        self.ip = ip
        self.mask = mask

    def __str__(self):
        if self.mask: return ip + " " + mask
        return ip
