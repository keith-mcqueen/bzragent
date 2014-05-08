#!/usr/bin/python -tt

from vec2d import Vec2d

from flagsfieldgen import FlagsFieldGen


class MasterFieldGen(object):
    def __init__(self, bzrc):
        self.bzrc = bzrc
        self.subfield_generators = [FlagsFieldGen(bzrc)]

    def vector_at(self, x, y):
        resultant_vector = Vec2d(0, 0)

        for fieldGen in self.subfield_generators:
            resultant_vector += fieldGen.vector_at(x, y)

        return resultant_vector
