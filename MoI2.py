import os
import math
import MoI2_Parse_DXF_Shape
import MoI2_Parse_CSV_Datapoints

# MoI2
# Copyright Melwyn Francis Carlo, 2024

os.system("cls")

DEFAULT_DATAPOINTS_CSV_FILE = "datapoints.csv"
DEFAULT_SHAPE_DXF_FILE = "shape.dxf"
DXF_EXTENSION = ".dxf"
CSV_EXTENSION = ".csv"

points_or_shape_filepath = input("\n Enter a polygon points filepath: ")
decimal_places = input(" Enter the number of decimal places: ")
if points_or_shape_filepath == "":
    if os.path.isfile(DEFAULT_SHAPE_DXF_FILE):
        points_or_shape_filepath = DEFAULT_SHAPE_DXF_FILE
    else:
        points_or_shape_filepath = DEFAULT_DATAPOINTS_CSV_FILE
if not os.path.isfile(points_or_shape_filepath) or not(points_or_shape_filepath.endswith(DXF_EXTENSION) or points_or_shape_filepath.endswith(CSV_EXTENSION)):
    print(" Error: Invalid file!")
elif not decimal_places.isnumeric():
    print(" Error: Invalid decimal places")
elif int(decimal_places) < 0 or int(decimal_places) > 10:
    print(" Error: Invalid decimal places")
else:
    print(" Parsing file ...")
    datatype = MoI2_Parse_DXF_Shape.DATATYPE_POLYLINE
    if points_or_shape_filepath.endswith(DXF_EXTENSION):
        [is_fileread_successful, datatype, datapoints] = MoI2_Parse_DXF_Shape.getDatapointsFromDxf(points_or_shape_filepath)
    else:
        [is_fileread_successful, datapoints] = MoI2_Parse_CSV_Datapoints.getDatapointsFromCsv(points_or_shape_filepath)
    if is_fileread_successful:
        if datatype == MoI2_Parse_DXF_Shape.DATATYPE_ELLIPSE or datatype == MoI2_Parse_DXF_Shape.DATATYPE_RECTANGLE:
            ixx = math.pi * datapoints[0] * math.pow(datapoints[1], 3) / 4
            iyy = math.pi * datapoints[1] * math.pow(datapoints[0], 3) / 4
            ixy = 0
            cx = datapoints[0] / 2
            cy = datapoints[1] / 2
            a = math.pi * datapoints[0] * datapoints[1] if datatype == MoI2_Parse_DXF_Shape.DATATYPE_ELLIPSE else datapoints[0] * datapoints[1]
        else:
            datapoints_list = datapoints
            decimal_places = int(decimal_places)
            ixx = 0
            iyy = 0
            ixy = 0
            cx = 0
            cy = 0
            a = 0
            previous_point = [0, 0]
            for i, point in enumerate(datapoints_list):
                point = [float(coordinate) for coordinate in point]
                if i != 0:
                    first_multiplicand = (previous_point[0]*point[1] - point[0]*previous_point[1])
                    ixx += first_multiplicand * (previous_point[1]*previous_point[1] + previous_point[1]*point[1] + point[1]*point[1])
                    iyy += first_multiplicand * (previous_point[0]*previous_point[0] + previous_point[0]*point[0] + point[0]*point[0])
                    ixy += first_multiplicand * (previous_point[0]*point[1] + 2*previous_point[0]*previous_point[1] + 2*point[0]*point[1] + point[0]*previous_point[1])
                    cx += first_multiplicand * (previous_point[0] + point[0])
                    cy += first_multiplicand * (previous_point[1] + point[1])
                    a += first_multiplicand
                previous_point = [point[0], point[1]]
            ixx /= 12
            iyy /= 12
            ixy /= 24
            a /= 2
            a = abs(a)
            cx /= (6*a)
            cy /= (6*a)
            ixx = abs(ixx) - a * cy * cy
            iyy = abs(iyy) - a * cx * cx
            ixy = abs(ixy) - a * cx * cy
        print(f"\n Ixx = {ixx:.{decimal_places}f}\n Iyy = {iyy:.{decimal_places}f}\n Ixy = {ixy:.{decimal_places}f}\n Cx = {cx:.{decimal_places}f}\n Cy = {cy:.{decimal_places}f}\n A = {a:.{decimal_places}f}")
