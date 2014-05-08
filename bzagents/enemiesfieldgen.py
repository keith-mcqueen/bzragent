#!/usr/bin/python -tt

from vec2d import Vec2d


class EnemiesFieldGen(object):
    def __init__(self, bzrc):
        self.bzrc = bzrc
        self.threshold = 100
        self.callsign = bzrc.get_mytanks()[0].callsign

    def vector_at(self, x, y):
        # create a vector for the given location
        location_vector = Vec2d(x, y)

        # prepare the resultant vector
        resultant_vector = Vec2d(0, 0)

        # for each enemy tank, compute it's effect at the given location
        for tank in self.bzrc.get_othertanks():
            # create a vector for the flag's position
            tank_vector = Vec2d(tank.x, tank.y)

            # get the distance between the current tank and the given location
            distance = location_vector.get_distance(tank_vector)

            # normalize the vector to the tank
            force_vector = (location_vector - tank_vector).normalized()

            # scale the vector according as a function of distance
            if distance < self.threshold:
                scale = 1 / distance
            else:
                scale = 0

            # add the vector to the resultant
            resultant_vector += force_vector * scale
            #return resultant_vector

        return resultant_vector
