#!/usr/bin/python -tt

import sys
import math
import time

from bzrc import BZRC, Command
from vec2d import Vec2d


class Agent(object):
    """Class handles all command and control logic for a teams tanks."""

    def __init__(self, bzrc):
        self.bzrc = bzrc
        self.constants = self.bzrc.get_constants()
        self.commands = []
        self.my_tanks = []
        self.other_tanks = []
        self.flags = []
        self.shots = []
        self.enemies = []

    def tick(self, time_diff):
        """Some time has passed; decide what to do next."""
        my_tanks, other_tanks, flags, shots = self.bzrc.get_lots_o_stuff()
        self.my_tanks = my_tanks
        self.other_tanks = other_tanks
        self.flags = flags
        self.shots = shots
        self.enemies = [tank for tank in other_tanks if tank.color != self.constants['team']]

        # clear the commands
        self.commands = []

        for tank in my_tanks:
            self.direct_tank(tank)

        self.bzrc.do_commands(self.commands)

    def direct_tank(self, tank):
        # get the tank's velocity vector
        tank_vector = Vec2d(tank.vx, tank.vy)

        # get vector(s) for the potential fields around the tank
        field_vectors = self.get_field_vectors(tank)

        # add up all the vector(s) from the potential fields to get the desired vector
        # subtract the tank's current vector from the desired vector to get the change vector?
        # use the change vector to get the tank to the desired vector?

    def get_field_vectors(self, tank):
        # where do I get the potential fields from?
        # it would be nice if they were passed in as arguments to the __init__ method, or something
        # it would also be nice if they were stored in a list so I could just iterate over them
        #   then I could just invoke the same method on each one (something like, pf.get_vector(<bzrc>, <tank_loc>)
        # collect the results into a list and return them
        # --OR--
        # do the vector sum here and return the resultant vector
        pass

    def move_to_position(self, tank, target_x, target_y):
        """Set command to move to given coordinates."""
        target_angle = math.atan2(target_y - tank.y,
                                  target_x - tank.x)
        relative_angle = self.normalize_angle(target_angle - tank.angle)
        self.commands.append(Command(tank.index, 1, 2 * relative_angle, True))

    @staticmethod
    def normalize_angle(angle):
        """Make any angle be between +/- pi."""
        angle -= 2 * math.pi * int(angle / (2 * math.pi))
        if angle <= -math.pi:
            angle += 2 * math.pi
        elif angle > math.pi:
            angle -= 2 * math.pi
        return angle


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

    agent = Agent(bzrc)

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
