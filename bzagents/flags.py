__author__ = 'keith'

from masterfieldgen import FieldGen
from vec2d import Vec2d
import math


class CaptureEnemyFlags(FieldGen):
    def __init__(self, bzrc):
        super(CaptureEnemyFlags, self).__init__(bzrc)

        self.threshold_sqrd = 100.0 ** 2
        self.min_scale = 0.5

        constants = bzrc.get_constants()
        self.team = constants["team"]
        self.world_size_sqrd = int(constants["worldsize"]) ** 2

        self.invocations_before_refresh = 10
        self.invoked = 0
        self.flags = bzrc.get_flags()

    def vector_at(self, x, y):
        # update data if necessary
        self.invoked += 1
        if self.invoked >= self.invocations_before_refresh:
            self.flags = self.bzrc.get_flags()
            self.invoked = 0

        best_distance_sqrd = self.world_size_sqrd
        vector_to_nearest_flag = None

        for flag in self.flags:
            # if the flag is our flag OR the flag is possessed by our team,
            # then skip it
            if flag.color == self.team or flag.poss_color == self.team:
                continue

            # create the vector to the flag
            vector_to_flag = Vec2d(flag.x - x, flag.y - y)

            # if the distance to this flag (squared) beats the current best,
            # then this is the new best
            distance_to_flag_sqrd = vector_to_flag.get_length_sqrd()
            if 0 < distance_to_flag_sqrd < best_distance_sqrd:
                best_distance_sqrd = distance_to_flag_sqrd
                vector_to_nearest_flag = vector_to_flag

        if vector_to_nearest_flag is None:
            return Vec2d(0, 0), False

        # scale the force as a function of distance
        if best_distance_sqrd < self.threshold_sqrd:
            scale = max(math.sqrt(best_distance_sqrd / self.threshold_sqrd), self.min_scale)
        else:
            scale = 1

        return vector_to_nearest_flag.normalized() * scale, False


class DefendTeamFlag(FieldGen):
    def __init__(self, bzrc):
        super(DefendTeamFlag, self).__init__(bzrc)

        self.threshold_sqrd = 30 ** 2
        self.team = bzrc.get_constants()["team"]

        self.invocations_before_refresh = 10
        self.invoked = 0
        self.flags = bzrc.get_flags()

    def vector_at(self, x, y):
        # update data if necessary
        self.invoked += 1
        if self.invoked >= self.invocations_before_refresh:
            self.flags = self.bzrc.get_flags()
            self.invoked = 0

        for flag in self.flags:
            if flag.color != self.team:
                continue

            # create the vector to the flag
            vector_to_flag = Vec2d(flag.x - x, flag.y - y)

            distance_sqrd = vector_to_flag.get_length_sqrd()
            if 0 < distance_sqrd < self.threshold_sqrd:
                scale = math.sqrt(distance_sqrd / self.threshold_sqrd)
            else:
                scale = 1

            return vector_to_flag.normalized() * scale, False


class ReturnToBase(FieldGen):
    def __init__(self, bzrc):
        super(ReturnToBase, self).__init__(bzrc)

        self.team = bzrc.get_constants()["team"]
        for base in bzrc.get_bases():
            if self.team == base.color:
                north = base.corner1_y
                east = base.corner1_x
                south = base.corner3_y
                west = base.corner3_x
                self.my_base = Vec2d((east + west) / 2, (north + south) / 2)
                break

    def vector_at(self, x, y):
        vector_to_base = Vec2d(self.my_base.x - x, self.my_base.y - y)

        return vector_to_base.normalized(), False
