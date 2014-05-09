#!/usr/bin/python -tt

from vec2d import Vec2d


class BasesFieldGen(object):
    def __init__(self, bzrc):
        # save the controller
        self.bzrc = bzrc

        # the threshold is the value at which the distance gives the greatest force
        self.threshold = 400
        self.min_scale = 0.3

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
        factor = 1

        # determine if any of my tanks is holding a flag
        for tank in self.bzrc.get_mytanks():
            if not tank.flag.startswith("-"):
                factor = -1
                break

        # create a vector for the given location
        location_vector = Vec2d(x, y)

        # get the distance between my base and the given location
        distance = location_vector.get_distance(self.my_base_center)

        # normalize the vector to the base center
        force_vector = (location_vector - self.my_base_center).normalized()

        # scale the vector according as a function of distance
        if factor > 0:
            if 0 < distance < self.threshold:
                scale = 1 / distance
            else:
                scale = 0
        else:
            scale = 1

        # add the vector to the resultant
        return force_vector * scale * factor
