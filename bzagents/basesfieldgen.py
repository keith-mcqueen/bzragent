#!/usr/bin/python -tt

import abc

from vec2d import Vec2d
from masterfieldgen import FieldGen


class BaseFieldGenBase(FieldGen):
    __metaclass__ = abc.ABCMeta

    def __init__(self, bzrc, default_factor=1):
        super(BaseFieldGenBase, self).__init__(bzrc)

        self.default_factor = default_factor
        self.shoot = False

        # use the callsign to determine which flag exclude
        self.team = bzrc.get_constants()['team']

        # get the bases
        for base in bzrc.get_bases():
            if self.team == base.color:
                north = base.corner1_y
                east = base.corner1_x
                south = base.corner3_y
                west = base.corner3_x
                self.my_base_center = Vec2d((east + west) / 2, (north + south) / 2)
                break

    def vector_at(self, x, y):
        factor = self.default_factor

        # create a vector for the given location
        location_vector = Vec2d(x, y)

        # get the distance between my base and the given location
        distance = location_vector.get_distance(self.my_base_center)

        # normalize the vector to the base center
        force_vector = (location_vector - self.my_base_center).normalized()

        # scale the vector according as a function of distance
        scale = self.get_scale(distance)

        # add the vector to the resultant
        return force_vector * scale * factor, self.shoot

    @abc.abstractmethod
    def get_scale(self, distance):
        return


class ReturnToBaseFieldGen(BaseFieldGenBase):
    def __init__(self, bzrc, default_factor=-1):
        super(ReturnToBaseFieldGen, self).__init__(bzrc, default_factor)

    def get_scale(self, distance):
        return 1


class LeaveHomeBaseFieldGen(BaseFieldGenBase):
    def __init__(self, bzrc, default_factor=1):
        super(LeaveHomeBaseFieldGen, self).__init__(bzrc, default_factor)
        self.outer_threshold = int(self.bzrc.get_constants()['worldsize']) / 2

    def get_scale(self, distance):
        if 0 < distance < self.outer_threshold:
            return 1 / distance

        return 0
