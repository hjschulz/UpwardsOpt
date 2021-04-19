import sys
import csv

from helpers import add_vectors, write_ranks
from cost import score, layer_score
import settings


def run():
    data_dict = {}
    ignore_cols = int(sys.argv[2])
    with open(sys.argv[1]) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        categories = []

        for row in csv_reader:
            row_data = row[ignore_cols:]
            if line_count == 0:
                categories = row_data
                line_count += 1
                continue
            if line_count == 1:
                for i in range(row_data.__len__()):
                    data_dict[categories[i]] = [float(row_data[i])]
                line_count += 1
                continue

            for i in range(row_data.__len__()):
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

    ranks = calculate_ranks(data_dict, weights)
    foundation = [0] * data_dict[ranks[0]].__len__()

    destination_file = open(sys.argv[3], 'w')
    write_ranks(ranks, destination_file)
    print('Score: %f' % score(data_dict, ranks, weights, foundation))


def calculate_ranks(data_dict, weights, foundation=None):
    ranks = [x for x in data_dict.keys()]
    if not foundation:
        foundation = [0] * data_dict[ranks[0]].__len__()
    print('Initial:\t%f' % score(data_dict, ranks, weights, foundation))

    ranks = best_first(data_dict, weights, foundation)
    print('BestFirst:\t%f' % score(data_dict, ranks, weights, foundation))

    ranks = two_opt(data_dict, weights, ranks, foundation)
    print('TwoOpt:\t%f' % score(data_dict, ranks, weights, foundation))

    return ranks


def best_first(data_dict, weights, foundation):
    remaining_categories = [x for x in data_dict.keys()]
    ranks = []
    num_layers = 0
    while remaining_categories:
        min_score = None
        min_category = None
        for category in remaining_categories:
            category_layer_score = layer_score(data_dict[category], foundation, weights)
            if not min_category or category_layer_score < min_score:
                min_score = category_layer_score
                min_category = category
        ranks.append(min_category)
        remaining_categories.remove(min_category)
        foundation = add_vectors(foundation, data_dict[min_category])
        print('Added %d layers' % num_layers)
        num_layers += 1

    return ranks


def two_opt(data_dict, weights, ranks, foundation):
    swaps = 0
    foundations = []
    for rank in ranks:
        foundations.append(foundation)
        foundation = add_vectors(foundation, data_dict[rank])

    best_score = score(data_dict, ranks, weights, foundation) * 2
    while score(data_dict, ranks, weights, foundation) < best_score:
        best_score = score(data_dict, ranks, weights, foundation)
        for i in range(1, len(ranks)):
            current_score = (layer_score(data_dict[ranks[i]], foundations[i], weights) +
                             layer_score(data_dict[ranks[i - 1]], foundations[i - 1], weights))
            swap_foundation = add_vectors(foundations[i - 1], data_dict[ranks[i]])
            swap_score = (layer_score(data_dict[ranks[i - 1]], swap_foundation, weights) +
                          layer_score(data_dict[ranks[i]], foundations[i - 1], weights))

            if swap_score < current_score:
                apply_moves(ranks, foundations, data_dict, {(i, 1): current_score - swap_score})
                swaps += 1
                print("Swappity swap # %d" % swaps)

    return ranks


def apply_moves(ranks, foundations, data_dict, eligible_moves):
    number_of_categories = ranks.__len__()
    sorted_eligible_moves = [i for i in
                             {k: v for k, v in
                              sorted(eligible_moves.items(), key=lambda item: item[1])}.keys()]
    swaps = 0
    protected_is = []
    for move in sorted_eligible_moves:
        if move[0] < move[1]:
            if swaps:
                continue
            popped_category = ranks.pop(move[0])
            ranks.insert((move[0] - move[1]) % number_of_categories, popped_category)
            for i in range(move[0] + 1, (move[0] - move[1]) % number_of_categories + 1):
                foundations[i] = add_vectors(foundations[i - 1], data_dict[ranks[i - 1]])

            swaps += 1
            break
        if not set(protected_is) & set(range(move[0] - move[1], move[0] + 1)):
            popped_category = ranks.pop(move[0])
            ranks.insert(move[0] - move[1], popped_category)
            protected_is.extend(range(max(0,
                                          move[0] - move[1]),
                                      min(number_of_categories - 1,
                                          move[0] + 1)))
            for i in range(move[0] - move[1] + 1, move[0] + 1):
                foundations[i] = add_vectors(foundations[i - 1], data_dict[ranks[i - 1]])
            swaps += 1
    return swaps


# Args:
# File name
# Number of columns to ignore
# Target file for ranks
# Target file for clusters
if __name__ == '__main__':
    run()
