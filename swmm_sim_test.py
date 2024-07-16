# -*- coding: utf-8 -*-

from pyswmm import Simulation

with Simulation('C:\\Users\\Anthony\\Desktop\\EPA SWMM\\Newport_010423b\\Newport_042220AZ2_edited.inp') as sim:
    sim.step_advance(300)
    for step in sim:
        print(sim.current_time)
        
        