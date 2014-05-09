#!/usr/bin/python -tt

from vec2d import Vec2d

from flagsfieldgen import FlagsFieldGen
from enemiesfieldgen import EnemiesFieldGen
from obstaclesfieldgen import ObstaclesFieldGen
from basesfieldgen import BasesFieldGen


class MasterFieldGen(object):
    def __init__(self, bzrc):
        self.bzrc = bzrc
        self.subfield_generators = [FlagsFieldGen(bzrc),
                                    EnemiesFieldGen(bzrc),
                                    ObstaclesFieldGen(bzrc),
                                    BasesFieldGen(bzrc)]
        #self.subfield_generators = [FlagsFieldGen(bzrc)]
        #self.subfield_generators = [EnemiesFieldGen(bzrc)]
        #self.subfield_generators = [ObstaclesFieldGen(bzrc)]
        #self.subfield_generators = [BasesFieldGen(bzrc)]
        #self.subfield_generators = []

    def vector_at(self, x, y):
        resultant_vector = Vec2d(0, 0)

        do_shoot = False
        for fieldGen in self.subfield_generators:
            field_vector, shoot = fieldGen.vector_at(x, y)
            resultant_vector += field_vector
            do_shoot = do_shoot or shoot

        return resultant_vector, do_shoot
