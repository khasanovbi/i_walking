def get_center_of_points(point1, point2):
    x1, y1 = point1['coordinates']
    x2, y2 = point2['coordinates']
    return (x1 + x2) / 2, (y1 + y2) / 2


def get_point_distance(point1, point2):
    x1, y1 = point1['coordinates']
    x2, y2 = point2['coordinates']
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** (1 / 2)


def get_normal_vector(point1, point2):
    # Вектор перпендикулярный исходному с длиной равной половине расстояния между точками
    # a * x + b * y = 0 - уравнение для вектора, перпендикулярного исходной прямой
    # - x * a / b = y
    # (1, -a / b)
    x1, y1 = point1['coordinates']
    x2, y2 = point2['coordinates']
    point_distance = get_point_distance(point1, point2)
    normal_vector = (1, - (x2 - x1) / (y2 - y1))
    normal_vector_length = (normal_vector[0] ** 2 + normal_vector[1] ** 2) ** (1 / 2)
    normal_vector = normal_vector[0] / normal_vector_length, normal_vector[1] / normal_vector_length
    return normal_vector[0] * point_distance / 2, normal_vector[1] * point_distance / 2
