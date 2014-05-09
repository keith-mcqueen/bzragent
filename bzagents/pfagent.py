#!/usr/bin/python -tt

import sys
import math
import time

from masterfieldgen import MasterFieldGen
from bzrc import BZRC, Command


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

        self.master_field_gen = MasterFieldGen(bzrc)

    def tick(self, time_diff):
        """Some time has passed; decide what to do next."""
        # my_tanks, other_tanks, flags, shots = self.bzrc.get_lots_o_stuff()
        # self.my_tanks = my_tanks
        # self.other_tanks = other_tanks
        # self.flags = flags
        # self.shots = shots
        # self.enemies = [tank for tank in other_tanks if tank.color != self.constants['team']]

        # clear the commands
        self.commands = []

        for tank in self.bzrc.get_mytanks():
            self.direct_tank(tank)

        self.bzrc.do_commands(self.commands)

    def direct_tank(self, tank):
        # get vector(s) for the potential fields around the tank
        field_vector = self.get_field_vector(tank)
        self.move_to_position(tank, field_vector[0], field_vector[1])
        self.commands.append(Command(tank.index, speed=field_vector.get_length()))

    def get_field_vector(self, tank):
        return self.master_field_gen.vector_at(tank.x, tank.y)

    def move_to_position(self, tank, target_x, target_y):
        """Set command to move to given coordinates."""
        target_angle = math.atan2(target_y - tank.y,
                                  target_x - tank.x)
        relative_angle = self.normalize_angle(target_angle - tank.angle)
        self.commands.append(Command(tank.index, 1, 2 * relative_angle, False))

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
