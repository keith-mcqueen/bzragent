#!/usr/bin/python -tt

from vec2d import Vec2d
from masterfieldgen import FieldGen


class FlagsFieldGen(FieldGen):
    def __init__(self, bzrc, default_factor=1):
        super(FlagsFieldGen, self).__init__(bzrc)
        # the threshold is the value at which the distance gives the greatest force
        self.threshold = 100
        self.protective_threshold = 50
        self.min_scale = 0.5
        self.default_factor = default_factor
        self.shoot = False

        # use the callsign to determine which flag exclude
        self.team = bzrc.get_constants()['team']
        self.enemy_colors = []
        for flag in bzrc.get_flags():
            if self.team != flag.color:
                self.enemy_colors.append(flag.color)

    def vector_at(self, x, y):
        factor = self.default_factor

        # determine if any of my tanks is holding a flag
        # for tank in self.bzrc.get_mytanks():
        #     if not tank.flag.startswith("-"):
        #         factor = 0
        #         break

        # create a vector for the given location
        location_vector = Vec2d(x, y)

        # prepare the resultant vector
        resultant_vector = Vec2d(0, 0)

        best_distance = int(self.bzrc.get_constants()['worldsize'])

        # for each flag, compute it's effect at the given location
        for flag in self.bzrc.get_flags():
            # if the flag is not one of our opponents' flag, then skip it
            # IOW, if its our own flag, ignore it
            if not flag.color in self.enemy_colors or flag.poss_color == self.team:
                continue

            # create a vector for the flag's position
            flag_vector = Vec2d(flag.x, flag.y)

            # get the distance between the current flag and the given location
            distance = location_vector.get_distance(flag_vector)
            if distance > best_distance:
                continue

            best_distance = distance

            # normalize the vector to the flag
            force_vector = (flag_vector - location_vector).normalized()

            # scale the vector as a function of distance
            if distance < self.threshold:
                scale = max(distance / self.threshold, self.min_scale)
            else:
                #scale = self.threshold / distance
                scale = 1

            # add the vector to the resultant
            resultant_vector = force_vector * scale * factor

        return resultant_vector, self.shoot
