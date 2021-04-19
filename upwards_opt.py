import sys
import csv
from helpers import add_vectors, write_ranks, write_foundation
from cost import score, layer_score
import settings


def run():
    num_start_cols = int(sys.argv[2])
    start_cols = []
    with open(sys.argv[1]) as csv_file:
        # csv_reader = csv.reader(csv_file, delimiter=',')
        row = list(csv.reader([csv_file.readline()]))[0]
        start_cols.append(row[:num_start_cols])
        line_count = 0
        categories = row[num_start_cols:]
        data_dict = {categories[i]: [] for i in range(len(categories))}

        while row:
            row = list(csv.reader([csv_file.readline()]))[0]
            start_cols.append(row[:num_start_cols])
            row_data = row[num_start_cols:]
            for i in range(len(row_data)):
                data_dict[categories[i]].append(float(row_data[i]))

            line_count += 1

    silhouette = None
    for value in data_dict.values():
        if not silhouette:
            silhouette = value
        else:
            silhouette = add_vectors(silhouette, value)

    weight_exponent = settings.significance
    total_sum = sum([sum([x ** weight_exponent for x in layer]) for layer in data_dict.values()])

    weights = {
        'min_improvement': settings.min_improvement,
        'fda': settings.flatness,
        'sda': settings.straightness,
        'fdr': settings.continuity,
        'bottom_line': settings.bottom_line,
        'middle_line': settings.middle_line,
        'top_line': settings.top_line,
        'weight_exponent': weight_exponent,
        'total_sum': total_sum,
        'silhouette': silhouette,
    }

    line_weight_sum = weights['bottom_line'] + weights['middle_line'] + weights['top_line']
    weights['bottom_line'] /= line_weight_sum
    weights['middle_line'] /= line_weight_sum
    weights['top_line'] /= line_weight_sum

    silhouette_max = max(silhouette)
    ranks, foundation = calculate_ranks(data_dict, weights)
    foundation_min = min(foundation)
    foundation = [x - foundation_min + silhouette_max * 0.05 for x in foundation]

    destination_file = open(sys.argv[3], 'w')
    write_ranks(ranks, destination_file)
    print('Score: %f' % score(data_dict, ranks, weights, foundation))


def calculate_ranks(data_dict, weights, foundation=None):
    ranks = [x for x in data_dict.keys()]
    if not foundation:
        foundation = [0] * data_dict[ranks[0]].__len__()
    print("%d layers" % len(ranks))
    print('Initial:\t%f' % score(data_dict, ranks, weights, foundation))

    ranks, foundation = upwards_opt(data_dict, weights, ranks, foundation)
    return ranks, foundation


def upwards_opt(data_dict, weights, ranks, foundation):
    n = len(ranks)
    old_cost = None
    passes = 0
    swaps = 0
    while not old_cost or score(data_dict, ranks, weights, foundation) < old_cost * (1 - weights['min_improvement']):
        old_cost = score(data_dict, ranks, weights, foundation)
        i = 0
        visited = []
        while i < n:
            if visited.__contains__(i):
                print("Skip layer %d" % i)
                i += 1
                continue
            new_index = find_best_position(i, data_dict, ranks, weights, foundation)
            if new_index != i:
                # Move the layer
                layer = ranks.pop(i)
                ranks.insert(new_index, layer)
                swaps += 1
                current_score = score(data_dict, ranks, weights, foundation)
                print('Move layer %d \tto %d\t Swaps: %d\tPasses: %d\tNew cost: %.3f\tImpr.: %.3f' %
                      (i,
                       new_index,
                       swaps,
                       passes,
                       current_score,
                       (1 - (current_score / old_cost)) * 100
                       ))
            else:
                print('Stay layer %d' % i)
            if new_index <= i:
                i += 1
            else:
                # Update visited indices accordingly
                for j in range(len(visited)):
                    v = visited[j]
                    if i < v <= new_index:
                        visited[j] -= 1

                # Insert newIndex
                visited.append(new_index)
        passes += 1
    return ranks, foundation


def find_best_position(i, data_dict, ranks, weights, foundation):
    g_below = foundation
    g_above = add_vectors(foundation, data_dict[ranks[i]])
    cost_below = []
    cost_above = []
    cost_layer = []
    for j in range(len(ranks)):
        if j != i:
            cost_below.append(layer_score(data_dict[ranks[j]], g_below, weights))
            cost_above.append(layer_score(data_dict[ranks[j]], g_above, weights))
            cost_layer.append(layer_score(data_dict[ranks[i]], g_below, weights))
            g_below = add_vectors(g_below, data_dict[ranks[j]])
            g_above = add_vectors(g_above, data_dict[ranks[j]])
    cost_layer.append(layer_score(data_dict[ranks[i]], g_below, weights))

    current_cost = sum(cost_above) + cost_layer[0]
    best_index = 0
    best_cost = current_cost
    for j in range(1, len(ranks)):
        current_cost += cost_below[j - 1] - cost_above[j - 1]
        current_cost += cost_layer[j] - cost_layer[j - 1]
        if current_cost < best_cost:
            best_index = j
            best_cost = current_cost
    return best_index


# Args:
# File name
# Number of columns to ignore
# Target file for clusters
# Target file for ranks
if __name__ == '__main__':
    run()
# 3987334.646617
