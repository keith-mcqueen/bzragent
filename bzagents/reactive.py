#!/usr/bin/python -tt

# An agent currently only using attractive fields.
# Always shoots when possible

import sys
import math
import time

from attractive import Attractive
from tangential import Tangential
from bzrc import BZRC, Command


class Agent(object):
    """Class handles all command and control logic for a teams tanks."""

    def __init__(self, bzrc):
        self.bzrc = bzrc
        self.constants = self.bzrc.get_constants()
        self.obstacles = self.bzrc.get_obstacles()
        self.bases = self.bzrc.get_bases()
        self.commands = []

    def tick(self, time_diff):
        """Some time has passed; decide what to do next."""
        mytanks, othertanks, flags, shots = self.bzrc.get_lots_o_stuff()
        self.mytanks = mytanks
        self.othertanks = othertanks
        self.flags = flags
        self.shots = shots
        self.enemies = [tank for tank in othertanks if tank.color !=
                                                       self.constants['team']]

        self.commands = []

        #one tank for each flag, yes this includes our own flag
        self.use_potential_fields(mytanks[0], self.flags[0])
        self.use_potential_fields(mytanks[1], self.flags[1])
        self.use_potential_fields(mytanks[2], self.flags[2])
        self.use_potential_fields(mytanks[3], self.flags[3])

        results = self.bzrc.do_commands(self.commands)

    def move_to_position(self, tank, target_x, target_y):
        """Set command to move to given coordinates."""
        target_angle = math.atan2(target_y - tank.y,
                                  target_x - tank.x)
        relative_angle = self.normalize_angle(target_angle - tank.angle)
        command = Command(tank.index, 1, 2 * relative_angle, True)
        self.commands.append(command)

    def use_potential_fields(self, tank, flag):
        goal = flag
        if tank.flag != '-':
            goal = self.bases[0]
            for dest in self.bases:
                if dest.color == 'red':
                    goal = dest
                    break

        pull = Attractive(goal)
        field = pull.get_vector(tank)
        #Add repulsive and tangential fields here to the field variable
        for obstacle in self.obstacles:
            wall = Tangential(obstacle)
            tangent = wall.get_vector(tank)
            field += tangent

        target_angle = field.angle
        relative_angle = self.normalize_angle(target_angle - tank.angle)
        command = Command(tank.index, field.get_length(), 2 * relative_angle, True)
        self.commands.append(command)

    def normalize_angle(self, angle):
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
