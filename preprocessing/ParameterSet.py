import pandas
import math


class Params:

    # creates array per center type with specific centers I_c
    def create_specific_centers(self):
        set_I_c = []
        center_counter = 0

        for i in self.ub_per_center:
            print(i)
            next_row = [center_counter + j for j in range(i)]
            set_I_c.append(next_row)
            center_counter = next_row[-1] + 1 if next_row else center_counter
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
        # aufrunden, auch wenn abrunden logisch gesehen richtig wäre (es geht ja darum, dass die Mindestauslastung eingehalten wird)
        # so aber kann nicht sichergestellt werden, dass ub_per_center nicht irgendwo den Wert Null annimmt
        # daher ist das aufgerundete rein theroetisch mehr, als durch die Constraints möglich wäre
        ub_per_center = [math.floor((self.demand_c[i] * self.num_SB_total/ (self.capacity_c[i] * self.beta))) for i in range (len(self.capacity_c))]
        return ub_per_center


    def __init__ (self):

        self.num_SB_total = 9                                     # number of superblocks
        self.set_SB = [i for i in range(self.num_SB_total)]       # create set where each number is the index of specific superbl.
        self.beta = 0.05
        self.max_area = 12000
        self.inhabitants_per_sb = 5000

        # input parameters that we want to obtain from the excel file
        filePath =  'preprocessing/MFMS_Daten_Dummy.xlsx'
        df = pandas.read_excel(filePath)
        self.area_c = df['area_c'].array
        demand_rate_c = df['demand_rate_c'].array
        self.demand_c = [self.inhabitants_per_sb * demand_rate_c[i] for i in range(len(demand_rate_c))]
        self.capacity_c = df['capacity_c'].array
        self.centernames = df['centernames'].array
        self.max_dist_c = df['max_dist_c'].array
        self.set_C = [i for i in range(len(self.area_c))]
        self.num_C_total = len(self.set_C)
        self.is_gc = [True if df['gigacenter'].array[i] == 'True' else False for i in self.set_C]

        # distance matrix
        filePath =  'preprocessing/Distance_Matrix_Layout_1.xlsx'
        self.distances = pandas.read_excel(filePath, header=None)
        self.M = 500000  # big M


        # create sb's and gates
        self.num_G_per_SB = 2                                     # number of gates per superblock
        self.num_G_total = self.num_G_per_SB * self.num_SB_total  # number of total gates of city (general gates)
        self.set_G = [i for i in range(self.num_G_total)]
        self.subset_G_SB = self.create_gsb()                        # specific gates per superblock; G_sb as subset of G

        self.ub_per_center = self.get_ub_for_center()              # calculates the max.number of possible center instances for each type
        self.num_I_total = sum(i for i in self.ub_per_center)       # number of total placable centers (general centers), i in I describes all used centers independent of center type
        self.set_I = [i for i in range(self.num_I_total)]
        for i in range(self.num_C_total):
            assert self.ub_per_center[i] > 0
        self.subset_I_c = self.create_specific_centers()  # assigns value to self.I_c





param = Params()
print(param.distances)