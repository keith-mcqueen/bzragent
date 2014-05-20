import math

from vec2d import Vec2d


class Tangential(object):
    """Contains logic for creating and using tangential fields"""

    def __init__(self, obstacle):
        self.obstacle = obstacle

    def get_nearest_point(self, tank):
        rightX = self.obstacle[0][0]
        topY = self.obstacle[0][1]
        leftX = self.obstacle[2][0]
        bottomY = self.obstacle[2][1]
        nearestX = rightX
        nearestY = topY
        if tank.x < leftX:
            nearestX = leftX
        elif tank.x < rightX:
            #nearestX = self.nearest_point(leftX, bottomY, rightX, bottomY, tank.x, tank.y)[0]
            nearestX = tank.x

        if tank.y < bottomY:
            nearestY = bottomY
        elif tank.y < topY:
            #nearestY = self.nearest_point(leftX, bottomY, leftX, topY, tank.x, tank.y)[1]
            nearestY = tank.y

        return Vec2d(nearestX, nearestY)

    #(x1,y1), (x2,y2) define the line while (x3,y3) is the point
    #Code copied from internet for finding the nearest point from
    #the tank to the obstacle
    def nearest_point(self, x1, y1, x2, y2, x3, y3):
        px = x2 - x1
        py = y2 - y1

        something = px * px + py * py

        u = ((x3 - x1) * px + (y3 - y1) * py) / float(something)

        if u > 1:
            u = 1
        elif u < 0:
            u = 0

        x = x1 + u * px
        y = y1 + u * py
        return Vec2d(x, y)

    def get_push(self, tank, obstacle):
        dist = math.sqrt((obstacle[0] - tank.x) ** 2 + (obstacle[1] - tank.y) ** 2)
        if dist > 40:
            return 0
        return 30 / dist

    def get_vector(self, tank):
        obstacle = self.get_nearest_point(tank)
        push = self.get_push(tank, obstacle)
        vector = Vec2d(obstacle.x - tank.x, obstacle.y - tank.y)
        vector.length = push
        #rotate a little more than 90 degrees so it pushes tanks away
        #slightly instead of being perfectly perpendicular
        vector.rotate(91)
        return vector

    def normalize_angle(self, angle):
        """Make any angle be between +/- pi."""
        angle -= 2 * math.pi * int(angle / (2 * math.pi))
        if angle <= -math.pi:
            angle += 2 * math.pi
        elif angle > math.pi:
            angle -= 2 * math.pi
        return angle
