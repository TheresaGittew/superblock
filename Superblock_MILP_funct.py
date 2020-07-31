import gurobipy as gp
from gurobipy import GRB
from pandas import *
import numpy as np
from preprocessing.ParameterSet import *


def execute_superblock(pm):

    m = gp.Model('Superblock')

    # decision variables
    visitors = {}
    for g1 in pm.set_G:
        for g2 in pm.set_G:
            for i in pm.set_I:
                visitors[g1, g2, i] = m.addVar(vtype=GRB.CONTINUOUS, name='visitors')

    selfVisitors = {}
    for sb in pm.set_SB:
        for i in pm.set_I:
            selfVisitors[sb, i] = m.addVar(vtype=GRB.CONTINUOUS, name='selfVisitors')

    visFreq = {}
    for sb in pm.set_SB:
        for i in pm.set_I:
            visFreq[sb, i] = m.addVar(vtype=GRB.CONTINUOUS, name='visFreq')

    placementKey = {}
    for sb2 in pm.set_SB:
        for i in pm.set_I:
            placementKey[sb2, i] = m.addVar(vtype=GRB.BINARY, name='placementKey' + str(sb2) + ' ' + str(i))

    z = {}
    for g1 in pm.set_G:
        for g2 in pm.set_G:
            for i in pm.set_I:
                z[g1, g2, i] = m.addVar(vtype=GRB.BINARY, name='z')

    m.update()

    # objective function
    # Minimize sum of traveled distances
    m.setObjective(sum(sum(sum(visitors[g1, g2, i] * pm.distances.iloc[g1, g2]
                               for g2 in pm.set_G) for g1 in pm.set_G)for i in pm.set_I), GRB.MINIMIZE)

    # constraints
    # constraint 1
    # Sum of all Visitors and selfVisitors from a specific gate in a superblock
    # to all general gates, for a specific center
    # equal the visitor frequency for the specific center for all superblocks and all specific centers
    for sb in pm.set_SB:
        gates_of_sb = pm.subset_G_SB[sb]  # e.g. sb = 1 G_sb = [0, 1]; sb = 2 G_sb = [2, 3]
        for i in pm.set_I:
            m.addConstr((sum(sum(visitors[g1, g2, i] for g2 in pm.set_G)
                             for g1 in gates_of_sb) + selfVisitors[sb, i] == visFreq[sb, i]), "1")

    # constraint 1a
    # Greater/equal zero constraint for visitors for all general gates and all specific centers
    for g1 in pm.set_G:
        for g2 in pm.set_G:
            for i in pm.set_I:
                m.addConstr((visitors[g1, g2, i] >= 0), "1a")

    # constraint 1b
    # Greater/equal zero constraint for selfVisitors for all superblocks and all specific centers
    for sb in pm.set_SB:
        for i in pm.set_I:
            m.addConstr((selfVisitors[sb, i] >= 0), "1b")

    # constraint 1c
    # visitors from g1 of sb to g2 of sb must be equal to zero for all superblocks,
    # for all block specific gates and all specific centers
    for sb in pm.set_SB:
        gates_of_sb = pm.subset_G_SB[sb]
        for g1 in gates_of_sb:
            for g2 in gates_of_sb:
                for i in pm.set_I:
                    m.addConstr((visitors[g1, g2, i] == 0), "1c")

    # constraint 2a
    # Sum of visitors frequency overall superblocks is greater/equal to minimal required utilization for all center types
    # and for all specific centers
    for c in pm.set_C:
        for i_c in (pm.subset_I_c[c]):
            m.addConstr(sum(visFreq[sb, i_c] for sb in pm.set_SB) >= pm.capacity_c[c] * pm.beta[c] * sum(
                placementKey[sb, i_c] for sb in pm.set_SB), "2a")

    # constraint 2b
    # Sum of visitors frequency overall superblocks is less/equal the utilization for all center types
    # and for all specific centers
    for c in pm.set_C:
        for i_c in (pm.subset_I_c[c]):
            m.addConstr(sum(visFreq[sb, i_c] for sb in pm.set_SB) <= pm.capacity_c[c], "2b")

    # constraint 3
    # Sum of visitor frequency overall specific centers is greater/equal center type demand
    # for all center types and all superblocks
    for c in pm.set_C:
        for sb in pm.set_SB:
            if sb not in pm.subset_SB_with_GC:
                m.addConstr((sum(visFreq[sb, i_c] for i_c in (pm.subset_I_c[c])) >= pm.demand_c[c]), "3")

    # constraint 4a
    # Big M constraint
    # if center is placed, visitors must be less than threshold M for all superblocks, for all general centers,
    # for all  general gates and for block specific gates (to make sure that visitor's don't visit a center instance i
    # that hasn't been build)
    for sb in pm.set_SB:   # we loop through all sb's that potentially have the center instance i
        gates_of_sb = pm.subset_G_SB[sb]
        for i in pm.set_I:
            for g1 in pm.set_G:
                for g2 in gates_of_sb:
                    m.addConstr((visitors[g1, g2, i]
                                 <= placementKey[sb, i] * pm.M), "4a")

    # constraint 4b
    # Big M constraint
    # If center is placed visitors to SelfVisitors to center must be less than threshold M for all superblocks
    # and for all general centers
    for sb in pm.set_SB:
        for i in pm.set_I:
            m.addConstr((selfVisitors[sb, i]
                         <= placementKey[sb, i] * pm.M), "4b")

    # constraint 4c
    # Sum of placementKey overall superblocks must be less/equal 1 for all general centers
    # (each center can only be placed maximal once)
    for i in pm.set_I:
        m.addConstr(sum(placementKey[sb, i] for sb in pm.set_SB) <= 1, "4c")

    # constraint 5
    # Distances that are traveled from g1 to g2 for a specific center must be less/equal the maxDistance
    # per center type for all center types, specific centers and general gates
    for c in pm.set_C:
        for i_c in pm.subset_I_c[c]:
            for g1 in pm.set_G:
                for g2 in pm.set_G:
                    m.addConstr((z[g1, g2, i_c] * (pm.distances.iloc[g1, g2]) <= pm.max_dist_c[c]), "5")

    # constraint 5a
    # Big M constraint that sets z[g1, g2, i] == 1 if there are visitors from g1 to g2 for i
    for c in pm.set_C:
        for i in pm.subset_I_c[c]:
            for g1 in pm.set_G:
                for g2 in pm.set_G:
                    m.addConstr((visitors[g1, g2, i] <= z[g1, g2, i] * pm.M), "5a")

    # constraint 6
    # The areas of all placed specific centers must be less/equal the maximum available area
    # in a superblock for all superblocks. The max. area is 0 in case the superblock is reserved for gigacenter.
    # Therefore, we just sum up all c's that are not giga centers.
    for sb in pm.set_SB:
            m.addConstr(sum(sum(pm.area_c[c] * placementKey[sb, i] for i in (pm.subset_I_c[c])) for c in
                            list(set(pm.set_C) - set(pm.subset_C_gigac))) <= pm.max_area_per_sb[sb], "6a")

    # constraint 6a
    # The placement key is already defined for sb's that are reserved for gigacenter:
    for sb in pm.subset_SB_with_GC:
        # look up assigned center typ
        assigned_centertyp = pm.dict_sb_giga_centertype[sb]
        assigned_center_instances = pm.subset_I_c[assigned_centertyp]
        m.addConstr(sum(placementKey[sb, i] for i in assigned_center_instances) == 1)

    # constraint 7a
    for sb in pm.set_SB:
        if sb not in pm.subset_SB_with_GC:
            for c_commerc in pm.subset_C_commc:
                for g1 in pm.subset_G_SB[sb]:
                m.addConstr(sum(sum(sum(visitors[g1, g2, i] for g2 in pm.subset_G_min_dist[g1]) for g1 in pm.subset_G_SB[sb]) for i in pm.subset_I_c[c_commerc]) >= pm.demand_c[c_commerc] * 0.1)


    # symmetry breaking constraint
    #for c in pm.set_C:
     #   for i in pm.subset_I_c[c]:
     #       if i <= len(pm.subset_I_c[c]) - 1:
     #           m.addConstr(
     #               sum(placementKey[sb, i] for sb in pm.set_SB) >= sum(placementKey[sb, i + 1] for sb in pm.set_SB))

    # execution
    m.optimize()

    return m.getVars();


params = Params([[4,'Hospital']])

execute_superblock(params)
