#!/usr/bin/python -tt

# An incredibly simple agent.  All we do is find the closest enemy tank, drive
# towards it, and shoot.  Note that if friendly fire is allowed, you will very
# often kill your own tanks with this code.

#################################################################
# NOTE TO STUDENTS
# This is a starting point for you.  You will need to greatly
# modify this code if you want to do anything useful.  But this
# should help you to know how to interact with BZRC in order to
# get the information you need.
#
# After starting the bzrflag server, this is one way to start
# this code:
# python agent0.py [hostname] [port]
#
# Often this translates to something like the following (with the
# port name being printed out by the bzrflag server):
# python agent0.py localhost 49857
#################################################################

import sys
import math
import time

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
        self.tank_target_angles = [None for _ in range(30)]

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

        # if it's been about 5 seconds, then do something stupid
        for tank in my_tanks:
            self.behave_stupidly(tank, time_diff)

        self.bzrc.do_commands(self.commands)

    def attack_enemies(self, tank):
        """Find the closest enemy and chase it, shooting as you go."""
        best_enemy = None
        best_dist = 2 * float(self.constants['worldsize'])
        for enemy in self.enemies:
            if enemy.status != 'alive':
                continue
            dist = math.sqrt((enemy.x - tank.x) ** 2 + (enemy.y - tank.y) ** 2)
            if dist < best_dist:
                best_dist = dist
                best_enemy = enemy
        if best_enemy is None:
            command = Command(tank.index, 0, 0, False)
            self.commands.append(command)
        else:
            self.move_to_position(tank, best_enemy.x, best_enemy.y)

    def move_to_position(self, tank, target_x, target_y):
        """Set command to move to given coordinates."""
        target_angle = math.atan2(target_y - tank.y,
                                  target_x - tank.x)
        relative_angle = self.normalize_angle(target_angle - tank.angle)
        command = Command(tank.index, 1, 2 * relative_angle, True)
        self.commands.append(command)

    @staticmethod
    def normalize_angle(angle):
        """Make any angle be between +/- pi."""
        angle -= 2 * math.pi * int(angle / (2 * math.pi))
        if angle <= -math.pi:
            angle += 2 * math.pi
        elif angle > math.pi:
            angle -= 2 * math.pi
        return angle

    def behave_stupidly(self, tank, time_diff):
        """Make the tank move forward for a little while, turn left 60 degrees, then shoot"""
        # if the tank's angle is within some margin of the target, stop rotating and then start moving again
        target_angle = self.tank_target_angles[tank.index]
        if target_angle is not None:
            angle_diff = self.normalize_angle(target_angle - tank.angle)
            if abs(angle_diff) <= math.pi / 72:
                self.tank_target_angles[tank.index] = None
                self.commands.append(Command(tank.index, 1, 0, False))

        # if it has been ~5 secs, then...
        if time_diff % 8 < 1:
            # begin rotating the tank
            self.tank_target_angles[tank.index] = self.normalize_angle(tank.angle + math.pi / 3)
            self.commands.append(Command(tank.index, 0, 0.8, False))

        # if it has been ~2 secs, then shoot
        if time_diff % 2 < 1:
            self.commands.append(Command(tank.index, shoot=True))


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
