#!/usr/bin/python -tt

from vec2d import Vec2d


class FlagsFieldGen(object):
    def __init__(self, bzrc):
        self.bzrc = bzrc
        self.threshold = 100
        flags = bzrc.get_flags()
        self.callsign = bzrc.get_mytanks()[0].callsign
        self.enemy_colors = []
        for flag in flags:
            if not self.callsign.startswith(flag.color):
                self.enemy_colors.append(flag.color)
                print flag.color

    def vector_at(self, x, y):
        flags = self.bzrc.get_flags()
        location_vector = Vec2d(x, y)

        resultant_vector = Vec2d(0, 0)

        for flag in flags:
            if flag.color in self.enemy_colors:
                # We create vector from flags position
                flag_vector = Vec2d(flag.x, flag.y)

                # Get distance between two vectors
                distance = location_vector.get_distance(flag_vector)

                force_vector = (flag_vector - location_vector).normalized()

                if distance < self.threshold:
                    scale = distance / self.threshold
                    force_vector *= scale
                else:
                    scale = self.threshold / distance
                    force_vector *= scale

                resultant_vector += force_vector
                #return resultant_vector

        return resultant_vector
