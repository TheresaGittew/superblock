import pandas
import math
import numpy


class Params:

    # creates array per center type with specific centers I_c
    def create_specific_centers(self):
        set_I_c = []
        self.dict_centerinstance_centertype = {}
        center_counter = 0
        j = 0

        for i in self.ub_per_center:
            next_row = [center_counter + j for j in range(i)]
            for n in next_row:
                self.dict_centerinstance_centertype[n] = self.centernames[j]
            set_I_c.append(next_row)
            center_counter = next_row[-1] + 1 if next_row else center_counter
            j += 1
        print("Set ic ", set_I_c)
        print(self.dict_centerinstance_centertype)
        return set_I_c

    #  creates array with specific gates per superblock
    def create_gsb(self):
        G_sb = []
        count = 0
        for sb in range(self.num_SB_total):
            new_row = []
            for n in range(self.num_G_per_SB):
                new_row.append(count)
                count += 1
            G_sb.append(new_row)
        return G_sb

    def get_ub_for_center(self):
        ub_per_center = [math.floor((self.demand_c[i] * (self.num_SB_total - len(self.subset_SB_with_GC)) / (self.capacity_c[i] * self.beta[i]))) for i
                         in range(len(self.capacity_c))]
        return ub_per_center

    # creates dictionary of type [4,1],[2,3]
    # means: on superblock 4, we have  centertype 1 (that has to be a gigacenter), on superblock 2, we have c-type 3...
    def create_dict_for_gigacenter(self, index_sb_with_gc):
        self.dict_sb_giga_centertype = {}
        for i in index_sb_with_gc:
            index_gigacenter = (numpy.where(numpy.array(self.centernames) == i[1]))[0][0]
            self.dict_sb_giga_centertype[i[0]] = index_gigacenter

    # given the minimum distance that has to be in between the origin superblock and destination commercial building
    # for a share of the population in each superblock, we generate a 2-dim. array
    # first dimension: index of origin gate
    # second dimension: all other gates in a sufficiently large distance to that gate
    def create_subset_gates_for_commercials(self, zone_dist_begin, zone_dist_end):
        subset_G_in_zone = []
        for i in self.distances:
            matches_current_gate = []
            for j in self.distances:
                if self.distances.iloc[i, j] > zone_dist_begin and self.distances.iloc[i, j] < zone_dist_end:
                    matches_current_gate.append(j)
            subset_G_in_zone.append(matches_current_gate)
        return subset_G_in_zone

    # index_sb_with_gc is an array in which we predefine sb-numbers and the assigned gigacenter type
    # [4,'Hospital'][10, 'University']...
    def __init__(self, index_sb_with_gc):

        # sb total, inhabitants
        self.num_SB_total = 16
        self.set_SB = [i for i in range(self.num_SB_total)]
        self.inhabitants_per_sb = 5000

        # input parameters that we want to obtain from the excel file
        filePath = 'preprocessing/Daten_real.xlsx' #MFMS_Daten_Dummy.xlsx' #'preprocessing/MFMS_Daten_Dummy.xlsx'
        df = pandas.read_excel(filePath)
        self.area_c = df['area_c'].array
        demand_rate_c = df['demand_rate_c'].array
        self.demand_c = [self.inhabitants_per_sb * demand_rate_c[i] for i in range(len(demand_rate_c))]
        self.capacity_c = df['capacity_c'].array
        self.centernames = df['centernames'].array
        self.max_dist_c = df['max_dist_c'].array
        self.beta = df['beta'].array
        self.set_C = [i for i in range(len(self.area_c))]
        self.num_C_total = len(self.set_C)
        self.subset_C_gigac = [i for i in self.set_C if df['gigacenter'].array[i]] # center types are a giga c.
        self.subset_C_commc = [i for i in self.set_C if df['commercial'].array[i]] # center types are commercial b.

        # distance matrix
        filePath = 'preprocessing/Distance_Matrix_Layout_1.xlsx' # 'Distance_Matrix_Layout_1.xlsx'#'preprocessing/Distance_Matrix_Layout_1.xlsx'
        self.distances = pandas.read_excel(filePath, header=None)

        # commercial building + commercial traffic special settings
        # first we set the "zone" distances
        self.com_buildings_zone1_dist = 4000
        self.com_buildings_zone2_dist = 5000
        # also we set the share of people that at least have to travel this distance
        self.prop_demand_zone1 = 0.1
        self.prop_demand_zone2 = 0.1

        # then we create a set that specifies the  gates in a particular zone for any given gate
        # these destination gates then have a min. distance to the origin gate
        self.subset_G_zone1 = self.create_subset_gates_for_commercials(self.com_buildings_zone1_dist, self.com_buildings_zone2_dist)
        self.subset_G_zone2 = self.create_subset_gates_for_commercials(self.com_buildings_zone2_dist, 100000)
        print("set 1: ", self.subset_G_zone1)
        print("set 2: " , self.subset_G_zone2)


        # big M
        self.M = 500000

        # gates
        self.num_G_per_SB = 2                                     # number of gates per superblock
        self.num_G_total = self.num_G_per_SB * self.num_SB_total  # number of total gates of city (general gates)
        self.set_G = [i for i in range(self.num_G_total)]
        self.subset_G_SB = self.create_gsb()                      # specific gates per superblock; G_sb as subset of G


        # giga center settings (SB_with_GC is subset with the index of SB's that are reserved for GB);
        # in the dictionary, we can look up the assigned center type for such a reserved SB.
        self.subset_SB_with_GC = [int(i) for i in numpy.array(index_sb_with_gc)[:, 0]]

        # centers
        self.ub_per_center = self.get_ub_for_center()  # calculates the max.# of possible center instances for each type
        self.num_I_total = sum(i for i in
                               self.ub_per_center)  # i in I describes all used centers independent of center type
        self.set_I = [i for i in range(self.num_I_total)]

        # we have to make sure that the max. allowed number of placable centers is not 0! Otherwise infeasible model!
        print("Assertion:")
        print(self.ub_per_center)
        for i in range(self.num_C_total):
            assert self.ub_per_center[i] > 0 ,\
                "Invalid Input Data for Superblock Model. The given min. utilization isn't possible for center "+str(i)
        self.subset_I_c = self.create_specific_centers()  # assigns value to self.I_c

        # max area settings (usually, lot of space => but in case sb's are reserved for a giga center, max area = 0)
        self.max_area_normal = 18000
        self.max_area_gc = 0
        self.max_area_per_sb = [self.max_area_normal if sb not in self.subset_SB_with_GC else self.max_area_gc for sb in
                                self.set_SB]
        # dictionary
        self.create_dict_for_gigacenter(index_sb_with_gc)


params = Params([[5,'Hospital'],[6,'University'],[9,'Industry']])
print(params.distances)
print(params.subset_C_gigac)
print(params.subset_C_commc)



