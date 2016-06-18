from geojson import Point, Polygon


class Parser(object):
    POLYGON_TEMPLATE = 'POLYGON('
    POINT_TEMPLATE = 'POINT('

    def parse_polygon(self, string):
        parsed_string = string[len(self.POLYGON_TEMPLATE):-1]
        return Polygon(parsed_string)

    def parse_point(self, string):
        parsed_string = string[len(self.POINT_TEMPLATE):-1]
        return Point(tuple(map(float, parsed_string.split(' '))))

    def parse(self, string):
        if string.startswith(self.POLYGON_TEMPLATE):
            return self.parse_polygon(string)
        if string.startswith(self.POINT_TEMPLATE):
            return self.parse_point(string)
