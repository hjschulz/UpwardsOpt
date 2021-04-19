import sys
import csv

with open(sys.argv[1], 'r') as csv_file:
    row = list(csv.reader([csv_file.readline()]))[0]

    num_start_cols = int(sys.argv[2])

    res_file = open(sys.argv[1] + '-unpivot.csv', 'w', newline='')
    res_file_writer = csv.writer(res_file, delimiter=',', quotechar='"')
    headers = row
    header = headers[0:num_start_cols]
    header.extend(['Name', 'Value'])
    res_file_writer.writerow(header)
    while row:
        row = list(csv.reader([csv_file.readline()]))[0]
        for i in range(num_start_cols, len(row)):
            line = row[0:num_start_cols]
            line.extend([headers[i], row[i]])
            res_file_writer.writerow(line)
