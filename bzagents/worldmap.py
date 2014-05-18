#!/usr/bin/python -tt

import numpy as np

from vec2d import Vec2d


class WorldMap(object):
    def __init__(self, bzrc):
        self.bzrc = bzrc
        self.obstacle_threshold = 1
        self.world_size = bzrc.get_constants()['worldsize']

        # create the world grid and fill it with zeroes
        self.world_grid = np.zeros((self.world_size, self.world_size))

        # make the perimeter (the outside walls) of the world an obstacle
        self.world_grid[0] = 1
        self.world_grid[:, 0] = 1
        self.world_grid[self.world_size - 1] = 1
        self.world_grid[:, self.world_size - 1] = 1

        self.edges = []

        self.init_grid(bzrc)

        for obstacle in bzrc.get_obstacles():
            length = len(obstacle)
            for i in range(0, length):
                self.edges.append([(obstacle[i % length], obstacle[(i + 1) % length])])

    def init_grid(self, bzrc):
        # init a grid with default values
        #   - the sample code for the visualization says that it expects us to
        #     use a numpy.array (so we probably should)
        #   - the grid represents the world, so we can make it 800x800, or we
        #     can subdivide into "cells" of a certain size
        #   - provide initial values for the array; couple of choices here:
        #       - 1: fill the array with zeroes (and we'll update later with
        #           our initial guess as we wander the field)
        #           - the pro here is that we can distinguish where we have
        #             visited and where we have not by having a different value
        #             than our initial guess
        #       - 2: fill the grid with our initial guess
        #           - the pro here is that the grid is fully initialized with
        #               probabilities, even if they are just our initial guesses
        world_size = int(bzrc.get_constants()['worldsize'])
        self.world_grid = np.zeros((world_size, world_size))

        for obstacle in bzrc.get_obstacles():
            pass

        pass

    def get_edge_from_grid(self, x, y, eff_dist):
        # get a subgrid of the world centered at (x, y) with (max) width and
        # height of 2*eff_dist (we'll also get the offset of the subgrid within
        # the world grid, to help us translate locations)
        subgrid, offset = self.get_subgrid(x, y, eff_dist)

        visited_locations = []
        iterations = subgrid.shape[1] / 2
        for i in range(1, iterations + 1):
            # compute the min/max row/col (the corners) of the square that we
            # will walk around
            min_row_col = iterations - i
            max_row_col = iterations + i - 1

            # compute all the locations to visit as we walk around the center
            # of the subgrid looking for an obstacle
            locations_to_visit = [(int(row), min_row_col) for row in range(min_row_col, max_row_col + 1)]
            locations_to_visit.extend([(max_row_col, int(col)) for col in range(min_row_col + 1, max_row_col + 1)])
            locations_to_visit.extend([(int(row), max_row_col) for row in range(max_row_col + 1, min_row_col - 1, -1)])
            locations_to_visit.extend([(min_row_col, int(col)) for col in range(max_row_col - 1, min_row_col - 1), -1])

            for (row, col) in locations_to_visit:
                visited_locations.append((row, col))
                if subgrid[row, col] >= self.obstacle_threshold:
                    # we've got a hit, now look around this point to see if
                    # there is another point we can use to assume an edge

                    # create the locations for the surrounding points
                    surrounding_locations = [
                        (row - 1, col - 1),
                        (row - 1, col),
                        (row - 1, col + 1),
                        (row, col - 1),
                        (row, col + 1),
                        (row + 1, col - 1),
                        (row + 1, col),
                        (row + 1, col + 1)]
                    for (r, c) in surrounding_locations:
                        if (r, c) not in visited_locations and subgrid[r, c] >= self.obstacle_threshold:
                            # it looks like we have an edge, so create the two
                            # endpoints and return them
                            ep1 = self.grid_to_world(row + offset[0], col + offset[1])
                            ep2 = self.grid_to_world(r + offset[0], c + offset[1])

                            return ep1, ep2

        return None

    def get_subgrid(self, x, y, size):
        # get a subview of the world grid centered at (x, y) with width and
        # height of (2*eff_dist)
        row1, col1 = self.world_to_grid(x - size, y + size)
        row2, col2 = self.world_to_grid(x + size, y - size)

        # if the subgrid would extend beyond the walls of the world, then
        # shrink the size of the grid by the overlap amount
        overlap = min(min(min(row1, col1), row2), col2)
        if overlap < 0:
            return self.get_subgrid(x, y, size + overlap)

        return self.world_grid[row1:row2 + 1:, col1:col2 + 1], (row1, col1)

    def world_to_grid(self, x, y):
        return x + (self.world_size / 2), (self.world_size / 2) - y

    def world_to_grid_safe(self, x, y):
        row, col = self.world_to_grid(x, y)
        return min(max(row, 0), self.world_size), min(max(col, self.world_size))

    def grid_to_world(self, row, col):
        return row - (self.world_size / 2), (self.world_size / 2) - col

    def obstacle_edge_at(self, x, y, distance):
        nearest_edge = self.get_edge_from_grid(x, y, distance)
        if nearest_edge is not None:
            return nearest_edge

        best_distance = distance
        nearest_edge = None

        # for each obstacle, compute it's effect at the given location
        for edge in self.edges:
            # get the distance from (x,y) to the edge
            current_distance, is_inside_edge = self.retrieve_distance(x, y, edge)
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
        edge_vector = Vec2d(edge[0][0] - edge[1][0], edge[0][1] - edge[1][1])

        # calculate the normal vector to the edge
        n = edge_vector.perpendicular_normal()

        # calculate the edge's distance from origin
        p1 = Vec2d(edge[0][0], edge[0][1])
        d = p1.dot(n)

        # calculate the distance from the point to the edge
        q = Vec2d(x, y)
        q_dot_n = q.dot(n)
        q_prime = q + (d - q_dot_n) * n
        is_inside = min(edge[0][0], edge[1][0]) < q_prime[0] < max(edge[0][0], edge[1][0]) and min(edge[0][1],
                                                                                                   edge[1][1]) < \
                                                                                               q_prime[1] < max(
            edge[0][1], edge[1][1])
        return q_dot_n - d, is_inside
