import sys
import math
import ezdxf

# MoI2
# Copyright Melwyn Francis Carlo, 2024

ARC_TO_POLYLINE_RESOLUTION = 10
ELLIPSE_TO_POLYLINE_RESOLUTION = 10

DATATYPE_POLYLINE = "polyline"
DATATYPE_ELLIPSE = "ellipse"
DATATYPE_RECTANGLE = "rectangle"

def getDatapointsFromDxf(shape_filepath):

    try:
        doc = ezdxf.readfile(shape_filepath)
    except IOError:
        print("\n Error: Not a DXF file or a generic I/O error.")
        return [False, DATATYPE_POLYLINE, []]
    except ezdxf.DXFStructureError:
        print("\n Invalid or corrupted DXF file.")
        return [False, DATATYPE_POLYLINE, []]

    point_pairs_list = []
    ellipse_data = []
    rectangle_data = []

    msp = doc.modelspace()

    for e in msp:
        def add_point_pairs_from_iterable(iterable_input, list_output):
            previous_start_point = None
            for i, vertex in enumerate(iterable_input):
                if i == 0:
                    previous_start_point = vertex
                    continue
                list_output.append([[previous_start_point.x, previous_start_point.y], [vertex.x, vertex.y]])
                # print([[previous_start_point.x, previous_start_point.y], [vertex.x, vertex.y]])
                previous_start_point = vertex

        if e.dxftype() == "LINE":
            point_pairs_list.append([[e.dxf.start.x, e.dxf.start.y], [e.dxf.end.x, e.dxf.end.y]])
            # print([[e.dxf.start.x, e.dxf.start.y], [e.dxf.end.x, e.dxf.end.y]])
        elif e.dxftype() == "ARC":
            sagitta_1 = -e.dxf.radius * (math.sqrt(1 - math.pow(math.sin(ARC_TO_POLYLINE_RESOLUTION / 2 / e.dxf.radius), 2)) - 1)
            # sagitta_2 =  e.dxf.radius * (math.sqrt(1 - math.pow(math.sin(ARC_TO_POLYLINE_RESOLUTION / 2 / e.dxf.radius), 2)) + 1)
            flattened_arc = e.flattening(sagitta_1)
            add_point_pairs_from_iterable(flattened_arc, point_pairs_list)
        elif e.dxftype() == "CIRCLE":
            ellipse_data = [e.dxf.radius, e.dxf.radius]
            # print(ellipse_data)
        elif e.dxftype() == "ELLIPSE":
            if e.start_point == e.end_point:
                ellipse_data = []
                if e.dxf.major_axis.x == e.minor_axis.y == 0:
                    ellipse_data = [e.minor_axis.x, e.dxf.major_axis.y]
                elif e.dxf.major_axis.y == e.minor_axis.x == 0:
                    ellipse_data = [e.dxf.major_axis.x, e.minor_axis.y]
                else:
                    major_axis_length = e.dxf.major_axis.distance(e.dxf.center)
                    sagitta = -major_axis_length * (math.sqrt(1 - math.pow(math.sin(ELLIPSE_TO_POLYLINE_RESOLUTION / 2 / major_axis_length), 2)) - 1)
                    flattened_ellipse = e.flattening(sagitta)
                    add_point_pairs_from_iterable(flattened_ellipse, point_pairs_list)
                if ellipse_data:
                    pass
                    # print(ellipse_data)

    number_of_point_pairs = len(point_pairs_list)

    vertex_link_found = False

    if number_of_point_pairs > 0:
        for i in range(number_of_point_pairs):
            vertex_link_found = False
            def inner_loop(is_reversed):
                nonlocal vertex_link_found, i, number_of_point_pairs, point_pairs_list
                for j in range(number_of_point_pairs):
                    if i == j:
                        continue
                    if ((is_reversed and point_pairs_list[i][1] == point_pairs_list[j][1])
                    or (not is_reversed and point_pairs_list[i][1] == point_pairs_list[j][0])):
                        vertex_link_found = True
                        if not(j == 0 and i == (number_of_point_pairs - 1)):
                            point_pairs_list.insert(i + 1, list(reversed(point_pairs_list[j])) if is_reversed else point_pairs_list[j])
                            if j < i:
                                point_pairs_list.pop(j)
                            else:
                                point_pairs_list.pop(j + 1)
                        break
            inner_loop(False)
            if not vertex_link_found:
                inner_loop(True)
                if not vertex_link_found:
                    print("\n The shape is either open or invalid!")
                    return [False, DATATYPE_POLYLINE, []]
                    
        for i in range(number_of_point_pairs - 1):
            if (point_pairs_list[i][0][0] == point_pairs_list[i][1][0] == point_pairs_list[i+1][0][0] == point_pairs_list[i+1][1][0]
            or  point_pairs_list[i][0][1] == point_pairs_list[i][1][1] == point_pairs_list[i+1][0][1] == point_pairs_list[i+1][1][1]):
                point_pairs_list.pop(i + 1)
                point_pairs_list[i][1] = point_pairs_list[i+1][0]

        if len(point_pairs_list) == 4:
            rectangle_data = [point_pairs_list[0][0].distance(point_pairs_list[0][1]), point_pairs_list[1][0].distance(point_pairs_list[1][1])]

        datapoints_list = []
        for i in range(number_of_point_pairs):
            datapoints_list.append(point_pairs_list[i][0])
        datapoints_list.append(point_pairs_list[0][0])

    if vertex_link_found:
        return [True, DATATYPE_POLYLINE, datapoints_list]
    elif ellipse_data:
        return [True, DATATYPE_ELLIPSE, ellipse_data]
    elif rectangle_data:
        return [True, DATATYPE_RECTANGLE, rectangle_data]
    else:
        print("\n The shape is invalid! Use lines and arcs only.\n Use the explode feature, or the PEDIT - convert to polylines feature for splines.")
        return [False, DATATYPE_POLYLINE, []]
