#!/usr/bin/python -tt

from vec2d import Vec2d
from masterfieldgen import FieldGen
from basesfieldgen import ReturnToBaseFieldGen


class ExploreFieldGen(FieldGen):
    def __init__(self, bzrc, world_map, default_factor=1):
        super(ExploreFieldGen, self).__init__(bzrc)

        self.default_shoot = False
        self.range = 50
        self.low_prob = 0.0005
        self.high_prob = 0.01
        self.default_factor = default_factor
        self.callsign = bzrc.get_mytanks()[0].callsign
        self.world_map = world_map

        self.return_to_base_field = ReturnToBaseFieldGen(bzrc)

    def vector_at(self, x, y):
        unexplored = self.world_map.find_point(x, y, self.range, self.world_map.default_probability,
                                               self.world_map.default_probability)
        if unexplored is None:
            return self.return_to_base_field.vector_at(x, y)

        return Vec2d(x - unexplored[0], y - unexplored[1]).normalized(), self.default_shoot
