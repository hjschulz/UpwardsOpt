def add_vectors(v1, v2):
    return [v1[i] + v2[i] for i in range(v1.__len__())]


# Adds a weight to a value for multiplication purposes. Weight should be between 0 and 1. A weight of 0 will return 1.
def add_weight(value, weight):
    weighted_value = value * weight
    return 1 - weight + weighted_value


def avg_of_middle_line_first_derivatives(data_dict, rel=False):
    first_derivatives = []
    for key in data_dict.keys():
        layer = data_dict[key]
        for i in range(1, layer.__len__()):
            first_derivative = abs(layer[i] - layer[i - 1])
            if rel:
                layer_thickness_start = layer[i - 1]
                layer_thickness_end = layer[i]
                layer_thickness_avg = (layer_thickness_start + layer_thickness_end) / 2
                if layer_thickness_avg > 0:
                    first_derivative /= layer_thickness_avg
                else:
                    first_derivative = 0
            if layer[i] or layer[i - 1] or not rel:
                first_derivatives.append(first_derivative)
    sum_of_first_derivatives = sum(first_derivatives)
    result = sum_of_first_derivatives / first_derivatives.__len__()
    return result / 2


def avg_of_middle_line_second_derivatives(data_dict, rel=False):
    second_derivatives = []
    for key in data_dict.keys():
        layer = data_dict[key]
        for i in range(2, layer.__len__()):
            second_derivative = abs((layer[i] - layer[i - 1]) - (layer[i - 1] - layer[i - 2]))
            if rel:
                if layer[i - 1] > 0:
                    second_derivative /= layer[i - 1]
                else:
                    second_derivative = 0
            second_derivatives.append(second_derivative)
    sum_of_first_derivatives = sum(second_derivatives)
    result = sum_of_first_derivatives / second_derivatives.__len__()
    return result / 2


def write_ranks(ranks, destination_file):
    destination_file.write('category, rank\n')
    destination_file.write('\"%s\", %d\n' % ("Baseline", 0))
    count = 1
    for rank in ranks:
        destination_file.write('\"%s\", %d\n' % (rank, count))
        count += 1


def write_foundation(foundation, start_cols):
    destination_file = open("baseline.csv", 'w', newline='')
    destination_file_writer = csv.writer(destination_file, delimiter=',', quotechar='"')
    header = start_cols[0]
    header.extend(['Name', 'Value'])
    destination_file_writer.writerow(header)
    for i in range(0, len(foundation)):
        row = start_cols[i + 1]
        row.extend(['Baseline', foundation[i]])
        destination_file_writer.writerow(row)