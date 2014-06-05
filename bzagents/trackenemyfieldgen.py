# !/usr/bin/python -tt

import time
import numpy
from numpy import matrix
from numpy import linalg

from masterfieldgen import FieldGen


class TrackEnemyFieldGen(FieldGen):
    def __init__(self, bzrc, default_factor=1):
        super(TrackEnemyFieldGen, self).__init__(bzrc)

        self.threshold = 100
        self.shooting_range = 280
        self.default_factor = default_factor
        self.callsign = bzrc.get_mytanks()[0].callsign

        tank = self.bzrc.get_othertanks()[0]
        bases = self.bzrc.get_bases()
        enemy_base = bases[0]
        for base in bases:
            if base.color == tank.color:
                enemy_base = base
        # Matrices for Kalman Agent
        self.mu_t = matrix([[enemy_base.x],
                            [0],
                            [0],
                            [enemy_base.y],
                            [0],
                            [0]])

        self.sigma_t = matrix([[100, 0, 0, 0, 0, 0],
                               [0, 0.1, 0, 0, 0, 0],
                               [0, 0, 0.1, 0, 0, 0],
                               [0, 0, 0, 100, 0, 0],
                               [0, 0, 0, 0, 0.1, 0],
                               [0, 0, 0, 0, 0, 0.1]])
        self.dt = .5
        self.friction = 0
        self.f = matrix([[1, self.dt, (self.dt ** 2) / 2, 0, 0, 0],
                         [0, 1, self.dt, 0, 0, 0],
                         [0, -self.friction, 1, 0, 0, 0],
                         [0, 0, 0, 1, self.dt, (self.dt ** 2) / 2],
                         [0, 0, 0, 0, 1, self.dt],
                         [0, 0, 0, 0, -self.friction, 1]])
        self.f_transpose = self.f.transpose();
        self.sigma_x = matrix([[0.1, 0, 0, 0, 0, 0],
                               [0, 0.1, 0, 0, 0, 0],
                               [0, 0, 100, 0, 0, 0],
                               [0, 0, 0, 0.1, 0, 0],
                               [0, 0, 0, 0, 0.1, 0],
                               [0, 0, 0, 0, 0, 100]])
        self.h = matrix([[1, 0, 0, 0, 0, 0],
                         [0, 0, 0, 1, 0, 0]])
        self.h_transpose = self.h.transpose();
        self.standard_d = 5
        self.sigma_z = matrix([[self.standard_d * self.standard_d, 0],
                               [0, self.standard_d * self.standard_d]])

        self.last_updated = time.time()

    def get_sigma_t(self):
        return self.sigma_t.item((0,0)), self.sigma_t.item((3,3)), self.mu_t.item((0,0)), self.mu_t.item((3,0))
    
    def vector_at(self, x, y):
        # only worry about one tank
        tank = self.bzrc.get_othertanks()[0]

        if time.time() - self.last_updated >= self.dt:
            self.last_updated = time.time()
            # (F)(Sigma_t)(F_transpose) + Sigma_x
            F_sigma = self.f.dot(self.sigma_t).dot(self.f_transpose) + self.sigma_x

            # K_next =
            k_matrix = (F_sigma).dot(self.h_transpose)
            inverse = linalg.inv(self.h.dot(F_sigma).dot(self.h_transpose) + self.sigma_z)
            k_matrix = k_matrix.dot(inverse)
            self.mu_t = self.f.dot(self.mu_t) + k_matrix.dot(
                matrix([[tank.x], [tank.y]]) - self.h.dot(self.f).dot(self.mu_t))
            # self.mu_t = self.F.dot(self.mu_t)
            self.sigma_t = (numpy.identity(6) - k_matrix.dot(self.h)).dot(F_sigma)

        # get the distance between the current tank and the given location
        # distance = location_vector.get_distance(tank_vector)
        # normalize the vector to the tank
        force_vector = (self.mu_t.item(0) - x, self.mu_t.item(3) - y)

        return force_vector, True
