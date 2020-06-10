from graphviz import Graph, Digraph
from dataStructures import *
from ipaddress import IPv4Network

class NetGenerator():

    node_mapping = {}

    def __init__(self, nodes, edges):
        if not nodes or not edges:
            return -1

        edge_list = []
        for edge in edges:
            transformed_edge = []
            for n in edge:
                transformed_edge.append((n[0], n[1].id.name if isinstance(n[1], Device) else n[1]))
            edge_list.append(tuple(transformed_edge))
        self.dot = Graph(comment='Network', format='jpg')
        self.data = {'nodes': [n.id.name for n in nodes], 'edges': edge_list}

        self.add_nodes()
        self.add_edges()
        self.dot.render('output/net_graph')
        self.generate_report(nodes)


    def add_nodes(self, node={}):
        if node:
            position = str(len(self.node_mapping))
            self.node_mapping[position] = node['name']
            if 'type' in node:
                self.dot.node(node['name'], image="../"+node['type']+".png", shape= 'plaintext')
            else:
                self.dot.node(node['name'], shape= 'plaintext')
            return position, node['name']
        else:
            for router in self.data['nodes']:
                self.node_mapping[str(len(self.node_mapping))] = router
                self.dot.node(router, image="../router.jpg",  shape= 'plaintext')


    def add_edges(self, edge=None):
        if not edge:
            self.add_nodes(node={'name':'NMS', 'type':'host'})
            net = Address.get_net_from_IP(self.data['edges'][0][0][0].addr.ip, self.data['edges'][0][0][0].addr.mask)
            self.dot.edge('NMS', self.data['edges'][0][0][1], label=net, headlabel=Address.get_gateway_number(self.data['edges'][0][0][0].addr.ip, net), minlen='4')

            num_nets = 0
            for edge in self.data['edges'][1:]:

                num_routers = len(edge)
                iff1, node1 = edge[0]
                net = Address.get_net_from_IP(iff1.addr.ip, iff1.addr.mask)
                ciddr = '/'+str(IPv4Network('0.0.0.0/' + iff1.addr.mask).prefixlen)
                if num_routers == 1:
                    self.dot.node('end'+str(num_nets),  shape='box', label='EndPoint')
                    self.dot.edge(node1, 'end'+str(num_nets), label=net+ciddr, taillabel=iff1.desc+'\n'+Address.get_gateway_number(iff1.addr.ip, net), minlen='4')
                elif num_routers == 2:
                    iff2, node2 = edge[1]
                    if isinstance(iff2, Interface):
                        self.dot.edge(node2, node1, label=net+ciddr, headlabel=iff2.desc+'\n'+Address.get_gateway_number(iff2.addr.ip, net), taillabel=iff1.desc+'\n'+Address.get_gateway_number(iff1.addr.ip, net), minlen='4')
                    else:
                        try:
                            self.dot.node('net'+str(num_nets),  shape='box', label='Network')
                            self.dot.edge(node1, 'net'+str(num_nets), label=net+ciddr, taillabel=iff1.desc+'\n'+Address.get_gateway_number(iff1.addr.ip, net), headlabel=Address.get_gateway_number(iff2, net), minlen='4')
                        except Exception: pass
                else:
                    self.dot.node('switch'+str(num_nets),  style='invis', label=net+ciddr)
                    for iff, node in edge:
                        if isinstance(iff, Interface):
                            self.dot.edge(node, 'switch'+str(num_nets), taillabel=iff.desc+'\n'+Address.get_gateway_number(iff.addr.ip, net), minlen='4')
                        else:
                            try:
                                self.dot.node('net'+str(num_nets),  shape='box', label='Network')
                                self.dot.edge('switch'+str(num_nets), 'net'+str(num_nets), taillabel=iff+'\n'+Address.get_gateway_number(iff, net), minlen='4')
                            except Exception: pass
                num_nets+=1


    def generate_report(self, nodes):
        def w(msg=''):
            file.write(msg+'\n')

        with open('output/report.txt', 'w') as file:
            w('Network Report\n')
            w('Routers in network\n')
            for router in nodes:
                w('ROUTER IDENTIFIER')
                w('Name: ' + router.id.name)
                w('Description: ' + router.id.description)
                w('Status: ' + router.id.status)
                w('Time on: ' + str(round(float(router.id.time_on)/600,2)) + ' minutes')
                w('\nROUTER INTERFACES')
                for iff in router.ifs:
                    w('\t'+iff.desc)
                    w('\t\tType Number: '+iff.type)
                    w('\t\tSpeed: '+ str(round(float(iff.speed)/1000000,2)) + ' Mbits per second')
                    w('\t\tIP Address: ' + str(iff.addr))
                w('\nROUTER IP TABLE')
                for entry in router.ip_table:
                    w('\tEntry')
                    w('\t\tRoute Type: '+entry.route_type)
                    w('\t\tAddress: '+ str(entry.addr))
                    w('\t\tnext_hop: '+ str(entry.next_hop))
                w('\n'+'-'*60+'\n')
