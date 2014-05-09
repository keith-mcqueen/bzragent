#!/usr/bin/python -tt
import abc

from vec2d import Vec2d


class FieldGen(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, bzrc):
        self.bzrc = bzrc

    @abc.abstractmethod
    def vector_at(self, x, y):
        return


class MasterFieldGen(FieldGen):
    def __init__(self, bzrc, subfield_generators):
        super(MasterFieldGen, self).__init__(bzrc)

        self.subfield_generators = subfield_generators

    def vector_at(self, x, y):
        resultant_vector = Vec2d(0, 0)

        do_shoot = False
        for fieldGen in self.subfield_generators:
            field_vector, shoot = fieldGen.vector_at(x, y)
            resultant_vector += field_vector
            do_shoot = do_shoot or shoot

        return resultant_vector, do_shoot
