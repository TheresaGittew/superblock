import math
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd

# matches sb index to gate
def match_sb(visitors):
    visitors['sb1'] = visitors['g1'].apply(lambda x: math.floor(x / 2))
    visitors['sb2'] = visitors['g2'].apply(lambda x: math.floor(x / 2))
    return visitors


# calculates total visitors per sb
def total_visitors_per_sb(visitors):
    notnull_visitors = match_sb(visitors)[visitors.visitors > 0].iloc[:, -3:]
    sum_visitors = notnull_visitors.groupby('sb2')['visitors'].sum()
    sns.set()
    plt.bar(sum_visitors.index, sum_visitors)
    plt.show()
    return result

def heatmap(visitors):
    visitors = match_sb(visitors)
    visitors = visitors.iloc[:,-4:]
    grouped_visitors = visitors.groupby(['sb1', 'sb2']).agg('sum').reset_index()
    matrix = grouped_visitors.pivot(index='sb1', columns='sb2', values='visitors')
    plt.figure(figsize=(20,10))
    sns.heatmap(matrix, cmap="BuPu", linewidths=.5)
    plt.show()
    return matrix
    

# constructs grid
def draw_gates(street_width, block_width, num_sb, visitors, centers):
    gates_p_row = int(np.sqrt(num_sb) * 2)  # e.g 6
    gates_p_col = int(np.sqrt(num_sb))  # e.g 3
    locations = []

    for index in range(gates_p_col):
        street_counter = 1
        block_counter = 0
        for index2 in range(gates_p_row):
            if index == 0 and index2 == 0:
                locations.append(tuple([street_width, block_width / 2 + street_width]))
            elif index2 % 2 != 0 and index == 0:
                block_counter += 1
                locations.append(tuple(
                    [block_counter * block_width + street_counter * street_width, block_width / 2 + street_width]))
                street_counter += 1
            elif index2 % 2 != 0 and index != 0:
                block_counter += 1
                locations.append((tuple([block_counter * block_width + street_counter * street_width,
                                         block_width / 2 + street_width + index * (block_width + street_width)])))
                street_counter += 1
            elif index2 % 2 == 0 and index == 0:
                locations.append(tuple(
                    [block_counter * block_width + street_counter * street_width, block_width / 2 + street_width]))
            else:  # index2 % 2 == 0 and index != 0
                locations.append(tuple([block_counter * block_width + street_counter * street_width,
                                        block_width / 2 + street_width + index * (block_width + street_width)]))

    sns.set()
    plt.figure(figsize=(100, 100))

    plt.xlim(0, 4000)
    plt.ylim(0, 4000)

    plt.plot(20, 0)
    for index in range(len(locations)):
        plt.scatter(locations[index][0], locations[index][1])

    plt.show()
    return locations


result = draw_gates(20, 1000, 9, 0, 0)
print(result)
