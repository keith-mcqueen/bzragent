#!/usr/bin/python -tt

from vec2d import Vec2d


class FlagsFieldGen(object):
    def __init__(self, bzrc):
        # save teh controller
        self.bzrc = bzrc

        # the threshold is the value at which the distance gives the greatest force
        self.threshold = 100

        # use the callsign to determine which flag exclude
        self.callsign = bzrc.get_mytanks()[0].callsign
        self.enemy_colors = []
        for flag in bzrc.get_flags():
            if not self.callsign.startswith(flag.color):
                self.enemy_colors.append(flag.color)
                print flag.color

    def vector_at(self, x, y):
        # create a vector for the given location
        location_vector = Vec2d(x, y)

        # prepare the resultant vector
        resultant_vector = Vec2d(0, 0)

        # for each flag, compute it's effect at the given location
        for flag in self.bzrc.get_flags():
            # if the flag is not one of our opponents' flag, then skip it
            # IOW, if its our own flag, ignore it
            if not flag.color in self.enemy_colors:
                continue

            # create a vector for the flag's position
            flag_vector = Vec2d(flag.x, flag.y)

            # get the distance between the current flag and the given location
            distance = location_vector.get_distance(flag_vector)

            # normalize the vector to the flag
            force_vector = (flag_vector - location_vector).normalized()

            # scale the vector according as a function of distance
            if distance < self.threshold:
                scale = distance / self.threshold
            else:
                scale = self.threshold / distance

            # add the vector to the resultant
            resultant_vector += force_vector * scale
            #return resultant_vector

        return resultant_vector
