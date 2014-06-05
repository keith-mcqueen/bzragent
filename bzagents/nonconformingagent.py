# !/usr/bin/python -tt

import sys
import time
import random

from vec2d import Vec2d
from bzrc import BZRC
from pfagent import Agent
from obstacles import WorldBoundaries
from enemies import Enemies


class NonConformingAgent(Agent):
    """Class handles all command and control logic for a teams tanks."""

    def __init__(self, bzrc):
        super(NonConformingAgent, self).__init__(bzrc)

        self.invocations_before_update = 0
        self.invocation_count = 0
        self.boundaries = WorldBoundaries(bzrc)
        self.enemies = Enemies(bzrc)
        self.last_vector = Vec2d(0.0, 0.0)

    def get_field_vector(self, tank):
        if self.invocation_count < self.invocations_before_update:
            self.invocation_count += 1
            return self.last_vector, False

        self.invocation_count = 0
        self.invocations_before_update = random.randrange(100, 1000)

        field_vec, shoot = self.field.vector_at(tank.x, tank.y)
        if field_vec.x != 0 or field_vec.y != 0:
            self.last_vector = field_vec
            return field_vec, False

        field_vec, shoot = self.enemies.vector_at(tank.x, tank.y)
        if field_vec.x != 0 or field_vec.y != 0:
            self.last_vector = field_vec
            return field_vec, False

        vx = random.uniform(-1.0, 1.0)
        vy = random.uniform(-1.0, 1.0)
        scale = random.uniform(-1.0, 1.0)
        self.last_vector = Vec2d(vx, vy).normalized()
        return self.last_vector * scale, False


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

    agent = NonConformingAgent(bzrc)

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
