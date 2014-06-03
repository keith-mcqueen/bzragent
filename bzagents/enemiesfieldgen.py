#!/usr/bin/python -tt

from vec2d import Vec2d
from masterfieldgen import FieldGen


class EnemiesFieldGen(FieldGen):
    def __init__(self, bzrc, default_factor=1):
        super(EnemiesFieldGen, self).__init__(bzrc)

        self.threshold = 100
        self.shooting_range = 30
        self.default_factor = default_factor
        # self.callsign = bzrc.get_mytanks()[0].callsign

    def vector_at(self, x, y):
        factor = self.default_factor

        # create a vector for the given location
        location_vector = Vec2d(x, y)

        # prepare the resultant vector
        resultant_vector = Vec2d(0, 0)

        # determine if we should shoot
        shoot = False

        # for each enemy tank, compute it's effect at the given location
        for tank in self.bzrc.get_othertanks():
            # create a vector for the tank's position
            tank_vector = Vec2d(tank.x, tank.y)

            # get the distance between the current tank and the given location
            distance = location_vector.get_distance(tank_vector)

            # normalize the vector to the tank
            force_vector = (location_vector - tank_vector).normalized()

            # scale the vector according as a function of distance
            if 0 < distance < self.threshold:
                scale = self.threshold / (distance ** 2)
            else:
                scale = 0

            if distance < self.shooting_range:
                shoot = shoot or True

            # add the vector to the resultant
            resultant_vector += force_vector * scale * factor
            #return resultant_vector

        return resultant_vector, shoot
