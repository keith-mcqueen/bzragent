
#!/usr/bin/python -tt

import sys
import math
import time

from masterfieldgen import MasterFieldGen
from basesfieldgen import ReturnToBaseFieldGen
from flagsfieldgen import FlagsFieldGen
from flagsfieldgen import RecoverFlagFieldGen
from enemiesfieldgen import EnemiesFieldGen
from obstaclesfieldgen import ObstaclesFieldGen
from basesfieldgen import LeaveHomeBaseFieldGen
from worldmap import WorldMap
from explorefieldgen import ExploreFieldGen
from bzrc import BZRC, Command
from vec2d import Vec2d
import random


class Agent(object):
    """Class handles all command and control logic for a teams tanks."""

    def __init__(self, bzrc):
        self.bzrc = bzrc
        self.constants = self.bzrc.get_constants()
        self.commands = []
        self.last_time_diff = 0
        self.target_angle = 0
        self.target_velocity = random.uniform(.1, 1)

    def tick(self, time_diff):
        """Some time has passed; decide what to do next."""
        # clear the commands
        self.commands = []

        # calculate the time differential
        d_t = time_diff - self.last_time_diff

        # save the current time_diff for next time (no pun intended)
        self.last_time_diff = time_diff

        for tank in self.bzrc.get_mytanks():
            if tank.status.startswith('alive'):  # and tank.index == 0:
                self.direct_tank(tank, d_t)

        self.bzrc.do_commands(self.commands)

    def direct_tank(self, tank, time_diff):
        # get the angle between the desired and current vectors
        angle = self.normalize_angle(self.target_angle)
        
        # now set the speed and angular velocity
        self.commands.append(Command(tank.index, self.target_velocity, angle, False))

   

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
