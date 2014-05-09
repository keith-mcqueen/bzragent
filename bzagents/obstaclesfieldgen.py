#!/usr/bin/python -tt

from vec2d import Vec2d


class ObstaclesFieldGen(object):
    def __init__(self, bzrc):
        self.bzrc = bzrc
        self.offset = 20
        self.force = 1
        self.obstacles = self.bzrc.get_obstacles()

    def vector_at(self, x, y):
        # for each obstacle, compute it's effect at the given location
        for obstacle in self.obstacles:
            north = obstacle[0][1]
            east = obstacle[0][0]
            south = obstacle[2][1]
            west = obstacle[2][0]

            # if the point is between the north and the south, then ...
            if south <= y <= north:
                # if the point is within the margin on the west, then return a westward vector
                if west - self.offset < x < west:
                    return Vec2d(-self.force, 0)
                # or if the point is within the margin on the east, then return an eastward vector
                elif east < x < east + self.offset:
                    return Vec2d(self.force, 0)
            # or if the point is between the east and the west, then ...
            elif west <= x <= east:
                # if the point is within the margin on the south, then return a southward vector
                if south - self.offset < y < south:
                    return Vec2d(0, -self.force)
                # or if the point is within the margin on the north, then return a northward vector
                elif north < y < north + self.offset:
                    return Vec2d(0, self.force)

        return Vec2d(0, 0)
