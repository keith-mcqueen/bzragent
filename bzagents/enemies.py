__author__ = 'keith'

from masterfieldgen import FieldGen
from vec2d import Vec2d
import math


class Enemies(FieldGen):
    def __init__(self, bzrc):
        super(Enemies, self).__init__(bzrc)

        self.effective_range_sqrd = 50 ** 2
        #self.shooting_range_sqrd = 30 ** 2

        self.other_tanks = bzrc.get_othertanks()

        self.invocations_before_refresh = 10
        self.invoked = 0

    def vector_at(self, x, y):
        # don't get all the tanks every time, but every Nth time
        self.invoked += 1
        if self.invoked >= self.invocations_before_refresh:
            self.other_tanks = self.bzrc.get_othertanks()
            self.invoked = 0

        # go through all the tanks, but only worry about the first one that is within range
        for tank in self.other_tanks:
            if not tank.status.startswith('alive'):
                continue

            vector_to_tank = Vec2d(x - tank.x, y - tank.y)

            # get the distance between the current tank and the given location
            distance_sqrd = vector_to_tank.get_length_sqrd()
            if 0 < distance_sqrd < self.effective_range_sqrd:
                return vector_to_tank.normalized() * 50.0 / math.sqrt(distance_sqrd), True

        return Vec2d(0, 0), False