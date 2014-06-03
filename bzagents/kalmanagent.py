#!/usr/bin/python -tt

import sys
import math
import time

from masterfieldgen import MasterFieldGen
from trackenemyfieldgen import TrackEnemyFieldGen
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
        self.angle_diffs_by_tank = {}

        self.track_enemy_strategy = MasterFieldGen(bzrc, [(TrackEnemyFieldGen(bzrc))])

        self.last_time_diff = 0
        self.k_p = 0.1
        self.k_d = 0.5

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
        # get vector(s) for the potential fields around the tank (this is the vector I want the tank to have)
        field_vector, shoot = self.get_field_vector(tank)
        # get the tank's current velocity vector
        tank_vector = Vec2d(tank.vx, tank.vy)
        if tank_vector[0] == 0 and tank_vector[1] == 0:
            tank_vector[0] = 1
            tank_vector.angle = math.degrees(tank.angle)
        
        # get the angle between the desired and current vectors
        angle_diff = self.normalize_angle(tank_vector.get_angle_between(field_vector))
        if tank.callsign in self.angle_diffs_by_tank:
            last_angle_diff = self.angle_diffs_by_tank[tank.callsign]
        else:
            last_angle_diff = angle_diff
            self.angle_diffs_by_tank[tank.callsign] = angle_diff
        
        #d_e = (angle_diff - last_angle_diff) / (time_diff if time_diff != 0 else 0.01)
        angvel = angle_diff#(self.k_p * angle_diff) + (self.k_d * d_e)
        
        # for Kalman lab, the agent can only rotate, so keep velocity at 0
        self.commands.append(Command(tank.index, 0, angvel, shoot and angle_diff < .5))

    def get_field_vector(self, tank):
        return self.track_enemy_strategy.vector_at(tank.x, tank.vy)

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

