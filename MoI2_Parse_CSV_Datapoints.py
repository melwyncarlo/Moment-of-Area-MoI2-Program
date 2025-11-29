import csv

# MoI2
# Copyright Melwyn Francis Carlo, 2024

def getDatapointsFromCsv(points_filepath):
    datapoints_list = []
    try:
        with open(points_filepath, "r") as points_file_handler:
            points_datastream = csv.reader(points_file_handler)
            for point in points_datastream:
                if len(point) != 2:
                    continue
                datapoints_list.append([float(coordinate) for coordinate in point])
        if not datapoints_list:
            raise Exception("Custom Exception")
        return [True, datapoints_list]
    except:
        print("\n Invalid or corrupted CSV file.")
        return [False, []]
