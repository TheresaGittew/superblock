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
