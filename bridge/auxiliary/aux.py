"""
Auxiliary math and utility module.
"""

import math
import typing
from typing import Optional, Sequence, TypeVar

from bridge import const


class Graph:
    """
    Class for working with graphs.
    """

    def __init__(self, num_vertices: int) -> None:
        """
        Initializes the graph and allocates memory for it.

        Args:
            num_vertices: Number of vertices in the graph.
        """
        self.num_vertices = num_vertices
        self.graph = [[0] * num_vertices for _ in range(num_vertices)]

    def add_edge(self, from_vertex: int, to_vertex: int, weight: int) -> None:
        """
        Adds an edge to the graph.

        Args:
            from_vertex: Starting vertex index.
            to_vertex: Ending vertex index.
            weight: Edge weight.
        """
        self.graph[from_vertex][to_vertex] = weight
        self.graph[to_vertex][from_vertex] = weight

    def dijkstra(self, start_vertex: int) -> list[float]:
        """
        Finds shortest paths from the start vertex using Dijkstra's algorithm.

        Args:
            start_vertex: Index of the start vertex.

        Returns:
            List of distances from start_vertex to all other vertices.
        """
        distances = [float("inf")] * self.num_vertices
        distances[start_vertex] = 0
        visited = [False] * self.num_vertices

        for _ in range(self.num_vertices):
            min_distance = float("inf")
            min_vertex = -1

            for v in range(self.num_vertices):
                if not visited[v] and distances[v] < min_distance:
                    min_distance = distances[v]
                    min_vertex = v

            visited[min_vertex] = True

            for v in range(self.num_vertices):
                if (
                    not visited[v]
                    and self.graph[min_vertex][v]
                    and distances[min_vertex] != float("inf")
                    and distances[min_vertex] + self.graph[min_vertex][v] < distances[v]
                ):
                    distances[v] = distances[min_vertex] + self.graph[min_vertex][v]

        return distances


class Point:
    """Class representing a point (vector)."""

    def __init__(self, x: float = 0, y: float = 0):
        """
        Initialize point with coordinates x and y.

        Attributes:
            x (float): X coordinate.
            y (float): Y coordinate.
        """
        self.x = x
        self.y = y

    def __add__(self, p: typing.Optional["Point"]) -> "Point":
        """Add two points component-wise."""
        if p is None:
            return self
        return Point(self.x + p.x, self.y + p.y)

    def __neg__(self) -> "Point":
        """Negate both coordinates of the point."""
        return Point(-self.x, -self.y)

    def __sub__(self, p: "Point") -> "Point":
        """Subtract two points component-wise."""
        return self + -p

    def __mul__(self, a: float) -> "Point":
        """Multiply point by scalar."""
        return Point(self.x * a, self.y * a)

    def __truediv__(self, a: float) -> "Point":
        """Divide point by scalar."""
        return self * (1 / a)

    def __pow__(self, a: float) -> "Point":
        """Raise both coordinates to power a."""
        return Point(self.x**a, self.y**a)

    def __eq__(self, p: typing.Any) -> bool:
        """Check if points are approximately equal."""
        try:
            return dist(self, p) < 0.1
        except AttributeError:
            return False

    def __str__(self) -> str:
        """String representation with two decimal places."""
        return f"x = {self.x:.2f}, y = {self.y:.2f}"

    def mag(self) -> float:
        """Return magnitude of vector."""
        return math.hypot(self.x, self.y)

    def arg(self) -> float:
        """Return argument of vector (angle relative to OX axis)."""
        return math.atan2(self.y, self.x)

    def unity(self) -> "Point":
        """Return unit vector in the same direction."""
        if self.mag() == 0:
            return self
        return self / self.mag()

    def debug_str(self) -> str:
        """Return string to recreate this point."""
        return f"aux.Point({self.x:.0f}, {self.y:.0f})"


RIGHT = Point(1, 0)
UP = Point(0, 1)
GRAVEYARD_POS = Point(0, const.GRAVEYARD_POS_X)
FIELD_INF = Point(const.GRAVEYARD_POS_X, 0)


def dist2line(line_start: Point, line_end: Point, point: Point) -> float:
    """
    Calculate the distance from a point to the line formed by two other points.

    Args:
        line_start (Point): The first point defining the line.
        line_end (Point): The second point defining the line.
        point (Point): The point from which the distance to the line is measured.

    Returns:
        float: The perpendicular distance from the point to the line.
    """
    return abs(vec_mult((line_end - line_start).unity(), point - line_start))


def segment_poly_intersect(segment_start: Point, segment_end: Point, polygon: list[Point]) -> typing.Optional[Point]:
    """
    Check if the segment intersects with the polygon.

    Args:
        segment_start (Point): Start point of the segment.
        segment_end (Point): End point of the segment.
        polygon (list[Point]): Vertices of the polygon.

    Returns:
        Optional[Point]: The intersection point if found, otherwise None.
    """
    for i in range(-1, len(polygon) - 1):
        p = get_line_intersection(segment_start, segment_end, polygon[i], polygon[i + 1], "SS")
        if p is not None:
            return p
    return None


def is_point_inside_poly(point: Point, polygon: list[Point]) -> bool:
    """
    Check if a point is inside a convex polygon.

    Args:
        point (Point): The point to check.
        polygon (list[Point]): Vertices of the convex polygon.

    Returns:
        bool: True if the point is inside the polygon, otherwise False.
    """
    old_sign = sign(vec_mult(point - polygon[-1], polygon[0] - polygon[-1]))
    for i in range(len(polygon) - 1):
        if old_sign != sign(vec_mult(point - polygon[i], polygon[i + 1] - polygon[i])):
            return False
    return True


def dist(point1: Point, point2: Point) -> float:
    """
    Compute the distance between two points.

    Args:
        point1 (Point): The first point.
        point2 (Point): The second point.

    Returns:
        float: The Euclidean distance between the two points.
    """
    return math.hypot(point1.x - point2.x, point1.y - point2.y)


def average_point(points: Sequence[Point]) -> Point:
    """
    Calculate the average point from a list of points.

    Args:
        points (Sequence[Point]): A list or sequence of points.

    Returns:
        Point: The point representing the average of the input points.
    """
    point = Point(0, 0)
    for p in points:
        point += p
    return point / len(points)


def average_angle(angles: list[float]) -> float:
    """
    Compute the average of multiple angles, properly handling angle wrapping.

    Args:
        angles (list[float]): A list of angles in radians.

    Returns:
        float: The average angle in radians.
    """
    delta_angle = 0.0
    angle_zero = angles[0]
    for ang in angles:
        delta_angle += wind_down_angle(ang - angle_zero)
    return delta_angle / len(angles) + angle_zero


def get_line_intersection(
    line1_start: Point,
    line1_end: Point,
    line2_start: Point,
    line2_end: Point,
    is_inf: str = "SS",
) -> typing.Optional[Point]:
    """
    Calculate the intersection point of two lines or segments.

    Args:
        line1_start: Start point of the first line.
        line1_end: End point of the first line.
        line2_start: Start point of the second line.
        line2_end: End point of the second line.
        is_inf (str): Defines line type (sequentially for line1 and line2):
            'S' - segment,
            'R' - ray,
            'L' - infinite line.

    Returns:
        Intersection point if valid; otherwise, None.
    """
    delta_x1 = line1_end.x - line1_start.x
    delta_y1 = line1_end.y - line1_start.y
    delta_x2 = line2_end.x - line2_start.x
    delta_y2 = line2_end.y - line2_start.y
    determinant = delta_y1 * delta_x2 - delta_y2 * delta_x1

    if determinant == 0:
        # The lines are parallel or coincident
        return None

    delta_x_start = line1_start.x - line2_start.x
    delta_y_start = line1_start.y - line2_start.y
    t1 = (delta_x_start * delta_y2 - delta_x2 * delta_y_start) / determinant
    t2 = (delta_x_start * delta_y1 - delta_x1 * delta_y_start) / determinant

    intersection_x = line1_start.x + t1 * delta_x1
    intersection_y = line1_start.y + t1 * delta_y1
    p = Point(intersection_x, intersection_y)

    first_valid = False
    second_valid = False
    if is_inf[0] == "S" and 0 <= t1 <= 1 or is_inf[0] == "R" and t1 >= 0 or is_inf[0] == "L":
        first_valid = True
    if is_inf[1] == "S" and 0 <= t2 <= 1 or is_inf[1] == "R" and t2 >= 0 or is_inf[1] == "L":
        second_valid = True

    if first_valid and second_valid:
        return p

    return None


def vec_mult(v: Point, u: Point) -> float:
    """
    Calculate the magnitude of the cross product (2D vector product) of two vectors.

    Args:
        v (Point): The first vector.
        u (Point): The second vector.

    Returns:
        float: The scalar value representing the magnitude of the cross product.
    """
    return v.x * u.y - v.y * u.x


def scal_mult(v: Point, u: Point) -> float:
    """
    Calculate the dot product (scalar product) of two vectors.

    Args:
        v (Point): The first vector.
        u (Point): The second vector.

    Returns:
        float: The scalar dot product of the two vectors.
    """
    return v.x * u.x + v.y * u.y


def rotate(vector: Point, angle: float) -> Point:
    """
    Rotate a vector by a given angle (counterclockwise).

    Args:
        vector (Point): The vector to be rotated.
        angle (float): The angle in radians by which to rotate the vector.

    Returns:
        Point: The rotated vector.
    """
    return Point(
        vector.x * math.cos(angle) - vector.y * math.sin(angle),
        vector.y * math.cos(angle) + vector.x * math.sin(angle),
    )


def find_nearest_point(center: Point, points: list[Point], exclude: Optional[list[Point]] = None) -> Point:
    """f
    Find the nearest point to a given point (center) from a list, optionally excluding some points.

    Args:
        center (Point): The reference point.
        points (list[Point]): The list of candidate points.
        exclude (Optional[list[Point]]): Points to ignore during the search (default is None).

    Returns:
        Point: The closest point to `center` that is not in `exclude`.
    """
    if exclude is None:
        exclude = []
    closest = points[0]
    min_dist = 10e10
    for _, point in enumerate(points):
        if point in exclude:
            continue
        if dist(center, point) < min_dist:
            min_dist = dist(center, point)
            closest = point
    return closest


def wind_down_angle(angle: float) -> float:
    """
    Normalize an angle to be within the range [-π, π].

    Args:
        angle (float): The input angle in radians.

    Returns:
        float: The normalized angle within [-π, π].
    """
    angle = angle % (2 * math.pi)
    if angle > math.pi:
        angle -= 2 * math.pi
    return angle


def closest_point_on_line(line_start: Point, line_end: Point, point: Point, is_inf: str = "S") -> Point:
    """
    Find the closest point on the line to the given point.

    Args:
        line_start (Point): The first point of the line.
        line_end (Point): The second point of the line.
        point (Point): The point to project onto the line.
        is_inf (str): Defines the type of line:
            'S' - segment
            'R' - ray starting at point1 towards point2
            'L' - infinite line

    Returns:
        The closest point on the specified line type.
    """
    line_vector = (line_end.x - line_start.x, line_end.y - line_start.y)
    line_length = dist(line_start, line_end)

    if line_length == 0:
        return line_start

    line_direction = (line_vector[0] / line_length, line_vector[1] / line_length)

    point_vector = (point.x - line_start.x, point.y - line_start.y)
    dot_product = point_vector[0] * line_direction[0] + point_vector[1] * line_direction[1]

    if dot_product <= 0 and is_inf != "L":
        return line_start
    if dot_product >= line_length and is_inf == "S":
        return line_end

    closest_point = Point(
        line_start.x + line_direction[0] * dot_product,
        line_start.y + line_direction[1] * dot_product,
    )

    return closest_point


def point_on_line(start: Point, end: Point, distance: float) -> Point:
    """
    Get a point on the line from 'start' to 'end' at a specified distance from 'start'.

    Args:
        start (Point): The starting point.
        end (Point): The target point defining the line direction.
        distance (float): Distance from 'start' to the desired point on the line.

    Returns:
        Point: The calculated point on the line.
    """
    return start + (end - start).unity() * distance


T = TypeVar("T", float, "Point")


def lerp(start: T, end: T, t: float) -> T:
    """
    Perform linear interpolation between two values or points.

    Args:
        start (float | Point): The start value or point.
        end (float | Point): The end value or point.
        t (float): The interpolation parameter (0 <= t <= 1).

    Returns:
        float | Point: The interpolated value or point.
    """
    return start * (1 - t) + end * t


def minmax(x: float, a: float, b: Optional[float] = None) -> float:
    """
    Clamp x to the nearest value within the range [a, b] or [-a, a] if b is None.

    Args:
        x (float): The value to clamp.
        a (float): One bound of the range.
        b (Optional[float]): The other bound of the range (optional).

    Returns:
        float: The clamped value.
    """
    if b is None:
        b = -a
    a, b = min(a, b), max(a, b)
    return min(max(x, a), b)


def angle_to_point(start: Point, end: Point) -> float:
    """
    Calculate the angle of the vector from 'start' to 'end'.

    Args:
        start (Point): The start point.
        end (Point): The end point.

    Returns:
        float: The angle of the vector in radians.
    """
    return (end - start).arg()


def sign(num: float) -> int:
    """
    Get the sign of a number.

    Args:
        num (float): The input number.

    Returns:
        int: 1 if positive, -1 if negative, 0 if zero.
    """
    if num == 0:
        return 0
    return int(num / abs(num))


def det(a: float, b: float, c: float, d: float) -> float:
    """
    Calculate the determinant of a 2x2 matrix.

    Matrix:
        |a b|
        |c d|

    Args:
        a (float): Top left element.
        b (float): Top right element.
        c (float): Bottom left element.
        d (float): Bottom right element.

    Returns:
        float: The determinant value.
    """
    return a * d - b * c
    

def nearest_point_on_poly(point: Point, polygon: list[Point]) -> Point:
    """
    Find the nearest point on the polygon's edge to a given point.

    Args:
        point (Point): The point to measure from.
        polygon (list[Point]): The polygon defined by a list of points.

    Returns:
        Point: The closest point on the polygon edge.
    """
    min_ = 10e10
    ans = Point(0, 0)
    for i, _ in enumerate(polygon):
        closest_point_on_poly = closest_point_on_line(polygon[i - 1], polygon[i], point)
        d = dist(closest_point_on_poly, point)
        if d < min_:
            min_ = d
            ans = closest_point_on_poly
    return ans


def nearest_point_in_poly(point: Point, polygon: list[Point]) -> Point:
    """
    Find the nearest point inside the polygon to a given point.
    Returns the point itself if it lies inside the polygon.

    Args:
        point (Point): The point to check.
        polygon (list[Point]): The polygon defined by a list of points.

    Returns:
        Point: The nearest point inside the polygon or the point itself if inside.
    """
    if is_point_inside_poly(point, polygon):
        return point

    return nearest_point_on_poly(point, polygon)


def in_place(point: Point, target: Point, epsilon: float) -> bool:
    """
    Check if a point lies within an epsilon radius of another point.

    Args:
        point (Point): The point to check.
        target (Point): The reference point.
        epsilon (float): The allowable radius.

    Returns:
        bool: True if 'point' is within epsilon of 'target', False otherwise.
    """
    return (point - target).mag() < epsilon


def circles_inter(center1: Point, center2: Point, radius1: float, radius2: float) -> tuple[Point, Point]:
    """
    Find the intersection points of two circles.

    Args:
        center1 (Point): Center of the first circle.
        center2 (Point): Center of the second circle.
        radius1 (float): Radius of the first circle.
        radius2 (float): Radius of the second circle.

    Returns:
        tuple[Point, Point]: The two intersection points.
    """
    d = dist(center1, center2)
    a = (radius1**2 - radius2**2 + d**2) / (2 * d)
    h = math.sqrt(radius1**2 - a**2)
    x2 = center1.x + a * (center2.x - center1.x) / d
    y2 = center1.y + a * (center2.y - center1.y) / d
    x3 = x2 + h * (center2.y - center1.y) / d
    y3 = y2 - h * (center2.x - center1.x) / d
    x4 = x2 - h * (center2.y - center1.y) / d
    y4 = y2 + h * (center2.x - center1.x) / d
    return Point(x3, y3), Point(x4, y4)


def get_tangent_points(center: Point, point: Point, r: float) -> list[Point]:
    """
    Get tangent points from a point outside a circle to the circle.

    Args:
        center (Point): Center of the circle.
        point (Point): External point from which tangents are drawn.
        r (float): Radius of the circle.

    Returns:
        list[Point]: List of tangent points on the circle.
    """
    d = dist(center, point)
    if d < r:
        return []

    if d == r:
        return [point]

    mid = (center + point) / 2
    p2, p3 = circles_inter(center, mid, r, d / 2)
    return [p2, p3]


def get_angle_between_points(end1: Point, start: Point, end2: Point) -> float:
    """
    Calculate the signed angle between vectors start->end1 and start->end2.

    Positive angle means end2 is to the left of end1 relative to start.

    Args:
        end1 (Point): Endpoint of first vector.
        start (Point): Common vertex point.
        end2 (Point): Endpoint of second vector.

    Returns:
        float: The signed angle in radians.
    """
    ang = angle_to_point(start, end2) - angle_to_point(start, end1)
    return wind_down_angle(ang)


def cosine_theorem(a: float, b: float, angle: float) -> float:
    """
    Calculate the length of the third side of a triangle using the law of cosines.

    Args:
        a (float): Length of side a.
        b (float): Length of side b.
        angle (float): Angle between sides a and b in radians.

    Returns:
        float: Length of the third side.
    """
    return math.sqrt(a * a + b * b - 2 * a * b * math.cos(angle))


def line_circle_intersect(
    line_start: Point, line_end: Point, center: Point, radius: float, is_inf: str = "L"
) -> list[Point]:
    """
    Find intersection points between a line (or segment or ray) and a circle.

    Args:
        line_start (Point): Start point of line/segment/ray.
        line_end (Point): End point of line/segment/ray.
        center (Point): Center of the circle.
        radius (float): Radius of the circle.
        is_inf (str): Defines line type:
            'S' - segment,
            'R' - ray,
            'L' - infinite line.

    Returns:
        list[Point]: List of intersection points (empty if none).
    """
    h = closest_point_on_line(line_start, line_end, center, is_inf)
    if radius < dist(center, h):
        return []
    if radius == dist(center, h):
        return [h]

    d = math.sqrt(radius**2 - dist(center, h) ** 2)
    vec = (line_end - line_start).unity() * d
    p1 = h + vec
    p2 = h - vec

    c1 = closest_point_on_line(line_start, line_end, p1, is_inf)
    c2 = closest_point_on_line(line_start, line_end, p2, is_inf)

    if p1 != c1 and p2 != c2:
        return []
    if p1 != c1:
        return [p2]
    if p2 != c2:
        return [p1]
    return [p1, p2]


def is_point_inside_circle(point: Point, center: Point, radius: float) -> bool:
    """
    Check if a point lies inside a circle.

    Args:
        point (Point): The point to check.
        center (Point): Center of the circle.
        radius (float): Radius of the circle.

    Returns:
        bool: True if point is inside the circle, False otherwise.
    """
    return dist(point, center) < radius


def nearest_point_on_circle(point: Point, center: Point, radius: float) -> Point:
    """
    Find the nearest point on the circumference to a given point.

    Args:
        point (Point): The external point.
        center (Point): Center of the circle.
        radius (float): Radius of the circle.

    Returns:
        Point: The closest point on the circle's edge.
    """
    return center + (point - center).unity() * radius


def is_point_on_line(point: Point, line_start: Point, line_end: Point, is_inf: str = "L") -> bool:
    """
    Check if a point lies exactly on a line, segment, or ray.

    Args:
        point (Point): The point to check.
        line_start (Point): Start point of the line.
        line_end (Point): End point of the line.
        is_inf (str): Defines line type:
            'S' - segment,
            'R' - ray,
            'L' - infinite line.

    Returns:
        bool: True if point lies on the defined line, False otherwise.
    """
    return point == closest_point_on_line(line_start, line_end, point, is_inf)


def offset_polygon(peaks: list[Point], distance: float) -> list[Point]:
    """
    Offset the edges of a convex polygon without straight angles by a specified distance.

    Args:
        peaks (list[Point]): Vertices of the polygon.
        distance (float): Offset distance (positive or negative).

    Returns:
        list[Point]: New list of offset vertices.
    """
    if len(peaks) < 3:
        return peaks

    direction_sing = sign(wind_down_angle(angle_to_point(peaks[0], peaks[1]) - angle_to_point(peaks[1], peaks[2])))
    if direction_sing < 0:
        distance *= -1

    new_peaks = peaks.copy()
    for idx, _ in enumerate(peaks):
        left_edge = peaks[idx - 1] - peaks[idx]
        perp_left = rotate(left_edge, -math.pi / 2).unity()
        right_edge = peaks[idx + 1 - len(peaks)] - peaks[idx]
        perp_right = rotate(right_edge, math.pi / 2).unity()

        delta_vec_angle = wind_down_angle(perp_left.arg() - perp_right.arg()) / 2
        delta_vec = (perp_left + perp_right).unity() * distance / math.cos(delta_vec_angle)
        new_peaks[idx] = peaks[idx] + delta_vec

    return new_peaks
