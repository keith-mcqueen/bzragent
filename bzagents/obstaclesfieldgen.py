#!/usr/bin/python -tt

from vec2d import Vec2d
from masterfieldgen import FieldGen
from worldmap import WorldMap


class ObstaclesFieldGen(FieldGen):
    def __init__(self, bzrc, default_factor=1):
        super(ObstaclesFieldGen, self).__init__(bzrc)

        self.offset = 40
        self.force = 1
        self.default_factor = default_factor
        self.obstacles = self.bzrc.get_obstacles()
        self.shoot = False
        self.world_map = WorldMap(self.bzrc)

    def vector_at(self, x, y):
        factor = self.default_factor
        closest_edge = self.world_map.obstacle_edge_at(x, y, self.offset)
        if closest_edge is None:
            return Vec2d(0, 0), self.shoot

        # position vector
        vector_s = Vec2d(x, y)

        # vector for endpoint 1
        vector_a = Vec2d(closest_edge[0])

        # vector for endpoint 2
        vector_c = Vec2d(closest_edge[1])

        # final vector is the sum of vector from C to S and from A to S
        final_vector = (vector_c - vector_s) + (vector_a - vector_s)

        return final_vector.normalized() * self.force * factor, self.shoot


class ObstaclesFieldGen2(FieldGen):
    def __init__(self, bzrc, default_factor=1):
        super(ObstaclesFieldGen2, self).__init__(bzrc)
        self.offset = 20
        self.force = 1
        self.default_factor = default_factor
        self.obstacles = self.bzrc.get_obstacles()
        self.shoot = False

    def vector_at(self, x, y):
        factor = self.default_factor

        location_vector = Vec2d(x, y)

        # for each obstacle, compute it's effect at the given location
        for obstacle in self.obstacles:
            vector_a = Vec2d(obstacle[0][0], obstacle[0][1])
            vector_c = Vec2d(obstacle[2][0], obstacle[2][1])

            diameter_vector = vector_a - vector_c
            center_vector = vector_c + (0.5 * diameter_vector)
            radial_vector = location_vector - center_vector

            # if the point lies outside the radius (plus an offset), then skip this obstacle
            distance = radial_vector.get_length()
            threshold = 0.5 * diameter_vector.get_length() + self.offset
            if 0 == distance or distance > threshold:
                continue

            return radial_vector.perpendicular_normal() * factor * self.force * (threshold / distance), self.shoot

        return Vec2d(0, 0), self.shoot
