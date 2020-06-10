from graphviz import Graph, Digraph
from dataStructures import *

#Tests
data_test = {'nodes': ['R1','R2','R3','R5','R4'],
            'edges': [
                (('40.1.12.1','R1'),()),
                (('192.168.17.1','R1'),('192.168.17.2','R2')),
                (('192.168.15.1','R1'),('192.168.15.3','R3')),
                (('192.168.3.3','R3'),('192.168.3.4','R4')),
                (('192.168.5.3','R3'),('192.168.5.5','R5')),
                (('192.168.13.3','R3'),('192.168.13.2','R2')),
                (('60.1.0.2','R2'),()),
                (('192.168.7.5','R5'),('192.168.7.4','R4')),
                (('90.9.1.5','R5'),()),
                (('30.0.2.4','R4'),()),
                (('50.0.4.4','R4'),()),
            ]}

class NetGenerator():

    node_mapping = {}

    def __init__(self, nodes, edges):
        if not nodes or not edges:
            return -1

        edge_list = []
        for edge in edges:
            transformed_edge = []
            for n in edge:
                transformed_edge.append((n[0], n[1].id.name))
            edge_list.append(tuple(transformed_edge))
        self.dot = Graph(comment='Network', format='pdf')
        self.data = {'nodes': [n.id.name for n in nodes], 'edges': edge_list}

        self.add_nodes()
        self.add_edges()
        self.dot.render('output/net')

    def add_nodes(self, node={}):
        #TO-DO if nodes not none
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
            self.dot.edge('NMS', self.data['edges'][0][0][1], label=self.data['edges'][0][0][0])

            num_nets = 0
            for net in self.data['edges'][1:]:
                num_routers = len(net)
                iff1, node1 = net[0]
                if num_routers == 1:
                    self.dot.node('end'+str(num_nets),  shape='box', label='EndPoint')
                    self.dot.edge(node1, 'end'+str(num_nets), taillabel=iff1)
                elif num_routers == 2:
                    iff2, node2 = net[1]
                    self.dot.edge(node2, node1, headlabel=iff2, taillabel=iff1)
                else:
                    pass


                num_nets+=1
