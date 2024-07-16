# -*- coding: utf-8 -*-
import pandas as pd
import pm4py
import os
class Node:    
    def __init__(self, node_id, legend_id):
        self.node_id = node_id
        self.legend_id = legend_id
class Edge:
    def __init__(self, source, target):
        self.source = source
        self.target = target
def toBPMN():
    print("\nConverting CSV File...\n")
    xml = []
    xml.append("<?xml version='1.0' encoding='UTF-8'?>\n")
    xml.append("<bpmn:definitions xmlns:bpmn='http://www.omg.org/spec/BPMN/20100524/MODEL' id='Definitions_1'>\n")
    xml.append("<bpmn:process id='Process_1' isExecutable='true'>\n")
    
    # creating start event(s)
    xml.append("<bpmn:startEvent id='StartEvent_1'/>\n")
    xml.append("<bpmn:sequenceFlow id='Flow_start_1' sourceRef='StartEvent_1' targetRef='Task_channel_alteration'/>\n")
    
    # creating nodes
    for node in node_list:
        xml.append(f"<bpmn:task id='Task_{node.node_id}' name='{node.node_id}'/>\n")
        
    flow_ID = 0
    
    # creating edges
    for edge in edge_list:
        flow_ID = flow_ID + 1
        xml.append(f"<bpmn:sequenceFlow id='Flow_{flow_ID}' sourceRef='Task_{edge.source}' targetRef='Task_{edge.target}'/>\n")
    
    # creating end event(s)
    xml.append("<bpmn:endEvent id='EndEvent_1'/>\n")
    xml.append("<bpmn:sequenceFlow id='Flow_end_1' sourceRef='Task_decreased_fish' targetRef='EndEvent_1'/>\n")
    
    xml.append("</bpmn:process>\n")
    xml.append("</bpmn:definitions>\n")
    
    print(f"BPMN file saved to {file_name}_Py.bpmn\n")
    return ''.join(xml)
def save_to_file(file_content, file_path_name):
    with open(file_path_name, 'w', encoding='utf-8') as file:
        file.write(file_content)
def bpmn_to_xes():
    print("Converting BPMN file to XES...\n")
    # Importing BPMN 2.0 XML file
    bpmn_graph = pm4py.read_bpmn(os.path.join(f"C:\\Users\\Anthony\\Desktop\\Python\\BPMN\\{file_name}_Py.bpmn"))
    
    # Conversion to Petri net
    net, im, fm = pm4py.convert_to_petri_net(bpmn_graph)
    
    # Simulated log
    simulated_log = pm4py.play_out(net, im, fm)
    
    # Conversion to event log
    event_log = pm4py.convert_to_event_log(simulated_log)
    
    # Exporting event log
    pm4py.write_xes(event_log, f"C:\\Users\\Anthony\\Desktop\\Python\\XES\\{file_name}_Py.xes")
    
    print(f"\nXES file saved to {file_name}_Py.xes!\n")
    return
# The Start of the program #
node_list = []
edge_list = []

file_name = "Ammonia_Detailed"

df = pd.read_csv(f"C:\\Users\\Anthony\\Desktop\\Python\\CSV\\{file_name}.csv")

for index, row in df.iterrows():
        r1 = row['r1']
        r2 = row['r2']
        r3 = row['r3']

        if r1 == "edge":
            edge_list.append(Edge(r2, r3))
        elif r1 == "node":
            node_list.append(Node(r2, r3))
    
xmlBPMN = toBPMN()    

file_path_name = f"C:\\Users\\Anthony\\Desktop\\Python\\BPMN\\{file_name}_Py.bpmn"

save_to_file(xmlBPMN, file_path_name)

bpmn_to_xes()