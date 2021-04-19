from helpers import add_vectors, add_weight

def score(data_dict, ranks, weights, foundation):
    if not foundation:
        foundation = [0] * len(data_dict[ranks[0]])
    chart_score = 0
    for rank in ranks:
        chart_score += layer_score(data_dict[rank], foundation, weights)
        foundation = add_vectors(foundation, data_dict[rank])
    return chart_score


def layer_score(layer, foundation, weights):
    bottom_line = foundation
    middle_line = add_vectors(foundation, [x / 2 for x in layer])
    top_line = add_vectors(foundation, layer)

    layer_score_value = 1

    wiggle_value = 0
    if weights['fda']:
        if weights['bottom_line']:
            wiggle_value += wiggle_line(layer, bottom_line, weights) * weights['bottom_line']
        if weights['middle_line']:
            wiggle_value += wiggle_line(layer, middle_line, weights) * weights['middle_line']
        if weights['top_line']:
            wiggle_value += wiggle_line(layer, top_line, weights) * weights['top_line']
        layer_score_value *= add_weight(wiggle_value, weights['fda'])

    bump_value = 0
    if weights['sda']:
        if weights['bottom_line']:
            bump_value += bump_line(layer, bottom_line, weights) * weights['bottom_line']
        if weights['middle_line']:
            bump_value += bump_line(layer, middle_line, weights) * weights['middle_line']
        if weights['top_line']:
            bump_value += bump_line(layer, top_line, weights) * weights['top_line']
        layer_score_value *= add_weight(bump_value, weights['sda'])

    break_value = 0
    if weights['fdr']:
        if weights['bottom_line']:
            break_value += break_line(layer, bottom_line, weights) * weights['bottom_line']
        if weights['middle_line']:
            break_value += break_line(layer, middle_line, weights) * weights['middle_line']
        if weights['top_line']:
            break_value += break_line(layer, top_line, weights) * weights['top_line']
        layer_score_value *= add_weight(break_value, weights['fdr'])

    return layer_score_value


def wiggle_point(line, j):
    return abs(line[j] - line[j - 1])


def wiggle_line(layer, line, weights):
    return sum(
        [(wiggle_point(line, j)
          * ((layer[j] + layer[j - 1]) ** weights['weight_exponent']))
         for j in range(1, len(line))]) / weights['total_sum']


def bump_point(line, j):
    return abs((line[j] - line[j - 1]) - (line[j - 1] - line[j - 2]))


def bump_line(layer, line, weights):
    return sum(
        [(bump_point(line, j)
          * (layer[j - 1] ** weights['weight_exponent']))
         for j in range(2, len(line))]) / weights['total_sum']


def break_point(layer, line, j):
    if (layer[j] + layer[j - 1]) / 2 == 0:
        return 0
    return (wiggle_point(line, j) / ((layer[j] + layer[j - 1]) / 2)) ** 2


def break_line(layer, line, weights):
    return sum(
        [(break_point(layer, line, j)
          * ((layer[j] + layer[j - 1]) ** weights['weight_exponent']))
         for j in range(1, len(line))]) / weights['total_sum']

