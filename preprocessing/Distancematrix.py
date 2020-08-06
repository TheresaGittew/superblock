import numpy as np
import xlsxwriter


# config 1 describes placement of gates in a horizontal line in the middle of each block
def generate_distance_matrix_config_1( num_gb_in_row, num_gb_per_col, gates_p_sb, street_width, block_width):
    workbook = xlsxwriter.Workbook('Distance_Matrix_Layout_1.xlsx')
    worksheet = workbook.add_worksheet()

    num_sb_per_gb = 16

    # depending on the particular layout : get gates in one row / gates in one column
    # here: gates are placed on a horizontal axis in the middle of each superblock
    gates_total = num_gb_per_col * num_gb_in_row * num_sb_per_gb * gates_p_sb
    gates_in_one_row = num_gb_in_row * (num_sb_per_gb ** 0.5) * gates_p_sb
    gates_in_one_col = num_gb_per_col * (num_sb_per_gb ** 0.5)
    gate_distance_matrix = np.zeros((gates_total, gates_total))
    for a in range(gates_total):
        for b in range(gates_total):

            # get horizontal distance
            pos_x_axis_start = a % gates_in_one_row if a % gates_in_one_row < b % gates_in_one_row else b % gates_in_one_row
            pos_x_axis_end =  b % gates_in_one_row if a % gates_in_one_row < b % gates_in_one_row else a % gates_in_one_row

            # get num of superblock - distances (horizontally) by getting number of blocks between gates
            pos_x_axis_start_blocks = pos_x_axis_start - 1 if pos_x_axis_start % 2 == 0 and pos_x_axis_start != pos_x_axis_end else pos_x_axis_start
            num_block_dists = ( pos_x_axis_end - pos_x_axis_start_blocks) // 2

            # do the same for streets
            pos_x_axis_start_streets = pos_x_axis_start - 1 if pos_x_axis_start % 2 == 1  and pos_x_axis_start != pos_x_axis_end else pos_x_axis_start
            num_streets_dists = (pos_x_axis_end - pos_x_axis_start_streets) // 2
            total_dist_x = num_block_dists * block_width + num_streets_dists * street_width
            print(total_dist_x)

            # get vertical distance (here it's easier)
            pos_y_axis_start = a // gates_in_one_row if  a // gates_in_one_row < b // gates_in_one_row else b // gates_in_one_row
            pos_y_axis_end = b // gates_in_one_row if a // gates_in_one_row < b // gates_in_one_row else a // gates_in_one_row
            num_dists = (pos_y_axis_end - pos_y_axis_start)
            total_dist_y = num_dists * (block_width + street_width)

            # for this configuration, we have to take into account that if two blocks are placed horizontally,
            # we also have to go down / up first and can not just get the linear distance
            bypass = block_width if pos_y_axis_end == pos_y_axis_start and pos_x_axis_start != pos_x_axis_end else 0

            gate_distance_matrix[a, b] = total_dist_x + total_dist_y + bypass
            worksheet.write(a, b,  total_dist_x + total_dist_y + bypass)
    workbook.close()
    return gate_distance_matrix

result = generate_distance_matrix_config_1(1, 1, 2, 20, 1000)

print(result)

#distance matrix honeycomb with on the corners 
def generate_distance_matrix_config2(num_sb_per_gb, gates_per_sb, street_width, length, block_width):
    workbook = xlsxwriter.Workbook('Distance_Matrix_Layout_3.xlsx')
    worksheet = workbook.add_worksheet()

    gates_total = num_sb_per_gb * gates_per_sb
    gates_in_row = 4
    # print(gates_in_row)
    gate_distance_matrix = np.zeros((gates_total, gates_total))
    locations = []
    rows = 3

    honey_comb_counter = 0.5
    street_vertical = 1
    triangle = (block_width - length) / 2
    for row_index in range(rows):
        street_horizontal = 1
        block_counter = 0
        length_counter = 1
        for index in range(gates_in_row):
            locations.append(tuple([math.floor(street_width + triangle + length_counter * length
                                    + street_horizontal * street_width
                                    + block_counter * block_width),
                                    math.floor(honey_comb_counter * block_width + street_vertical * street_width)]))
            if index % 2 == 0:
                block_counter +=1
            else:
                street_horizontal += 2
                length_counter +=1
        honey_comb_counter += 0.5
        street_vertical +=1

    #print(locations)
    distances = np.zeros((gates_total, gates_total))
    for (index,gates) in enumerate(locations):
        for (index2, gates2) in enumerate(locations):
            #das stimmt noch nicht 
            distances[index, index2] = abs(gates[0] - gates2[0]) + abs(gates[1] - gates2[1])

    return locations, distances


locations, distance = generate_distance_matrix_config2(6, 2, 20, 800, 1000)
print(distance)
