# CombiningData.py

import datetime
from collections import defaultdict
import itertools
import copy
import random
import networkx as nx
import pandas as pd
from pm4py import read_xes
from pyswmm import Simulation, Nodes, Links, Subcatchments
import numpy as np

# Inputs: 
# - T: set of traces from previous phase
# - M: map of EPA CADDIS human activities/sources to EPA SWMM landuses
# - G = (V,E): stormwater network graph of nodes V and edges E
# - maxdist: a maximum distance threshold

class Event:
    def __init__(self, name, timestamp):
        self.name = name
        self.timestamp = timestamp
        self.node = None
    def get_name(self):
        return (self.name)
    def get_timestamp(self):
        return (self.timestamp)
    def get_node(self):
        return (self.node)
    def set_timestamp(self, timestamp):
        self.timestamp = timestamp
    def set_node(self, node):
        self.node = node
class Trace:
    def __init__(self):
        self.events = []
    def add_event(self, event):
        self.events.append(event)
    def get_events(self):
        return self.events
class T_List:
    def __init__(self):
        self.traces = []
    def add_trace(self, trace):
        self.traces.append(trace)
    def get_traces(self):
        return self.traces
class mapping:
    def __init__(self, mappings):
        self.mappings = mappings
    def get_landuses_of(self, k):
        epa_caddis_nodes = self.mappings[self.mappings['c1'] == k.get_name()]
        landuses = epa_caddis_nodes['c2']
        return (list(landuses))
def create_set_of_traces(diagram):
    t_list = T_List()
    
    log = load_xes(diagram)

    list_of_events = Trace()
    current_trace_id = None
    
    for index, row in log.iterrows():
        name = row.iloc[0]
        timestamp = row.iloc[1]
        trace_id = row.iloc[2]
        
        if (trace_id == current_trace_id):
            
            new_event = Event(name, timestamp)
            list_of_events.add_event(new_event)
            
        else:
            if current_trace_id is not None:
                t_list.add_trace(list_of_events)
            
            list_of_events = Trace()
            current_trace_id = trace_id

            new_event = Event(name, timestamp)
            list_of_events.add_event(new_event)
    t_list.add_trace(list_of_events)
    
    '''# goes through all traces and their events
    for trace in t_list.get_traces():
        print("Trace:")
        for event in trace.get_events():
            print(f"{event.get_name()}, {event.get_timestamp()}")
    '''
    return (t_list)

def load_xes(diagram):
    
    log = read_xes(f'C:\\...\\{diagram}_Detailed_Py.xes')
    '''
    # Number of traces in event log
    print(f'Number of traces: {len(log)}')
    
    # Print events in upcoming traces
    for i in range(20):
        print(log.iloc[i])
        
    # Accessing specific column
    column = log.iloc[:, {column_number}}]
    '''
    return (log)
    
def load_mapping(diagram):
    
    df = pd.read_csv(f'C:\\...\\{diagram}_Detailed_MAPPING.csv')
    M = mapping(df)
    
    return (M)

def get_first_event_in_trace(trace):
    
    first_event = trace.get_events()[0]
    
    return (first_event)
    
def create_stormwater_graph(simulation):
    G = nx.DiGraph()
    
    for node in Nodes(simulation):
        G.add_node(node.nodeid)
    for link in Links(simulation):
        G.add_edge(link.inlet_node, link.outlet_node)
       
    return (G)

def get_landuse_percentages(sub, landuse):
    
    landuse_percentage = None
    addedPercent = False
    
    with open('C:\\...\\Newport_042220AZ2_edited.inp', 'r') as file:
        lines_in_file = file.readlines()
        
    inSection = False
    
    for line in lines_in_file:
        line = line.strip()
        
        if line.startswith('[COVERAGES]'):
            inSection = True
            continue
        
        if inSection and line == '':
            inSection = False
            break
        
        if inSection:
            data = line.split()
            curr_sub = data[0]
            curr_landuse = data[1]
            curr_percent = data[2]
            #print(f"CURRENT SUB, LANDUSE, PERCENT:{data[0]},{data[1]},{data[2]}")
            if sub == curr_sub:
                if landuse == curr_landuse:
                    if addedPercent:
                        landuse_percentage = landuse_percentage + float(curr_percent)
                    else:
                        landuse_percentage = float(curr_percent)
                        addedPercent = True
                        
    return (landuse_percentage)
    
def get_area(v, landuse, sim):
    # get landuse percentage of subcatchment and calculate area
    # area_landuse_in_subcatchment = subcatchment_area * landuse percentage    
    # subcatchment.connection gives the node
    sub = None
    subcatchment_node = None
    subcatchment_area = None
    found = False

    for node in v:
        if found:
            break
        for subcatchment in Subcatchments(sim):
            if node in subcatchment.connection:
                sub = subcatchment
                subcatchment_node = subcatchment.connection
                subcatchment_area = subcatchment.area
                found = True
                #print(f"Subcatchment ID, Area, Node: {sub.subcatchmentid}, {subcatchment_area}, {subcatchment_node}")
                break
    
    if sub is not None:
        landuse_percentage = get_landuse_percentages(sub, landuse)
        #print(landuse_percentage)
        if landuse_percentage is not None:
            associated_area = subcatchment_area * (landuse_percentage / 100.0)
            print(f"FOUND AREA: {associated_area}")
            return (associated_area)
        else:
            print("Landuse percentage is zero")
            return (0.0)
    else:
        print("Subcatchment not found")
        return (0.0)

def get_downstream_nodes(G, source_node, maxdist):
    # maxdist is inf
    downstream_nodes = nx.descendants(G, source_node)
    #print(downstream_nodes)
    
    return (downstream_nodes)

def get_propagation_time(source_node, dn_node, sim):
    constraint_F = 0.1
    
    source = Nodes(sim)[source_node]
    dn = Nodes(sim)[dn_node]
    
    time_when_flow_appears = None
    
    source.generated_inflow(0.2)
    
    for step in sim:
        curr_flow = dn.total_inflow
        
        if curr_flow > constraint_F:
            time_when_flow_appears = sim.current_time
            break
    timestamp = time_when_flow_appears.timestamp()
    print(timestamp)
    return (timestamp)

def assign_timestamp_and_node_to_item(dn_node, timestamp, item1):
    item1.set_timestamp(timestamp)
    item1.set_node(dn_node)
    print("ASSIGNED")
    
def edge_weight(start_node, end_node):
    distr_sample = np.random.uniform(60,24*60)
    
    return (distr_sample)

def combine_v1(T, M, G, sim):
    
    D = []
    
    v = list(G.nodes())
    
    sorted_nodes = sorted(v)
    
    for trace in T.get_traces():
        trace_startpoint = get_first_event_in_trace(trace)
        landuses = M.get_landuses_of(trace_startpoint) # list of landuses
        landuse = random.choice(landuses)
        print(landuse)
        landuse_area_at_node = get_area(v, landuse, sim)
        #source_node = random.choices(sorted_nodes, weights=landuse_area_at_node, k = 1)
        source_node = random.choice(sorted_nodes)
        
        downstream_nodes = get_downstream_nodes(G, source_node, maxdist=maxdist)
        for dn_node in downstream_nodes:
            proptime = get_propagation_time(source_node, dn_node, sim)
            print(proptime)
            
            new_trace = copy.deepcopy(trace)
            timestamp = proptime
            for item1,item2 in itertools.pairwise(trace.get_events()):
                timestamp += edge_weight(item1, item2)
                assign_timestamp_and_node_to_item(dn_node, timestamp, item1)
                
            D.append(new_trace)
    
    return (D)

def main():
        with Simulation('C:\\...\\Newport_042220AZ2_edited.inp') as sim:
            T = create_set_of_traces("Ammonia")
            M = load_mapping("Ammonia")
            G = create_stormwater_graph(sim)
            combine_v1(T, M, G, sim)
maxdist = float('inf')
main()
print("\n\nProgram Done")
