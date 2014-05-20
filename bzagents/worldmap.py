#!/usr/bin/python -tt

import numpy as np
import threading

import gridviz


def set_interval(interval):
    def decorator(function):
        def wrapper(*args, **kwargs):
            stopped = threading.Event()

            def loop():  # executed in another thread
                while not stopped.wait(interval):  # until stopped
                    function(*args, **kwargs)

            t = threading.Thread(target=loop)
            t.daemon = True  # stop if the program exits
            t.start()
            return stopped

        return wrapper

    return decorator


class WorldMap(object):
    def __init__(self, bzrc):
        self.bzrc = bzrc
        self.obstacle_threshold = 1
        constants = bzrc.get_constants()
        self.world_size = int(constants['worldsize'])
        self.true_positive = float(constants['truepositive'])
        self.true_negative = float(constants['truenegative'])

        self.default_probability = 0.005

        # create the world grid and fill it with zeroes
        self.world_grid = np.zeros((self.world_size, self.world_size))

        for i in range(self.world_size):
            self.world_grid[i] = self.default_probability
            self.world_grid[:, i] = self.default_probability

        # make the perimeter (the outside walls) of the world an obstacle
        # north
        #self.world_grid[0] = 1
        # south
        #self.world_grid[-1] = 1
        # west
        #self.world_grid[:, 0] = 1
        # east
        #self.world_grid[:, -1] = 1

        gridviz.init_window(self.world_size, self.world_size)
        self.update_grid(bzrc)

    #@set_interval(1.0)
    def update_grid(self, bzrc):
        for tank in bzrc.get_mytanks():
            # if tank is not alive, skip it
            if tank.status != 'alive':
                continue

            #print "getting occ-grid for tank %s" % tank.index
            occ_grid_loc, occ_grid = self.bzrc.get_occgrid(tank.index)

            for x in range(0, len(occ_grid)):
                values = occ_grid[x]

                for y in range(0, len(values)):
                    row, col = self.world_to_grid(x + occ_grid_loc[0], y + occ_grid_loc[1])
                    if row >= self.world_size or col >= self.world_size:
                        break
                    self.world_grid[row, col] = self.update_probability(occ_grid[x][y], self.world_grid[row, col])

        gridviz.update_grid(self.world_grid)
        gridviz.draw_grid()

    def get_edge_from_grid(self, x, y, eff_dist):
        # if the (x, y) is out of bounds, then just return nothing
        if abs(x) > self.world_size / 2 or abs(y) > self.world_size / 2:
            return None

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
            locations_to_visit = []
            north = [(min_row_col, c) for c in range(min_row_col, max_row_col + 1)]
            east = [(r, max_row_col) for r in range(min_row_col + 1, max_row_col + 1)]
            south = [(max_row_col, c) for c in range(max_row_col - 1, min_row_col - 1, -1)]
            west = [(r, min_row_col) for r in range(max_row_col - 1, min_row_col, -1)]

            locations_to_visit.extend(north)
            locations_to_visit.extend(east)
            locations_to_visit.extend(south)
            locations_to_visit.extend(west)

            for (row, col) in locations_to_visit:
                visited_locations.append((row, col))

                if subgrid[row, col] >= self.obstacle_threshold:
                    # we've got a hit, now look around this point to see if
                    # there is another point we can use to assume an edge

                    # create the locations for the surrounding points
                    # (the order we visit may be important)
                    surrounding_locations = [
                        (row - 1, col + 1),
                        (row - 1, col),
                        (row - 1, col - 1),
                        (row, col - 1),
                        (row + 1, col - 1),
                        (row + 1, col),
                        (row + 1, col + 1),
                        (row, col + 1)]
                    for (r, c) in surrounding_locations:
                        # if we've already visited the current location, then skip it
                        if (r, c) in visited_locations:
                            continue

                        # if the row/col is out of bounds, then skip it
                        if r >= subgrid.shape[0] or c >= subgrid.shape[1]:
                            continue

                        # check if the value at row/col is an obstacle
                        if subgrid[r, c] >= self.obstacle_threshold:
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
        #row1, col1 = self.world_to_grid(x - size, y + size)
        row2, col2 = self.world_to_grid(x + (size - 1), y - (size - 1))

        # if the subgrid would extend beyond the walls of the world, then
        # shrink the size of the grid by the overlap amount
        overlap = min(min(min(row1, col1), row2), col2)
        if overlap < 0:
            return self.get_subgrid(x, y, size + overlap)

        overlap = max(max(max(row1, col1), row2), col2)
        if overlap > self.world_size - 1:
            return self.get_subgrid(x, y, size - (overlap - (self.world_size - 1)))

        return self.world_grid[row1:row2 + 1:, col1:col2 + 1], (row1, col1)

    def world_to_grid(self, x, y):
        return (self.world_size / 2) - y, x + (self.world_size / 2)

    def world_to_grid_safe(self, x, y):
        row, col = self.world_to_grid(x, y)
        return min(max(row, 0), self.world_size), min(max(col, self.world_size))

    def grid_to_world(self, row, col):
        return (self.world_size / 2) - col, row - (self.world_size / 2)

    def obstacle_edge_at(self, x, y, distance):
        return self.get_edge_from_grid(x, y, distance)

    def update_probability(self, observed, previous):
        if observed == 1:
            return (self.true_positive * previous / (self.true_positive * previous + (1 - self.true_negative) * (1 - previous)))
        elif observed == 0:
            return ((1 - self.true_positive) * previous / ((1 - self.true_positive) * previous + self.true_negative * (1 - previous)))
        else :
            return previous
            
    def is_unexplored(self, x, y):
        value = self.world_grid[x, y]
        return value > .0000002 and value < .8
