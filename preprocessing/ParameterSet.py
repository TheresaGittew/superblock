from preprocessing.GenerationSubsets import *
import pandas


class Params:
    def __init__ (self):

        # hardcoded input parameters
        self.I_center = [100, 100, 100]                    # number of specific centers per center type
        self.I = sum(i for i in self.I_center)             # number of total placable centers (general centers), i in I describes all used centers independent of center type
        self.I_c = create_specific_centers(self.I_center)  # specific centers per center type,  I_c describes a subset of I with only the center instances of type c
        self.SB = 9                                        # number of superblocks
        self.G_count = 2                                   # number of gates per superblock
        self.G = self.G_count * self.SB                    # number of total gates of city (general gates)
        self.G_sb = create_gsb(self.G_count, self.SB)      # specific gates per superblock; G_sb as subset of G
        self.beta = 0.01
        self.max_area = 1000
        self.inhabitants_per_sb = 5000

        # input parameters that we want to obtain from an excel file
        filePath = 'MFMS_Daten.xlsx'
        df = pandas.read_excel(filePath)
        self.area_c = df['area_c'].array
        demand_rate_c = df['demand_rate_c'].array
        self.demand_c = [self.inhabitants_per_sb * demand_rate_c[i] for i in range (len(demand_rate_c))]
        self.capacity_c = df['capacity_c'].array
        self.centernames = df['centernames'].array
        self.max_dist_c = df['max_dist_c'].array

        # distance matrix
        filePath = 'Distance_Matrix_Layout_1.xlsx'
        self.distances = pandas.read_excel(filePath, header=None)
        self.M = 500000  # big M

param = Params()
print(param.centernames)
