import gurobipy as gp
from gurobipy import GRB
from pandas import *
from preprocessing.GenerationSubsets import *

# parameters (will later be initialized in separated script)
I_center = [10, 10, 10]  # number of specific centers per center type
I = sum(i for i in I_center)  # number of total placable centers (general centers)
I_c = create_specific_centers(I_center)  # specific centers per center type
C = {'museum', 'doctor', 'police'}  # center types
SB = 9  # number of superblocks


G_count = 2  # number of gates per superblock
G = G_count * SB  # number of total gates of city (general gates)
G_sb = create_gsb(G_count, SB)  # specific gates per superblock
demand_c = [5, 20, 15]  # demand per center type
capacity_c = [100, 100, 100]  # capacity per center type
beta = 0.01
area_c = [100, 450, 716]  # area needed per center type
maxArea = 1000  # maxArea available for center placement in each superblock
# distance matrix
filePath = 'preprocessing/Distance_Matrix_Layout_1.xlsx'
distances = pandas.read_excel(filePath, header=None)
maxDist_c = [3000, 3000, 3000]  # maximum Distances to center types
M = 500000  # big M



# SuperblockImplementation
m = gp.Model('Superblock')

# decision variables
visitors = {}
for g1 in range(G):
    for g2 in range(G):
        for i in range(I):
            visitors[g1, g2, i] = m.addVar(vtype=GRB.CONTINUOUS, name='visitors')

selfVisitors = {}
for sb in range(SB):
    for i in range(I):
        selfVisitors[sb, i] = m.addVar(vtype=GRB.CONTINUOUS, name='selfVisitors')

visFreq = {}
for sb in range(SB):
    for i in range(I):
        visFreq[sb, i] = m.addVar(vtype=GRB.CONTINUOUS, name='visFreq')

placementKey = {}
for sb2 in range(SB):
    for i in range(I):
        placementKey[sb2, i] = m.addVar(vtype=GRB.BINARY, name='placementKey' + str(sb2) + ' ' + str(i))

z = {}
for g1 in range(G):
    for g2 in range(G):
        for i in range(I):
            z[g1, g2, i] = m.addVar(vtype=GRB.BINARY, name='z')

m.update()
# objective function
# Minimize sum of traveled distances
m.setObjective(sum(sum(sum(visitors[g1, g2, i] * distances.iloc[g1, g2]
                           for g2 in range(G)) for g1 in range(G)) for i in range(I)), GRB.MINIMIZE)

# constraints
# constraint 1
# Sum of all Visitors and selfVisitors from a specific gate in a superblock
# to all general gates, for a specific center
# equal the visitor frequency for the specific center for all superblocks and all specific centers
for sb in range(SB):
    gates_of_sb = G_sb[sb]  # e.g. sb = 1 G_sb = [0, 1]; sb = 2 G_sb = [2, 3]
    for i in range(I):
        m.addConstr((sum(sum(visitors[g1, g2, i] for g2 in range(G))
                         for g1 in gates_of_sb) + selfVisitors[sb, i] == visFreq[sb, i]), "1")

# constraint 1a
# Greater/equal zero constraint for visitors for all general gates and all specific centers
for g1 in range(G):
    for g2 in range(G):
        for i in range(I):
            m.addConstr((visitors[g1, g2, i] >= 0), "1a")

# constraint 1b
# Greater/equal zero constraint for selfVisitors for all superblocks and all specific centers
for sb in range(SB):
    for i in range(I):
        m.addConstr((selfVisitors[sb, i] >= 0), "1b")

# constraint 1c
# visitors from g1 of sb to g2 of sb must be equal to zero for all superblocks,
# for all block specific gates and all specific centers
for sb in range(SB):
    gates_of_sb = G_sb[sb]
    for g1 in gates_of_sb:
        for g2 in gates_of_sb:
            for i in range(I):
                m.addConstr((visitors[g1, g2, i] == 0), "1c")

# constraint 2a
# Sum of visitors frequency overall superblocks is greater/equal to minimal required utilization for all center types
# and for all specific centers
for c in range(len(C)):
    for i_c in (I_c[c]):
        m.addConstr(sum(visFreq[sb, i_c] for sb in range(SB)) >= capacity_c[c] * beta * sum(
            placementKey[sb, i_c] for sb in range(SB)), "2a")

# constraint 2b
# Sum of visitors frequency overall superblocks is less/equal the utilization for all center types
# and for all specific centers
for c in range(len(C)):
    for i_c in (I_c[c]):
        m.addConstr(sum(visFreq[sb, i_c] for sb in range(SB)) <= capacity_c[c], "2b")

# constraint 3
# Sum of visitor frequency overall specific centers is greater/equal center type demand
# for all center types and all superblocks
for c in range(len(C)):
    for sb in range(SB):
            m.addConstr((sum(visFreq[sb, i_c] for i_c in (I_c[c])) >= demand_c[c]), "3")

# constraint 4a
# Big M constraint
# if center is placed visitors must be less than threshold M for all superblocks, for all general centers,
# for all  general gates and for block specific gates
for sb in range(SB):
    # print(sb)
    gates_of_sb = G_sb[sb]
    for i in range(I):
        # print(i)
        for g1 in range(G):
            # print(g1)
            for g2 in gates_of_sb:
                # print (g2)
                m.addConstr((visitors[g1, g2, i]
                             <= placementKey[sb, i] * M), "4a")

# constraint 4b
# Big M constraint
# If center is placed visitors to SelfVisitors to center must be less than threshold M for all superblocks
# and for all general centers
for sb in range(SB):
    for i in range(I):
        m.addConstr((selfVisitors[sb, i]
                     <= placementKey[sb, i] * M), "4b")

# constraint 4c
# Sum of placementKey overall superblocks must be less/equal 1 for all general centers
# (each center can only be placed maximal once)
for i in range(I):
    m.addConstr(sum(placementKey[sb, i] for sb in range(SB)) <= 1, "4c")

# constraint 5
# Distances that are traveled from g1 to g2 for a specific center must be less/equal the maxDistance
# per center type for all center types, specific centers and general gates
for c in range(len(C)):
    for i_c in I_c[c]:
        for g1 in range(G):
            for g2 in range(G):
                m.addConstr((z[g1, g2, i_c] * distances.iloc[g1, g2] <= maxDist_c[c]), "5")

# constraint 5a
# Big M constraint that sets z[g1, g2, i] == 1 if there are visitors from g1 to g2 for i
for c in range(len(C)):
    for i in I_c[c]:
        for g1 in range(G):
            for g2 in range(G):
                m.addConstr((visitors[g1, g2, i] <= z[g1, g2, i] * M), "5a")

# constraint 6
# The areas of all placed specific centers must be less/equal the maximum available area
# in a superblock for all superblocks
for sb in range(SB):
    m.addConstr((sum(sum(area_c[c] * placementKey[sb, i] for i in (I_c[c])) for c in
                     range(len(C))) <= maxArea), "6a")


#symmetry breaking constraint
for c in range(len(C)):
    print(I_c[c])
    for i in I_c[c]:
        if i <= len(I_c[c]) - 1:
            m.addConstr(sum(placementKey[sb, i] for sb in range(SB)) >= sum(placementKey[sb, i+1] for sb in range(SB)))

# execution
m.optimize()
