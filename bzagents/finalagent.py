#!/usr/bin/python -tt

import sys
import math
import time

from bzrc import BZRC, Command
from vec2d import Vec2d

from obstaclesfieldgen import ObstaclesFieldGen
from obstacles import WorldBoundaries, ObstaclesTangential, ObstaclesNormal
from enemies import Kalman, Enemies, Attack
from flags import CaptureEnemyFlags, DefendTeamFlag, ReturnToBase
from worldmap import WorldMap

class Agent(object):
    """Class handles all command and control logic for a teams tanks."""

    def __init__(self, bzrc):
        self.bzrc = bzrc
        self.constants = self.bzrc.get_constants()
        # This is used to determined what each tank will do and duties at the end are lost first as our tanks die
        self.duties = ["capture", "defend", "attack", "capture", "defend", "attack", "capture", "defend", "attack", "capture"]
        self.commands = []
        self.my_tanks = []
        self.other_tanks = []
        self.flags = []
        self.shots = []
        self.enemies = []
        self.angle_diffs_by_tank = {}
        
        self.kalman = Kalman(bzrc)
        self.world_map = WorldMap(bzrc)

        obstacles = ObstaclesFieldGen(bzrc, self.world_map)
        #world_boundaries = WorldBoundaries(bzrc)
        #obstacles_normal = ObstaclesNormal(bzrc)
        #obstacles_tangential = ObstaclesTangential(bzrc)
        enemies = Enemies(bzrc, self.kalman)
        capture_enemy_flags = CaptureEnemyFlags(bzrc)
        defend_team_flag = DefendTeamFlag(bzrc)
        return_to_base = ReturnToBase(bzrc)
        attack = Attack(bzrc, self.kalman)
        attack_nearby = Attack(bzrc, self.kalman, True)

        self.behaviors = {
            "capture": [
                obstacles
#                world_boundaries
#                , obstacles_tangential
#                , obstacles_normal
                , enemies
                , capture_enemy_flags
            ],
            "defend": [
                obstacles
#                world_boundaries
#                , obstacles_tangential
#                , obstacles_normal
                , attack_nearby
                , defend_team_flag
            ],
            "return-to-base": [
                obstacles
#                world_boundaries
#                , obstacles_tangential
#                , obstacles_normal
                , enemies
                , return_to_base
            ],
            "attack": [
                obstacles
#                world_boundaries
#                , obstacles_tangential
#                , obstacles_normal
                , attack
            ]
        }

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
        self.dead = 0
        
        for tank in self.bzrc.get_mytanks():
            if tank.status.startswith('alive'):  # and tank.index == 0:
                self.direct_tank(tank, d_t)
            else:
                self.dead += 1

        self.bzrc.do_commands(self.commands)

    def direct_tank(self, tank, time_diff):
        # get vector(s) for the potential fields around the tank (this is the vector I want the tank to have)
        field_vector, shoot = self.get_field_vector(tank)

        # get the tank's current velocity vector
        tank_vector = Vec2d(tank.vx, tank.vy)

        # get the angle between the desired and current vectors
        angle_diff = self.normalize_angle(tank_vector.get_angle_between(field_vector))
        if tank.callsign in self.angle_diffs_by_tank:
            last_angle_diff = self.angle_diffs_by_tank[tank.callsign]
        else:
            last_angle_diff = angle_diff
            self.angle_diffs_by_tank[tank.callsign] = angle_diff

        d_e = (angle_diff - last_angle_diff) / (time_diff if time_diff != 0 else 0.01)
        angvel = (self.k_p * angle_diff) + (self.k_d * d_e)

        # now set the speed and angular velocity
        self.commands.append(Command(tank.index, field_vector.get_length(), angvel, abs(angle_diff) < math.radians(3.0)))

    def get_field_vector(self, tank):
        # if the tank doesn't have a flag, then either go get a flag,
        # or defend our own flag
        if tank.flag == '-':
            return self.vector_at(self.duties[tank.index - self.dead], tank.x, tank.y)

        # tank has a flag, so get back to base ASAP
        return self.vector_at("return-to-base", tank.x, tank.y)

    @staticmethod
    def normalize_angle(angle):
        """Make any angle be between +/- pi."""
        angle -= 2 * math.pi * int(angle / (2 * math.pi))
        if angle <= -math.pi:
            angle += 2 * math.pi
        elif angle > math.pi:
            angle -= 2 * math.pi
        return angle

    def vector_at(self, behavior, x, y):
        resultant_vector = Vec2d(0, 0)

        do_shoot = False
        for field in self.behaviors[behavior]:
            field_vec, shoot = field.vector_at(x, y)

            resultant_vector += field_vec
            do_shoot = do_shoot or shoot

        return resultant_vector, do_shoot


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
