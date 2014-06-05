
#!/usr/bin/python -tt

import math
import sys
import time
import random

from bzrc import BZRC
from vec2d import Vec2d
from obstacles import WorldBoundaries
from enemies import Enemies
from pfagent import Agent


class StraightAgent(Agent):
    """Class handles all command and control logic for a teams tanks."""
    def __init__(self, bzrc):
        super(StraightAgent, self).__init__(bzrc)

        self.target_velocity = random.uniform(0.5, 1)
        self.boundaries = WorldBoundaries(bzrc)
        self.enemies = Enemies(bzrc)

    def get_field_vector(self, tank):
        field_vec, shoot = self.boundaries.vector_at(tank.x, tank.y)
        if field_vec.x != 0 or field_vec.y != 0:
            return field_vec, False

        field_vec, shoot = self.enemies.vector_at(tank.x, tank.y)
        if field_vec.x != 0 or field_vec.y != 0:
            return field_vec, False

        # if the tank has some velocity, then just use that
        if tank.vx != 0 and tank.vy != 0:
            return Vec2d(tank.vx, tank.vy), False

        # just go in the direction that the tank is currently pointing
        return Vec2d(math.cos(tank.angle), math.sin(tank.angle)), False


def main():
    # Process CLI arguments.
    try:
        execname, host, port = sys.argv
    except ValueError:
        execname = sys.argv[0]
        print >> sys.stderr, '%s: incorrect number of arguments' % execname
        print >> sys.stderr, 'usage: %s hostname port' % sys.argv[0]
        sys.exit(-1)

    # Connect.
    #bzrc = BZRC(host, int(port), debug=True)
    bzrc = BZRC(host, int(port))

    agent = StraightAgent(bzrc)

    prev_time = time.time()

    # Run the agent
    try:
        while True:
            time_diff = time.time() - prev_time
            agent.tick(time_diff)
    except KeyboardInterrupt:
        print "Exiting due to keyboard interrupt."
        bzrc.close()


if __name__ == '__main__':
    main()

# vim: et sw=4 sts=4
