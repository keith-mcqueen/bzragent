import math

from vec2d import Vec2d


class Attractive(object):
    """Contains logic for creating and using an attractive field"""

    def __init__(self, goal):
        self.goal = goal

    def get_angle(self, tank):
        f = Vec2d(self.goal.x - tank.x, self.goal.y - tank.y)
        angle = f.angle
        return self.normalize_angle(angle)

    def get_pull(self, tank):
        dist = math.sqrt((self.goal.x - tank.x) ** 2 + (self.goal.y - tank.y) ** 2)
        if dist > 50:
            dist = 50
        return dist / 10

    def get_vector(self, tank):
        pull = self.get_pull(tank)
        vector = Vec2d(self.goal.x - tank.x, self.goal.y - tank.y)
        vector.length = pull
        return vector

    def normalize_angle(self, angle):
        """Make any angle be between +/- pi."""
        angle -= 2 * math.pi * int(angle / (2 * math.pi))
        if angle <= -math.pi:
            angle += 2 * math.pi
        elif angle > math.pi:
            angle -= 2 * math.pi
        return angle
