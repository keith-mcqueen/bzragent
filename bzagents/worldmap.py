#!/usr/bin/python -tt

from vec2d import Vec2d
from masterfieldgen import FieldGen


class WorldMap(object):
    def __init__(self, bzrc):
		self.bzrc = bzrc
		self.edges = []
		for obstacle in bzrc.get_obstacles():
			self.edges.append([(obstacle[0],obstacle[1]),
			                   (obstacle[1],obstacle[2]),
			                   (obstacle[2],obstacle[3]),
			                   (obstacle[3],obstacle[4])])        

    def obstacle_edge_at(self, x, y, distance):
        best_distance = distance
        nearest_edge = None
        
        # for each obstacle, compute it's effect at the given location
        for edge in self.edges:
			
			# get the distance from (x,y) to the edge
			# if distance > given distance then skip
			# if distance > best current distance then skip
			# update best current distance and save nearest edge
			
		# return nearest edge
        return nearest_edge
