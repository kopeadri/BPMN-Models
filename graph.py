import pygraphviz as pgv
import getting_relations as gr

class MyGraph(pgv.AGraph):

    def __init__(self, *args):
        super(MyGraph, self).__init__(strict=False, directed=True, *args)
        self.graph_attr['rankdir'] = 'LR'
        self.node_attr['shape'] = 'Mrecord'
        self.node_attr['style'] = 'filled'
        self.graph_attr['splines'] = 'ortho'
        self.graph_attr['nodesep'] = '0.8'
        self.edge_attr.update(penwidth='2')

    def add_event(self, name):
        super(MyGraph, self).add_node(name, shape="circle", label="")

    def add_end_event(self, name):
        super(MyGraph, self).add_node(name, shape="circle", label="", penwidth='3')

    def add_and_gateway(self, *args):
        super(MyGraph, self).add_node(*args, shape="diamond",
                                      width=".7", height=".7",
                                      fixedsize="true",
                                      fontsize="40", label="+")

    def add_xor_gateway(self, *args):
        super(MyGraph, self).add_node(*args, shape="diamond",
                                      width=".7", height=".7",
                                      fixedsize="true",
                                      fontsize="40", label="×")

    def add_and_split_gateway(self, source, targets, *args):
        gateway = 'ANDs ' + str(source) + '->' + str(targets)
        self.add_and_gateway(gateway, *args)
        super(MyGraph, self).add_edge(source, gateway)
        for target in targets:
            super(MyGraph, self).add_edge(gateway, target)

    def add_xor_split_gateway(self, source, targets, *args):
        gateway = 'XORs ' + str(source) + '->' + str(targets)
        self.add_xor_gateway(gateway, *args)
        super(MyGraph, self).add_edge(source, gateway)
        for target in targets:
            super(MyGraph, self).add_edge(gateway, target)

    def add_and_merge_gateway(self, sources, target, *args):
        gateway = 'ANDm ' + str(sources) + '->' + str(target)
        self.add_and_gateway(gateway, *args)
        super(MyGraph, self).add_edge(gateway, target)
        for source in sources:
            super(MyGraph, self).add_edge(source, gateway)

    def add_xor_merge_gateway(self, sources, target, *args):
        gateway = 'XORm ' + str(sources) + '->' + str(target)
        self.add_xor_gateway(gateway, *args)
        super(MyGraph, self).add_edge(gateway, target)
        for source in sources:
            super(MyGraph, self).add_edge(source, gateway)

    ######## adding loops ########
    def add_single_loop(self, node, *args):
        gateway = 'XORol ' + str(node)
        self.add_node(node)
        self.add_xor_gateway(gateway, *args)
        self.add_edge(node, gateway)
        self.add_edge(gateway, node)

    def add_double_loops(self, double_loop_set, parallel_events, causality):
        for loop_place in double_loop_set:
            if set(loop_place) not in parallel_events:
                first, second = loop_place
                if first in causality:
                    start = first
                    stop = second
                else:
                    start = second
                    stop = first
                gateway1 = 'XORtls ' + str(start) + '->' + str(stop)
                gateway2 = 'XORtlf ' + str(stop) + '->' + str(start)
                self.add_xor_gateway(gateway1)
                self.add_edge(start, gateway1)
                self.add_edge(gateway1, stop)
                self.add_xor_gateway(gateway2)
                self.add_edge(stop, gateway2)
                self.add_edge(gateway2, start)

    ##############################

    def update_nodes_attrs(self, events_counter, color_min, color_max):
        for node in self.nodes():
            if node not in ('start', 'end') and (node.find('XOR') and node.find('AND')) == -1:
                value = events_counter[node]
                color = 100 - int(float(color_max - value) / float(color_max - color_min) * 100.00)
                my_color = "#ff9933" + str(hex(color))[2:]
                node.attr['fillcolor'] = my_color
                node.attr['label'] = node + ", " + str(value)

    def update_edges_attrs(self, events_counter, direct_successors_dict, trace_min, trace_max):
        for edge in self.edges():
            if edge[0] != 'start' and edge[1] != 'end':
                if edge[0].find('XOR') != -1 and edge[0].find('end') != -1:  # dla pętli na cały proces
                    node_before = self.in_neighbors(edge[0])[0]
                    idx = direct_successors_dict[node_before]['successors'].index(edge[1])
                    cnt = direct_successors_dict[node_before]['counter'][idx]
                elif edge[0].find('XOR') != -1 or edge[0].find('AND') != -1:
                    cnt = events_counter[edge[1]]
                elif edge[1].find('XOR') != -1 or edge[1].find('AND') != -1:
                    cnt = events_counter[edge[0]]
                else:
                    idx = direct_successors_dict[edge[0]]['successors'].index(edge[1])
                    cnt = direct_successors_dict[edge[0]]['counter'][idx]
                edge.attr['penwidth'] = 2 * cnt / (trace_max - trace_min)
                edge.attr['xlabel'] = str(cnt)


def build_graph_from_log_matrix(log_matrix):
    start_set_events, end_set_events = gr.get_start_and_ends_events(log_matrix)
    direct_successors_dict = gr.get_direct_successors(log_matrix)
    causality, parallel_events = gr.get_causality_and_parallel(direct_successors_dict)
    inv_causality = gr.get_inv_causality(causality)
    events_counter = gr.get_events_counter(direct_successors_dict,log_matrix)

    one_loop_matrix = gr.get_one_loop_matrix(direct_successors_dict)
    two_loop_matrix = gr.get_two_loop_matrix(log_matrix, direct_successors_dict)

    parallel_events = [(k, *v) for k, v in parallel_events.items()]

    G = MyGraph()

    # adding split gateways based on causality
    for event in causality:
        if len(causality[event]) > 1:
            if tuple(causality[event]) in parallel_events:
                G.add_and_split_gateway(event, causality[event])
            else:
                G.add_xor_split_gateway(event, causality[event])

    # adding merge gateways based on inverted causality
    for event in inv_causality:
        if len(inv_causality[event]) > 1:
            if tuple(inv_causality[event]) in parallel_events:
                G.add_and_merge_gateway(inv_causality[event], event)
            else:
                G.add_xor_merge_gateway(inv_causality[event], event)
        elif len(inv_causality[event]) == 1:
            source = list(inv_causality[event])[0]
            G.add_edge(source, event)

    ######## adding loops ########

    # adding a single loop
    single_loop = []
    direct_successors_list = list(direct_successors_dict.keys())

    for i in range(0, len(one_loop_matrix)):
        for j in range(0, len(one_loop_matrix)):
            if (one_loop_matrix[i][j] != '') and (one_loop_matrix[i][j] != 0):
                single_loop.append(direct_successors_list[i])
    single_loop_set = set(single_loop)

    for node in single_loop_set:
        G.add_single_loop(node)

    # adding a double node
    double_loop = []
    for i in range(0, len(two_loop_matrix)):
        for j in range(0, len(two_loop_matrix)):
            if (two_loop_matrix[i][j] != '') and (two_loop_matrix[i][j] != 0):
                double_loop.append([direct_successors_list[i], direct_successors_list[j]])

    double_loop_set = []
    for short_list in double_loop:
        sorted_list = sorted(short_list)
        if (sorted_list not in double_loop_set) and sorted_list[0] != sorted_list[
            1]:  # to eliminate single loops in this iteration
            double_loop_set.append(sorted_list)

    G.add_double_loops(double_loop_set, parallel_events, causality)

    ###############################

    # adding start event
    G.add_event("start")
    if len(start_set_events) > 1:
        if tuple(start_set_events) in parallel_events:
            G.add_and_split_gateway("start", start_set_events)
        else:
            G.add_xor_split_gateway("start", start_set_events)
    else:
        in_nodes = G.in_neighbors(list(start_set_events)[0])
        if len(in_nodes) != 0:
            for n in in_nodes:
                if n.find('XORtlf') != -1:
                    G.add_edge("start", n)
                else:
                    G.add_edge("start", list(start_set_events)[0])
        else:
            G.add_edge("start", list(start_set_events)[0])

    # adding end event
    G.add_end_event("end")
    if len(end_set_events) > 1:
        if tuple(end_set_events) in parallel_events:
            G.add_and_merge_gateway(end_set_events, "end")
        else:
            G.add_xor_merge_gateway(end_set_events, "end")
    else:
        G.add_edge(list(end_set_events)[0], "end")

    # adding xor for a loop for the entire process

    for edge in G.edges():
        if edge[0] in end_set_events and edge[1] not in ('start', 'end') and (
                edge[1].find('XOR') and edge[1].find('AND')) == -1:
            G.add_xor_split_gateway(edge[0], (edge[1], 'end'))
            G.delete_edge(edge[0], 'end')
            G.delete_edge(edge)

    # update colors
    color_min = min(list(events_counter.values()))
    color_max = max(list(events_counter.values()))
    G.update_nodes_attrs(events_counter, color_min, color_max)
    G.update_edges_attrs(events_counter, direct_successors_dict, trace_min=color_min, trace_max=color_max)

    G.draw('./static/simple_process_model.png', prog='dot')
    #display(Image('simple_process_model.png'))

    return G