# !/usr/bin/python -tt

import time
import numpy
from numpy import matrix
from numpy import linalg

from vec2d import Vec2d

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
        self.dt = .1
        self.friction = 0
        self.f = matrix([[1, self.dt, (self.dt ** 2) / 2, 0, 0, 0],
                         [0, 1, self.dt, 0, 0, 0],
                         [0, -self.friction, 1, 0, 0, 0],
                         [0, 0, 0, 1, self.dt, (self.dt ** 2) / 2],
                         [0, 0, 0, 0, 1, self.dt],
                         [0, 0, 0, 0, -self.friction, 1]])
        self.f_transpose = self.f.transpose()
        self.sigma_x = matrix([[0.1, 0, 0, 0, 0, 0],
                               [0, 0.1, 0, 0, 0, 0],
                               [0, 0, 100, 0, 0, 0],
                               [0, 0, 0, 0.1, 0, 0],
                               [0, 0, 0, 0, 0.1, 0],
                               [0, 0, 0, 0, 0, 100]])
        self.h = matrix([[1, 1, 0, 0, 0, 0],
                         [0, 0, 0, 1, 1, 0]])
        self.h_transpose = self.h.transpose()
        self.standard_d = 5
        self.sigma_z = matrix([[self.standard_d * self.standard_d, 0],
                               [0, self.standard_d * self.standard_d]])

        self.last_updated = time.time()

    def vector_at(self, x, y):
        # only worry about one tank
        tank = self.bzrc.get_othertanks()[0]

        if time.time() - self.last_updated >= self.dt:
            self.last_updated = time.time()

            # ######### Compute estimate of where we think the tank *IS*
            # (F)(Sigma_t)(F_transpose) + Sigma_x
            f_sigma = self.f.dot(self.sigma_t).dot(self.f_transpose) + self.sigma_x

            # K_next =
            k_matrix = (f_sigma).dot(self.h_transpose)
            inverse = linalg.inv(self.h.dot(f_sigma).dot(self.h_transpose) + self.sigma_z)
            k_matrix = k_matrix.dot(inverse)
            self.mu_t = self.f.dot(self.mu_t) + k_matrix.dot(
                matrix([[tank.x], [tank.y]]) - self.h.dot(self.f).dot(self.mu_t))
            self.sigma_t = (numpy.identity(6) - k_matrix.dot(self.h)).dot(f_sigma)

            # ######### Now compute where we think the tank *WILL* be
            # self.mu_t = self.f.dot(self.mu_t)

        # get the distance between the current tank and the given location
        # distance = location_vector.get_distance(tank_vector)
        # normalize the vector to the tank
        vector_to_position = Vec2d(self.mu_t.item(0) - x, self.mu_t.item(3) - y)
        target_vector = vector_to_position + Vec2d(self.mu_t.item(1), self.mu_t.item(4))

        return target_vector, True
