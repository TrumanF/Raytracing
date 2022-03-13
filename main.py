import pygame
import math
import numpy as np
import random

pygame.init()
WIDTH, HEIGHT = 1200, 1200
MAX_RAY_LENGTH = math.sqrt(WIDTH ** 2 + HEIGHT ** 2)
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Raytracing engine")
FPS = 60

WHITE = (255, 255, 255)
walls = []


class Source:
    def __init__(self, x, y, ray_count):
        self.x = x
        self.y = y
        self.ray_count = ray_count
        self.ray_displacement_list = []
        angle = 2 * math.pi / self.ray_count
        self.rays = []
        for ray in range(1, ray_count+1):
            self.rays.append(Ray(self.x, self.y, angle * ray))

    def draw(self):
        pygame.draw.circle(WIN, WHITE, to_cartesian((self.x, self.y)), 4)
        for ray in self.rays:
            ray.draw()

    def update(self, mx, my):
        self.x = mx
        self.y = my
        for ray in self.rays:
            ray.update(mx, my)


class Ray:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.dir = (math.cos(angle), math.sin(angle))
        # self.equation = equationOfLine((self.x, self.y), (self.x + self.dir[0], self.y + self.dir[1]))
        # self.length = math.sqrt(WIDTH ** 2 + HEIGHT ** 2)
        self.start = (x, y)
        self.end = (self.x + self.dir[0] * MAX_RAY_LENGTH, self.y + self.dir[1] * MAX_RAY_LENGTH)

    def checkCollision(self, obstacle):
        return lineSegmentIntersection((self.start, self.end), (obstacle.start, obstacle.end))

    def draw(self):
        temp_d = None
        closest_wall = None
        for wall in walls:
            coord = self.checkCollision(wall)  # return either (x, y) or None
            if coord is None:
                continue
            distance_to_coord = distance((self.x, self.y), coord)
            if temp_d is None or distance_to_coord < temp_d:
                temp_d = distance_to_coord  # save the new closest wall distance
                closest_wall = wall

        if closest_wall is not None:  # If there is a closest_wall, then draw to this wall
            coord = self.checkCollision(closest_wall)
            pygame.draw.line(WIN, WHITE, to_cartesian((self.x, self.y)),
                             to_cartesian((float(coord[0]), float(coord[1]))))

        else:  # Otherwise, there isn't a closest_wall, so there is no wall, draw to edge of screen
            pygame.draw.line(WIN, WHITE, to_cartesian((self.x, self.y)),
                             to_cartesian((self.x + self.dir[0] * MAX_RAY_LENGTH, self.y + self.dir[1] * MAX_RAY_LENGTH)))

    def update(self, mx, my):
        self.x = mx
        self.y = my
        self.start = (mx, my)
        self.end = (self.x + self.dir[0] * MAX_RAY_LENGTH, self.y + self.dir[1] * MAX_RAY_LENGTH)


class Wall:
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.equation = equationOfLine(self.start, self.end)

    def draw(self):
        pygame.draw.line(WIN, WHITE, to_cartesian(self.start), to_cartesian(self.end))

    def update(self):
        # for updates
        pass


def to_cartesian(coord):
    x, y = coord
    return x, HEIGHT - y


# Not in use
def equationOfLine(start, end):
    # return tuple, second item 0:y and 1:x
    start_x, start_y = start
    end_x, end_y = end
    slope_num = (end_y - start_y)
    slope_denom = (end_x - start_x)
    if slope_denom == 0:
        return [1, 0], [end_x]
    if slope_num == 0:
        return [0, 1], [end_y]
    slope = slope_num/slope_denom
    b = end_y - slope*end_x
    return [slope, -1], [-b]


# Not in use
def equationOfCircle(center, radius):
    center_x, center_y = center
    return [-2*center_x, -2*center_y, 1, 1], [radius ** 2 - center_x ** 2 - center_y ** 2]


def lineSegmentIntersection(line1, line2):
    x1, y1 = line1[0]
    x2, y2 = line1[1]
    x3, y3 = line2[0]
    x4, y4 = line2[1]

    t_num = (x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

    if denom == 0:
        return None
    t = t_num/denom
    u_num = (x1 - x3) * (y1 - y2) - (y1 - y3) * (x1 - x2)
    u = u_num/denom

    if 0 <= t <= 1 and 0 <= u <= 1:
        point = (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
        # point = (x3 + u * (x4 - x3)), (y3 + u * (y4 - y3))
        return point


# Not in use
def solveSystem(equations):
    lhs = []
    rhs = []
    for equation in equations:
        lhs.append(equation[0])
        rhs.append(equation[1])
    A = np.array(lhs)
    b = np.array(rhs)
    try:
        solution = np.linalg.solve(A, b)
    except:
        return None
    return solution


def distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def main():

    run = True
    clock = pygame.time.Clock()
    light = Source(600, 600, 300)
    lights = [light]
    global walls
    for i in range(5):
        walls.append(Wall((random.randint(200, 1000), random.randint(200, 1000)),
                          (random.randint(200, 1000), (random.randint(200, 1000)))))

    while run:
        # game speed changes based on FPS at the moment
        clock.tick(FPS)
        WIN.fill((0, 0, 0))
        mx, my = to_cartesian(pygame.mouse.get_pos())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        for light in lights:
            light.update(mx, my)
            light.draw()
        for wall in walls:
            wall.draw()
        pygame.display.update()

    pygame.quit()


main()
