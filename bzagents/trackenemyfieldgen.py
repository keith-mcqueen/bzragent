#!/usr/bin/python -tt

from vec2d import Vec2d
from masterfieldgen import FieldGen
import time
import numpy
from numpy import matrix
from numpy import linalg

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
        #Matrices for Kalman Agent
        self.mu_t = matrix( [[enemy_base.x],[0],[0],[enemy_base.y],[0],[0]] )
        print self.mu_t
        self.sigma_t = matrix( [[100, 0, 0, 0, 0, 0],[0, 0.1, 0, 0, 0, 0],[0, 0, 0.1, 0, 0, 0],[0, 0, 0, 100, 0, 0],[0, 0, 0, 0, 0.1, 0],[0, 0, 0, 0, 0, 0.1]] )
        self.time_d = .5
        self.friction = 0
        self.F = matrix( [[1, self.time_d, (self.time_d*self.time_d)/2, 0, 0, 0], [0, 1, self.time_d, 0, 0, 0], [0, -self.friction, 1, 0, 0, 0], [0, 0, 0, 1, self.time_d, (self.time_d*self.time_d)/2], [0, 0, 0, 0, 1, self.time_d], [0, 0, 0, 0, -self.friction, 1]]) 
        self.F_T = self.F.transpose();
        self.sigma_x = matrix( [[0.1, 0, 0, 0, 0, 0],[0, 0.1, 0, 0, 0, 0],[0, 0, 100, 0, 0, 0],[0, 0, 0, 0.1, 0, 0],[0, 0, 0, 0, 0.1, 0],[0, 0, 0, 0, 0, 100]] )
        self.H = matrix( [[1,0,0,0,0,0],[0,0,0,1,0,0]] )
        self.H_T = self.H.transpose();
        self.standard_d = 5
        self.sigma_z = matrix( [[self.standard_d*self.standard_d, 0],[0,self.standard_d*self.standard_d]] )
        
        self.last_updated = time.time()

    def vector_at(self, x, y):
        # only worry about one tank
        tank = self.bzrc.get_othertanks()[0]
        
        if time.time() - self.last_updated >= 0.5:
            self.last_updated = time.time()
            F_sigma = self.F.dot(self.sigma_t).dot(self.F_T) + self.sigma_x
            k_matrix = (F_sigma).dot(self.H_T)
            inverse = linalg.inv(self.H.dot(F_sigma).dot(self.H_T) + self.sigma_z)
            k_matrix = k_matrix.dot(inverse)
            self.mu_t = self.F.dot(self.mu_t) + k_matrix.dot(matrix([[tank.x],[tank.y]]) - self.H.dot(self.F).dot(self.mu_t))
            self.sigma_t = (numpy.identity(6) - k_matrix.dot(self.H)).dot(F_sigma)
        
        factor = self.default_factor

        # create a vector for the given location
        location_vector = Vec2d(x, y)

        # prepare the resultant vector
        resultant_vector = Vec2d(0, 0)

        # determine if we should shoot
        shoot = False
        
        # create a vector for the tank's position
        tank_vector = Vec2d(self.mu_t.item(0), self.mu_t.item(3))

        # get the distance between the current tank and the given location
        distance = location_vector.get_distance(tank_vector)
        # normalize the vector to the tank
        force_vector = (tank_vector - location_vector).normalized()

        # scale the vector according as a function of distance
        if distance < self.threshold:
            scale = max(distance / self.threshold, self.min_scale)
        else:
            scale = 1

        if distance < self.shooting_range:
            shoot = shoot or True

        # add the vector to the resultant
        resultant_vector += force_vector * scale * factor

        return resultant_vector, shoot
