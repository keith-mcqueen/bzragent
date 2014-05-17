#!/usr/bin/python -tt

from vec2d import Vec2d
from masterfieldgen import FieldGen


class WorldMap(object):
    def __init__(self, bzrc):
        self.bzrc = bzrc
        self.edges = []
        for obstacle in bzrc.get_obstacles():
            length = len(obstacle)
            for i in range(0,length):
                self.edges.append((obstacle[i%length],obstacle[(i+1)%length]))
                    

    def obstacle_edge_at(self, x, y, distance):
        best_distance = distance
        nearest_edge = None
        
        # for each obstacle, compute it's effect at the given location
        for edge in self.edges:
			# get the distance from (x,y) to the edge
            current_distance, is_inside_edge = self.retrieve_distance(x,y,edge)		
            if not is_inside_edge:
                continue
				
			# if distance > given distance then skip
            if current_distance > distance:
                continue
				
			# if distance > best current distance then skip
            if current_distance > best_distance:
                continue
				 
			# update best current distance and save nearest edge
            best_distance = current_distance
            nearest_edge = edge
			
		# return nearest edge
        return nearest_edge
	
    def retrieve_distance(self, x, y, edge):
		# calculate the vector between the edge endpoints
        edge_vector = Vec2d(edge[0][0]-edge[1][0],edge[0][1] - edge[1][1])
		
		# calculate the normal vector to the edge
        n = edge_vector.perpendicular_normal()
		
		# calculate the edge's distance from origin
        p1 = Vec2d(edge[0][0],edge[0][1])
        d = p1.dot(n)
		
		# calculate the distance from the point to the edge
        q = Vec2d(x,y)
        q_dot_n = q.dot(n)
        q_prime = q + (d - q_dot_n)*n
        is_inside = min(edge[0][0], edge[1][0]) < q_prime[0] < max(edge[0][0], edge[1][0]) and min(edge[0][1], edge[1][1]) < q_prime[1] < max(edge[0][1], edge[1][1])
        return q_dot_n - d, is_inside
