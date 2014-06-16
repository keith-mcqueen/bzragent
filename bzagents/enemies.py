__author__ = 'keith'

import time
import numpy
import math
from numpy import matrix
from numpy import linalg

from vec2d import Vec2d
from masterfieldgen import FieldGen



# Should share one instance of this class with any object that needs to know enemy tanks'
# location to avoid redundancy of computing the Kalman matrices in multiple places.


class Kalman(object):
    def __init__(self, bzrc):
        self.bzrc = bzrc
        self.dt = .1
        self.friction = 0
        # these matrices never change, so can have one copy for all tanks
        self.f = matrix([[1, self.dt, (self.dt ** 2) / 2, 0, 0, 0],
                         [0, 1, self.dt, 0, 0, 0],
                         [0, -self.friction, 1, 0, 0, 0],
                         [0, 0, 0, 1, self.dt, (self.dt ** 2) / 2],
                         [0, 0, 0, 0, 1, self.dt],
                         [0, 0, 0, 0, -self.friction, 1]])
        self.f_transpose = self.f.transpose()
        self.sigma_x = matrix([[0.1, 0, 0, 0, 0, 0],
                               [0, 0.1, 0, 0, 0, 0],
                               [0, 0, 70, 0, 0, 0],
                               [0, 0, 0, 0.1, 0, 0],
                               [0, 0, 0, 0, 0.1, 0],
                               [0, 0, 0, 0, 0, 70]])
        self.h = matrix([[1, 1, 0, 0, 0, 0],
                         [0, 0, 0, 1, 1, 0]])
        self.h_transpose = self.h.transpose()
        self.standard_d = 5
        self.sigma_z = matrix([[self.standard_d * self.standard_d, 0],
                               [0, self.standard_d * self.standard_d]])
        # keep arrays of the Kalman matrices to keep track of all enemy tanks
        self.mu_t = []
        self.sigma_t = []

        # assuming get_othertanks always returns tanks in the same order
        bases = self.bzrc.get_bases()
        tanks = self.bzrc.get_othertanks()
        enemy_base = bases[0]
        for tank in tanks:
            for base in bases:
                if base.color == tank.color:
                    enemy_base = base
                    break

            self.mu_t.append(matrix([[enemy_base.x],
                                     [0],
                                     [0],
                                     [enemy_base.y],
                                     [0],
                                     [0]]))

            self.sigma_t.append(matrix([[100, 0, 0, 0, 0, 0],
                                        [0, 0.1, 0, 0, 0, 0],
                                        [0, 0, 0.1, 0, 0, 0],
                                        [0, 0, 0, 100, 0, 0],
                                        [0, 0, 0, 0, 0.1, 0],
                                        [0, 0, 0, 0, 0, 0.1]]))

        self.last_updated = time.time()

    def get_sigma_t(self, index):
        self.update_matrices()
        return self.sigma_t[index].item((0, 0)), self.sigma_t[index].item((3, 3)), self.mu_t[index].item((0, 0)), \
               self.mu_t[index].item((3, 0))

    def get_mu_t(self, index):
        self.update_matrices()
        # Return where we think the tank *WILL* be
        return self.f.dot(self.mu_t[index])

    # We might just want to update each tank at a separate time interval so this method will run quicker
    def update_matrices(self):
        if time.time() - self.last_updated >= self.dt:
            self.last_updated = time.time()
            tanks = self.bzrc.get_othertanks()
            index = 0
            for tank in tanks:
                # ignore dead enemy tanks
                if not tank.status.startswith('alive'):
                    continue
                # ######### Compute estimate of where we think the tank *IS*
                # (F)(Sigma_t)(F_transpose) + Sigma_x
                f_sigma = self.f.dot(self.sigma_t[index]).dot(self.f_transpose) + self.sigma_x

                # K_next =
                k_matrix = (f_sigma).dot(self.h_transpose)
                inverse = linalg.inv(self.h.dot(f_sigma).dot(self.h_transpose) + self.sigma_z)
                k_matrix = k_matrix.dot(inverse)
                self.mu_t[index] = self.f.dot(self.mu_t[index]) + k_matrix.dot(
                    matrix([[tank.x], [tank.y]]) - self.h.dot(self.f).dot(self.mu_t[index]))
                self.sigma_t[index] = (numpy.identity(6) - k_matrix.dot(self.h)).dot(f_sigma)


class Enemies(FieldGen):
    def __init__(self, bzrc):
        super(Enemies, self).__init__(bzrc)

        self.effective_range_sqrd = 50 ** 2
        # self.shooting_range_sqrd = 30 ** 2
        self.kalman = Kalman(self.bzrc)

        self.other_tanks = self.bzrc.get_othertanks()

        self.time_diff = 1
        self.last_time = time.time() - self.time_diff

    def vector_at(self, x, y):
        # update data if necessary
        if time.time() - self.last_time >= self.time_diff:
            self.other_tanks = self.bzrc.get_othertanks()
            self.last_time = time.time()

        # go through all the tanks, but only worry about the first one that is within range
        for tank in self.other_tanks:
            if not tank.status.startswith('alive'):
                continue

            vector_to_tank = Vec2d(x - tank.x, y - tank.y)

            # get the distance between the current tank and the given location
            distance_sqrd = vector_to_tank.get_length_sqrd()
            if 0 < distance_sqrd < self.effective_range_sqrd:
                return vector_to_tank.normalized() * 50.0 / math.sqrt(distance_sqrd), True

        return Vec2d(0, 0), False


class Attack(FieldGen):
    def __init__(self, bzrc, range):
        super(Attack, self).__init__(bzrc)

        self.kalman = Kalman(self.bzrc)
        self.threshold = range ** 2
        self.other_tanks = self.bzrc.get_othertanks()

        self.time_diff = 0.1
        self.last_time = time.time() - self.time_diff

    def vector_at(self, x, y):
        # update data if necessary
        if time.time() - self.last_time >= self.time_diff:
            self.other_tanks = self.bzrc.get_othertanks()
            self.last_time = time.time()

        # compute the distance without the square root to speed up computation since it is only used
        # to find which enemy tank is the closest
        # nearest = (x - tank.x) ** 2 + (y - tank.y) ** 2
        nearest = self.threshold
        index = -1
        i = 0
        for enemy in self.other_tanks:
            # skip dead tanks
            if not enemy.status.startswith('alive'):
                continue

            distance = (x - enemy.x) ** 2 + (y - enemy.y) ** 2
            if distance < nearest:
                nearest = distance
                index = i
            i += 1

        # if self.use_threshold and nearest > self.threshold:
        # return Vec2d(0, 0), False
        if index < 0:
            return Vec2d(0, 0), True

        mu_t = self.kalman.get_mu_t(index)

        enemy_position = Vec2d(mu_t.item(0) - x, mu_t.item(3) - y)
        enemy_distance = enemy_position.get_length() / 40
        enemy_velocity = Vec2d(mu_t.item(1), mu_t.item(4)) * enemy_distance
        target_vector = enemy_position + enemy_velocity

        return target_vector, True
