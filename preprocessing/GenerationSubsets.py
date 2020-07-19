def create_specific_centers(centers):
    """
     creates array per center type with specific centers I_c
    """
    I_c = []
    center_counter = 0
    for i in centers:
        next_row = [center_counter + j for j in range(i)]
        I_c.append(next_row)
        center_counter = next_row[-1] + 1
    return I_c


def create_gsb(number_gates, number_sb):
    """
    creates array with specific gates per superblock
    """
    G_sb = []
    count = 0
    for sb in range(number_sb):
        new_row = []
        for n in range(number_gates):
            new_row.append(count)
            count += 1
        G_sb.append(new_row)

    return G_sb

    # print(create_gsb(2, 9))
    # all_centers = (create_specific_centers([100, 100, 100]))
    # print(all_centers)
    # print("Nur Polizei:")
    # print(all_centers[0])
