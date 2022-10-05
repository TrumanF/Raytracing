import pygame
import math
import numpy as np
import random

# TODO: Rewrite that fucking circle_line_intersection bullshit whatever function and understand what the fuck the
#  math is behind it

pygame.init()
WIDTH, HEIGHT = 1200, 1200
MAX_RAY_LENGTH = math.sqrt(WIDTH ** 2 + HEIGHT ** 2)
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Raytracing engine")
FPS = 60

WHITE = (255, 255, 255)
obstacles = []


class Source:
    def __init__(self, x, y, bar=False):
        self.bar = bar
        self.x = x
        self.y = y
        self.ray_count = 250
        self.angle = 2 * math.pi / self.ray_count
        self.rays = []
        self.source_state = True
        for ray in range(1, self.ray_count+1):
            self.rays.append(self.Ray(self.x, self.y, self.angle * ray))

    def draw(self):
        if self.bar:
            pass
        else:
            pygame.draw.circle(WIN, WHITE, to_cartesian((self.x, self.y)), 4)
            if self.source_state:
                for ray in self.rays:
                    ray.draw()

    def update(self, mx, my):
        self.x = mx
        self.y = my
        for ray in self.rays:
            ray.update(mx, my)

    def toggle_state(self):
        self.source_state = not self.source_state

    def change_density(self, amount):
        if not self.ray_count + amount == 0:
            self.ray_count += amount
            self.angle = 2 * math.pi / self.ray_count
            self.rays = []
            for ray in range(1, self.ray_count+1):
                self.rays.append(self.Ray(self.x, self.y, self.angle * ray))

    class Ray:
        def __init__(self, x, y, angle):
            self.x = x
            self.y = y
            self.dir = (math.cos(angle), math.sin(angle))
            # self.equation = equationOfLine((x, y), (x + self.dir[0], y + self.dir[1]))
            self.start = (x, y)
            self.end = (x + self.dir[0] * MAX_RAY_LENGTH, y + self.dir[1] * MAX_RAY_LENGTH)

        def check_collision(self, obstacle):
            if type(obstacle) == Circle:
                coord = circle_line_segment_intersection((obstacle.x, obstacle.y), obstacle.radius, self.start, self.end,
                                                         False)
                if len(coord) > 0:
                    coord = coord[0]
                else:
                    coord = None
            else:
                coord = lineSegmentIntersection((self.start, self.end), (obstacle.start, obstacle.end))  # return either (x, y) or None
            return coord

        def draw(self):
            temp_d = None
            closest_obstacle = None
            for obstacle in obstacles:
                coord = self.check_collision(obstacle)  # return either (x, y) or None
                # coord = self.checkCollision(obstacle)  # return either (x, y) or None
                if coord is None:
                    continue
                distance_to_coord = distance((self.x, self.y), coord)
                if temp_d is None or distance_to_coord < temp_d:
                    temp_d = distance_to_coord  # save the new closest wall distance
                    closest_obstacle = obstacle

            if closest_obstacle is not None:  # If there is a closest_wall, then draw to this wall
                coord = self.check_collision(closest_obstacle)  # return either (x, y) or None
                # coord = self.checkCollision(closest_obstacle)  # return either (x, y) or None
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
        # self.equation = equationOfLine(start, end)

    def draw(self):
        pygame.draw.line(WIN, WHITE, to_cartesian(self.start), to_cartesian(self.end))

    def update(self):
        # for updates
        pass


class Circle:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        # self.equation = equationOfCircle((x, y), radius)

    def draw(self):
        pygame.draw.circle(WIN, WHITE, to_cartesian((self.x, self.y)), self.radius, 1)

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
        return point


# Not in use
def solveSystem(equations):
    lhs = []
    rhs = []
    max_args = 0
    for equation in equations:
        if len(equation[0]) > max_args:
            max_args = len(equation[0])

    for equation in equations:
        if len(equation[0]) < max_args:
            equation[0].extend([0] * (max_args - len(equation[0])))
        lhs.append(equation[0])
        rhs.append(equation[1])
    A = np.array(lhs)
    B = np.array(rhs)
    # print(A, B)
    try:
        solution = np.linalg.solve(A, B)
    except:
        return None
    return solution


def circle_line_segment_intersection(circle_center, circle_radius, pt1, pt2, full_line=True, tangent_tol=1e-9):
    """ Find the points at which a circle intersects a line-segment.  This can happen at 0, 1, or 2 points.

    :param circle_center: The (x, y) location of the circle center
    :param circle_radius: The radius of the circle
    :param pt1: The (x, y) location of the first point of the segment
    :param pt2: The (x, y) location of the second point of the segment
    :param full_line: True to find intersections along full line - not just in the segment.  False will just return intersections within the segment.
    :param tangent_tol: Numerical tolerance at which we decide the intersections are close enough to consider it a tangent
    :return Sequence[Tuple[float, float]]: A list of length 0, 1, or 2, where each element is a point at which the circle intercepts a line segment.

    Note: We follow: http://mathworld.wolfram.com/Circle-LineIntersection.html
    """

    (p1x, p1y), (p2x, p2y), (cx, cy) = pt1, pt2, circle_center
    (x1, y1), (x2, y2) = (p1x - cx, p1y - cy), (p2x - cx, p2y - cy)
    dx, dy = (x2 - x1), (y2 - y1)
    dr = (dx ** 2 + dy ** 2)**.5
    big_d = x1 * y2 - x2 * y1
    discriminant = circle_radius ** 2 * dr ** 2 - big_d ** 2

    if discriminant < 0:  # No intersection between circle and line
        return []
    else:  # There may be 0, 1, or 2 intersections with the segment
        intersections = [
            (cx + (big_d * dy + sign * (-1 if dy < 0 else 1) * dx * discriminant**.5) / dr ** 2, cy + (-big_d * dx + sign * abs(dy) * discriminant**.5) / dr ** 2) for sign in ((1, -1) if dy < 0 else (-1, 1))]  # This makes sure the order along the segment is correct
        if not full_line:  # If only considering the segment, filter out intersections that do not fall within the segment
            fraction_along_segment = [(xi - p1x) / dx if abs(dx) > abs(dy) else (yi - p1y) / dy for xi, yi in intersections]
            intersections = [pt for pt, frac in zip(intersections, fraction_along_segment) if 0 <= frac <= 1]
        if len(intersections) == 2 and abs(discriminant) <= tangent_tol:  # If line is tangent to circle, return just one point (as both intersections have same location)
            return [intersections[0]]
        else:
            return intersections


def distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def main():

    run = True
    clock = pygame.time.Clock()
    light = Source(600, 600)
    lights = [light]
    global obstacles
    for i in range(5):
        obstacles.append(Wall((random.randint(200, 1000), random.randint(200, 1000)),
                          (random.randint(200, 1000), (random.randint(200, 1000)))))
        if i < 3:
            obstacles.append(Circle(random.randint(200, 1000), random.randint(200, 1000), random.randint(25, 100)))

    while run:
        # game speed changes based on FPS at the moment
        clock.tick(FPS)
        WIN.fill((0, 0, 0))
        mx, my = to_cartesian(pygame.mouse.get_pos())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    for light in lights:
                        light.toggle_state()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    for light in lights:
                        light.change_density(5)
                elif event.button == 5:
                    for light in lights:
                        light.change_density(-5)
        for light in lights:
            light.update(mx, my)
            light.draw()
        for obstacle in obstacles:
            obstacle.draw()
        pygame.display.update()

    pygame.quit()


main()
