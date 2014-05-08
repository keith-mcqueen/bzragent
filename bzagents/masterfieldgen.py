#!/usr/bin/python -tt

import sys
import math
import time

from bzrc import BZRC, Command
from Vec2d import Vec2d

from flagsfieldgen import FlagsFieldGen


class MasterFieldGen(object):

    def __init__(self, bzrc):
        self.bzrc = bzrc
        self.subFieldGens = [FlagsFieldGen(bzrc)]
    
    def vectorAt(self, x, y):
        resultantVector = Vec2d(0,0)

        for fieldGen in self.subFieldGens:
            resultantVector.__iadd__(fieldGen.vectorAt(x,y))
	
	return resultantVector
	       
