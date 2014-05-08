#!/usr/bin/python -tt

import sys
import math
import time

from bzrc import BZRC, Command
from Vec2d import Vec2d


class FlagsFieldGen(object):
    def __init__(self, bzrc):
	self.bzrc = bzrc
        self.threshold = 100
        flags = bzrc.get_flags()
        self.callsign = bzrc.get_mytanks()[0].callsign
        self.enemycolors = []
        for flag in flags:
            if not self.callsign.startswith(flag.color):
                self.enemycolors.append(flag.color)
                print flag.color
       
    def vectorAt(self, x, y):
	flags = self.bzrc.get_flags()
	locationVector = Vec2d(x,y)

	resultantVector = Vec2d(0, 0)

        for flag in flags:
            if flag.color in self.enemycolors:
                # We create vector from flags position
                flagVector = Vec2d(flag.x,flag.y)
	    
	        # Get distance between two vectors
	        distance = locationVector.get_distance(flagVector)

	        forceVector = (flagVector - locationVector).normalized()
 	   
	        if distance < self.threshold:
                    scale = distance/self.threshold
                    forceVector = forceVector*scale

		resultantVector += forceVector
                return resultantVector
            
	return resultantVector
	 
