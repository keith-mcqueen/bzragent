__author__ = 'keith'

from masterfieldgen import FieldGen
from vec2d import Vec2d
from bzrc import BZRC

EFFECTIVE_RANGE = 40


class WorldBoundaries(FieldGen):
    def __init__(self, bzrc):
        super(WorldBoundaries, self).__init__(bzrc)

        self.effective_range = 40
        self.world_size = int(bzrc.get_constants()["worldsize"]) / 2

    def vector_at(self, x, y):
        if x + EFFECTIVE_RANGE >= self.world_size:
            return Vec2d(-1, 0), False
            # return -1, 0, False

        if x - EFFECTIVE_RANGE <= -self.world_size:
            return Vec2d(1, 0), False
            # return 1, 0, False

        if y + EFFECTIVE_RANGE >= self.world_size:
            return Vec2d(0, -1), False
            # return 0, -1, False

        if y - EFFECTIVE_RANGE <= -self.world_size:
            return Vec2d(0, 1), False
            # return 0, 1, False

        return Vec2d(0, 0), False
        # return 0, 0, False


class ObstaclesNormal(FieldGen):
    def __init__(self, bzrc):
        super(ObstaclesNormal, self).__init__(bzrc)

        self.effective_range = 40

        self.edges = []
        for obstacle in bzrc.get_obstacles():
            length = len(obstacle)
            for i in range(0, length):
                self.edges.append(Edge(obstacle[i % length], obstacle[(i + 1) % length]))

    def vector_at(self, x, y):
        for edge in self.edges:
            # get the distance from the point to the edge
            distance_to_edge = edge.distance_to_point(x, y)

            # if the distance is within the effective range
            if 0 < distance_to_edge < self.effective_range:
                # get the closest point within the edge
                q = edge.get_closest_point(x, y)

                # if the closest point is within the edge endpoints
                if min(edge.p1.x, edge.p2.x) <= q.x <= max(edge.p1.x, edge.p2.x) and \
                    min(edge.p1.y, edge.p2.y) <= q.y <= max(edge.p1.y, edge.p2.y):
                    # return a force along the normal
                    return edge.normal, False

        return Vec2d(0, 0), False


# class ObstaclesTangential(FieldGen):
#     def __init__(self, bzrc):
#         super(ObstaclesTangential, self).__init__(bzrc)
#
#         self.effective_range = 15
#         self.obstacles = bzrc.get_obstacles()
#
#     def vector_at(self, x, y):
#         location_vector = Vec2d(x, y)
#
#         # for each obstacle, compute it's effect at the given location
#         for obstacle in self.obstacles:
#             vector_a = Vec2d(obstacle[0][0], obstacle[0][1])
#             vector_c = Vec2d(obstacle[2][0], obstacle[2][1])
#
#             diameter_vector = vector_a - vector_c
#             center_vector = vector_c + (0.5 * diameter_vector)
#             radial_vector = location_vector - center_vector
#
#             # if the point lies outside the radius (plus an offset), then skip this obstacle
#             distance = radial_vector.get_length()
#             threshold = 0.5 * diameter_vector.get_length() + self.effective_range
#             if distance > threshold or distance == 0:
#                 continue
#
#             return radial_vector.perpendicular_normal() * (threshold / distance), False
#
#         return Vec2d(0, 0), False


class ObstaclesTangential(FieldGen):
    def __init__(self, bzrc):
        super(ObstaclesTangential, self).__init__(bzrc)

        self.effective_range_sqrd = 30 ** 2

        self.corners = []
        for obstacle in bzrc.get_obstacles():
            self.corners.extend(Vec2d(p[0], p[1]) for p in obstacle)

    def vector_at(self, x, y):
        # check each corner
        for corner in self.corners:
            # create a vector to the corner from the current location
            vector_to_corner = Vec2d(corner.x - x, corner.y - y)

            # if the current location is within range of the corner
            if vector_to_corner.get_length_sqrd() <= self.effective_range_sqrd:
                # return a force vector around the corner
                return vector_to_corner.perpendicular_normal(), False

        return Vec2d(0, 0), False


class Edge:
    def __init__(self, p1, p2):
        self.p1 = Vec2d(p1)
        self.p2 = Vec2d(p2)
        self.normal = (self.p2 - self.p1).perpendicular_normal()
        self.d = self.p1.dot(self.normal)

    def distance_to_point(self, x, y):
        q = Vec2d(x, y)

        return abs(q.dot(self.normal) - self.d)

    def get_closest_point(self, x, y):
        q = Vec2d(x, y)

        return q + ((self.d - q.dot(self.normal)) * self.normal)


def main():
    bzrc = BZRC("localhost", 50005)
    obs_normal = ObstaclesNormal(bzrc)
    vector = obs_normal.vector_at(160, 100)
    print vector


if __name__ == '__main__':
    main()