"""
Class with robot actions
"""

import math
from time import time
from typing import Optional

import bridge.auxiliary.quickhull as qh
from bridge import const
from bridge.auxiliary import aux, fld, rbt, tau
from bridge.auxiliary.entity import Entity
from bridge.router.action import Action, ActionDomain, ActionValues, limit_action
from bridge.strategy.strategy import GameStates

# Actions: ActionDomain -> ActionValues


class Actions:
    """Class with all user-available actions (except kicks)"""

    class Stop(Action):
        """Stop the robot"""

        def behavior(self, domain: ActionDomain, current_action: ActionValues) -> None:
            """Behavior"""
            current_action.vel = aux.Point(0, 0)
            current_action.angle = domain.robot.get_angle()
            current_action.beep = 0

    class GoToPointIgnore(Action):
        """Go to point ignore obstacles"""

        def __init__(
            self,
            target_pos: aux.Point,
            target_angle: float,
            ball_interact: bool = False,
            target_vel: aux.Point = aux.Point(0, 0),
        ) -> None:
            self.target_pos = target_pos
            self.target_angle = target_angle
            self.ball_interact = ball_interact
            self.target_vel = target_vel

        def behavior(self, domain: ActionDomain, current_action: ActionValues) -> None:
            cur_robot = domain.robot
            vec_err = self.target_pos - cur_robot.get_pos()
            cur_vel = cur_robot.get_vel()

            ball_escorting = self.ball_interact and aux.dist(cur_robot.get_pos(), domain.field.ball.get_pos()) < 700
            if ball_escorting:
                cur_robot.pos_reg_x.select_mode(tau.Mode.SOFT)
                cur_robot.pos_reg_y.select_mode(tau.Mode.SOFT)
            else:
                cur_robot.pos_reg_x.select_mode(tau.Mode.NORMAL)
                cur_robot.pos_reg_y.select_mode(tau.Mode.NORMAL)

            u_x = cur_robot.pos_reg_x.process_(vec_err.x, -cur_vel.x, time() - cur_robot.prev_sended_time)
            u_y = cur_robot.pos_reg_y.process_(vec_err.y, -cur_vel.y, time() - cur_robot.prev_sended_time)
            current_action.vel = aux.Point(u_x, u_y)
            # return
            cur_vel_abs = aux.rotate(current_action.vel, cur_robot.get_angle())
            prev_vel_abs = aux.rotate(cur_robot.prev_sended_vel, cur_robot.prev_sended_angle)
            if (cur_vel_abs - prev_vel_abs).mag() / (time() - cur_robot.prev_sended_time) > const.MAX_ACCELERATION:
                # domain.field.router_image.draw_circle(aux.Point(0, 1000), size_in_mms=200)
                current_action.vel = aux.rotate(
                    prev_vel_abs
                    + (cur_vel_abs - prev_vel_abs).unity() * const.MAX_ACCELERATION * (time() - cur_robot.prev_sended_time),
                    -cur_robot.get_angle(),
                )

            # current_action.vel = aux.Point(0,500)
            cur_robot.prev_sended_vel = current_action.vel
            cur_robot.prev_sended_angle = cur_robot.get_angle()
            cur_robot.prev_sended_time = time()
            current_action.angle = self.target_angle

            DumbActions.AddFinalVelocityAction(self.target_pos, self.target_vel).process(domain, current_action)

    class GoToPoint(Action):
        """Go to point and avoid obstacles"""

        def __init__(
            self, target_pos: aux.Point, target_angle: float, ball_interact: bool = False, ignore_ball: bool = False
        ) -> None:
            self.target_pos = target_pos
            self.target_angle = target_angle
            self.ball_interact = ball_interact
            self.ignore_ball = ignore_ball

        def use_behavior_of(self, domain: ActionDomain, current_action: ActionValues) -> list["Action"]:
            angle0 = self.target_angle
            next_point = self.target_pos
            if not aux.is_point_inside_poly(next_point, domain.field.hull):
                next_point = aux.nearest_point_on_poly(next_point, domain.field.hull)

            if domain.robot.r_id != domain.field.gk_id:
                if aux.is_point_inside_poly(next_point, domain.field.ally_goal.hull):
                    next_point = aux.nearest_point_on_poly(next_point, domain.field.ally_goal.big_hull)
                elif aux.is_point_inside_poly(next_point, domain.field.enemy_goal.hull):
                    next_point = aux.nearest_point_on_poly(next_point, domain.field.enemy_goal.big_hull)

                if aux.is_point_inside_poly(domain.robot.get_pos(), domain.field.ally_goal.hull):
                    next_point = aux.nearest_point_on_poly(domain.robot.get_pos(), domain.field.ally_goal.big_hull)
                    return [Actions.GoToPointIgnore(next_point, angle0)]
                elif aux.is_point_inside_poly(domain.robot.get_pos(), domain.field.enemy_goal.hull):
                    next_point = aux.nearest_point_on_poly(domain.robot.get_pos(), domain.field.enemy_goal.big_hull)
                    return [Actions.GoToPointIgnore(next_point, angle0)]

            pint = aux.segment_poly_intersect(domain.robot.get_pos(), next_point, domain.field.ally_goal.hull)
            if pint is not None:
                convex_hull = qh.shortesthull(domain.robot.get_pos(), next_point, domain.field.ally_goal.big_hull)
                for j in range(len(convex_hull) - 2, 0, -1):
                    next_point = convex_hull[j]

            pint = aux.segment_poly_intersect(domain.robot.get_pos(), next_point, domain.field.enemy_goal.hull)
            if pint is not None:
                convex_hull = qh.shortesthull(domain.robot.get_pos(), next_point, domain.field.enemy_goal.big_hull)
                for j in range(len(convex_hull) - 2, 0, -1):
                    domain.field.path_image.draw_circle(convex_hull[j], (150, 0, 150), 100)
                    next_point = convex_hull[j]

            avoid_ball = domain.game_state in [GameStates.STOP, GameStates.PREPARE_KICKOFF] or not domain.we_active
            pth_wp = calc_passthrough_wp(domain, next_point, avoid_ball=avoid_ball, ignore_ball=self.ignore_ball)
            if pth_wp is not None:
                return [Actions.GoToPointIgnore(pth_wp, angle0)]
            if next_point != self.target_pos:
                return [Actions.GoToPointIgnore(next_point, angle0)]
            return [Actions.GoToPointIgnore(self.target_pos, angle0, self.ball_interact)]

    class BallPlacement(Action):
        """Move ball to target_point"""

        def __init__(self, target_point: aux.Point) -> None:
            self.target_point = target_point

        def behavior(self, domain: ActionDomain, current_action: ActionValues) -> None:
            current_action.dribbler_speed = 0

        def use_behavior_of(self, domain: ActionDomain, current_action: ActionValues) -> list["Action"]:
            # current_action.dribbler_speed = 15
            target_angle = (-domain.field.ball.get_pos() + self.target_point).arg()
            if aux.dist(domain.field.ball.get_pos(), self.target_point) < 10:
                current_action.dribbler_speed = 0
                current_action.angle = (self.target_point - domain.robot.get_pos()).arg()
                return []
            if domain.field.is_ball_in(domain.robot):
                return [Actions.GoToPointIgnore(self.target_point, target_angle), DumbActions.LimitSpeed(500)]
            return [Actions.BallGrab(target_angle), DumbActions.LimitSpeed(700)]

    class BallGrab(Action):
        """Grab ball in a given direction"""

        def __init__(self, target_angle: float) -> None:
            self.target_angle = target_angle

        def is_defined(self, domain: ActionDomain) -> bool:
            return aux.dist(domain.robot.get_pos(), domain.field.ball.get_pos()) < 3000 and (
                domain.robot.r_id == const.GK
                or (
                    not aux.is_point_inside_poly(domain.field.ball.get_pos(), domain.field.enemy_goal.hull)
                    and not aux.is_point_inside_poly(domain.field.ball.get_pos(), domain.field.ally_goal.hull)
                )
            )

        def behavior(self, domain: ActionDomain, current_action: ActionValues) -> None:
            ball_pos = domain.field.ball.get_pos()
            align_pos = ball_pos - aux.rotate(aux.RIGHT, self.target_angle) * const.GRAB_ALIGN_DIST
            transl_vel = get_grab_speed(
                domain.robot.get_pos(),
                current_action.vel,
                domain.field,
                align_pos,
                self.target_angle,
            )
            transl_vel += domain.field.ball.get_vel() / 1.2

            current_action.vel = transl_vel
            current_action.angle = self.target_angle

            current_action.dribbler_speed = 15

        def use_behavior_of(self, domain: ActionDomain, current_action: ActionValues) -> list["Action"]:
            ball_pos = domain.field.ball.get_pos()
            align_pos = ball_pos - aux.rotate(aux.RIGHT, self.target_angle) * const.GRAB_ALIGN_DIST
            return [Actions.GoToPoint(align_pos, self.target_angle, True)]

    class Velocity(Action):
        """Move robot with velocity and angle_speed"""

        def __init__(self, velocity: aux.Point, angle: float, control_angle_by_speed: bool = False) -> None:
            self.velocity = velocity
            self.angle = angle  # angle to turn / angle speed

            self.control_angle_by_speed = control_angle_by_speed

        def behavior(self, domain: ActionDomain, current_action: ActionValues) -> None:

            current_action.vel = self.velocity
            current_action.angle = self.angle

            if self.control_angle_by_speed:
                current_action.beep = 1

    twisted_flag = False
    fast_twist_timer = None

    class Kick(Action):
        """Choose type of kick (from KickActions)"""

        def __init__(
            self,
            target_pos: aux.Point,
            voltage: int = const.VOLTAGE_SHOOT,
            is_pass: bool = False,
            is_upper: bool = False,
        ) -> None:
            self.kick_args = (target_pos, voltage, is_pass, is_upper)

        def use_behavior_of(self, domain: ActionDomain, current_action: ActionValues) -> list["Action"]:
            return [KickActions.Straight(*self.kick_args)]


class KickActions:
    """Class with available types of ball kicks"""

    class Kick(Action):
        """Base class"""

        def __init__(
            self,
            target_pos: aux.Point,
            voltage: float = const.VOLTAGE_SHOOT,
            is_pass: bool = False,
            is_upper: bool = False,
        ) -> None:
            self.target_pos = target_pos
            self.voltage = voltage  # ignore if is_pass
            self.is_upper = is_upper

            self.pass_pos: Optional[aux.Point] = None
            if is_pass:
                self.pass_pos = self.target_pos

    class Straight(Kick):
        """Grab the ball and kick it straight"""

        def use_behavior_of(self, domain: ActionDomain, current_action: ActionValues) -> list["Action"]:
            kick_angle = aux.angle_to_point(domain.field.ball.get_pos(), self.target_pos)

            actions = [
                Actions.BallGrab(kick_angle),
                DumbActions.ShootAction(kick_angle, self.is_upper),
                DumbActions.ControlVoltageAction(domain.field.ball.get_pos(), self.voltage, self.pass_pos),
            ]

            return actions


class DumbActions:
    """User-unavailable actions, are used in Actions"""

    class ShootAction(Action):
        """Shoot the target when kick is aligned"""

        def __init__(self, target_angle: float, is_upper: bool = False, angle_bounds: Optional[float] = None) -> None:
            self.target_angle = target_angle
            self.autokick = 2 if is_upper else 1
            self.angle_bounds = angle_bounds

        def is_defined(self, domain: ActionDomain) -> bool:
            is_aligned = (
                domain.robot.is_kick_aligned_by_angle(self.target_angle, angle_bounds=self.angle_bounds)
                if self.angle_bounds is not None
                else domain.robot.is_kick_aligned_by_angle(self.target_angle)
            )
            return domain.field.is_ball_in(domain.robot) and is_aligned

        def behavior(self, domain: ActionDomain, current_action: ActionValues) -> None:
            current_action.auto_kick = self.autokick

    class ControlVoltageAction(Action):
        """Control voltage before shooting"""

        def __init__(
            self, ball_pos: aux.Point, voltage: float = const.VOLTAGE_SHOOT, pass_pos: Optional[aux.Point] = None
        ) -> None:
            self.voltage = voltage
            self.ball_pos = ball_pos
            self.pass_pos = pass_pos

        def is_defined(self, domain: ActionDomain) -> bool:
            return aux.dist(domain.robot.get_pos(), self.ball_pos) < 1000

        def behavior(self, domain: ActionDomain, current_action: ActionValues) -> None:
            if self.pass_pos is not None:
                self.voltage = get_pass_voltage(aux.dist(domain.robot.get_pos(), self.pass_pos))

            current_action.kicker_voltage = int(self.voltage)

    class AddFinalVelocityAction(Action):
        """Add velocity in final target"""

        def __init__(
            self, target: aux.Point, final_velocity: aux.Point, max_dist: float = 1000, min_dist: float = 200
        ) -> None:
            self.target = target
            self.final_velocity = final_velocity
            self.min_dist = min_dist
            self.max_dist = max_dist

        def is_defined(self, domain: ActionDomain) -> bool:
            return aux.dist(self.target, domain.robot.get_pos()) < self.max_dist

        def behavior(self, domain: ActionDomain, current_action: ActionValues) -> None:
            cur_speed = self.final_velocity
            vec_to_target = self.target - domain.robot.get_pos()
            if vec_to_target.mag() > self.min_dist:
                cur_speed = self.final_velocity * ((self.max_dist - vec_to_target.mag()) / (self.max_dist - self.min_dist))

            current_action.vel += cur_speed

    class LimitSpeed(Action):
        """Limit robot speed"""

        def __init__(self, limit: float = const.MAX_SPEED) -> None:
            self.limit = limit

        def behavior(self, domain: ActionDomain, current_action: ActionValues) -> None:
            limit_action(domain, current_action, self.limit)


def get_pass_voltage(length: float) -> int:
    """Calc voltage for pass by length"""
    return int(aux.minmax(0.0016 * length + 2.4, 6, const.VOLTAGE_SHOOT))


def get_grab_speed(
    robot_pos: aux.Point,
    transl_vel: aux.Point,
    field: fld.Field,
    grab_point: aux.Point,
    grab_angle: float,
    target_speed: float = 0,
) -> aux.Point:
    """Calculate speed for carefully grabbing a ball"""
    ball = field.ball.get_pos()

    point_on_center_line = aux.closest_point_on_line(ball, grab_point, robot_pos, "S")
    dist_to_center_line = aux.dist(robot_pos, point_on_center_line)
    ball_dist_center_line = aux.dist(point_on_center_line, ball)

    if ball_dist_center_line == 0:
        offset_angle = const.GRAB_OFFSET_ANGLE
    else:
        offset_angle = math.atan(dist_to_center_line / ball_dist_center_line)

    dist_to_catch = (ball - aux.rotate(aux.RIGHT, grab_angle) * const.GRAB_DIST) - robot_pos

    vel_to_catch = dist_to_catch * const.GRAB_MULT

    vel_to_catch_r = (
        aux.scal_mult(
            vel_to_catch,
            aux.rotate(aux.RIGHT, grab_angle),
        )
        + target_speed
    )

    vel_to_align_r = aux.scal_mult(
        transl_vel,
        aux.rotate(aux.RIGHT, grab_angle),
    )

    vel_to_align = transl_vel - aux.rotate(aux.RIGHT, grab_angle) * vel_to_align_r

    board = min(offset_angle / const.GRAB_OFFSET_ANGLE, 1)  # 0 - go to ball; 1 - go to grab_point

    vel_r = vel_to_catch_r * (1 - board) + vel_to_align_r * board
    vel = vel_to_align + aux.rotate(aux.RIGHT, grab_angle) * vel_r

    # if aux.dist(robot_pos, grab_point) < 500:
    #     draw_grabbing_image(
    #         field,
    #         grab_point,
    #         grab_angle,
    #         robot_pos,
    #         transl_vel,
    #         vel_to_catch,
    #         vel,
    #     )

    return vel


# def draw_grabbing_image(
#     field: fld.Field,
#     grab_point: aux.Point,
#     grab_angle: float,
#     robot_pos: aux.Point,
#     vel_to_align: aux.Point,
#     vel_to_catch: aux.Point,
#     vel: aux.Point,
# ) -> None:
#     """Draw a screen easily debug grabbing a ball"""
#     ball = field.ball.get_pos()

#     cord_scale = 0.8
#     vel_scale = 0.4
#     size = 200
#     angle = -grab_angle - math.pi / 2
#     if ball.x > 0:
#         middle = aux.Point(120, 680)
#     else:
#         middle = aux.Point(1080, 680)

#     field.router_image.draw_rect(middle.x - size / 2, middle.y - size / 2, size, size, (200, 200, 200))
#     field.router_image.print(
#         middle - aux.Point(0, size / 2 + 10),
#         "GRABBING A BALL",
#         need_to_scale=False,
#     )

#     ball_screen = middle - aux.Point(0, size // 2 - 30)
#     center_boarder = convert_to_screen(ball_screen, cord_scale, angle, ball, grab_point)
#     center_boarder += aux.RIGHT / 2  # чтобы не мерцало, хз
#     field.router_image.draw_line(ball_screen, center_boarder, size_in_pixels=3, need_to_scale=False)

#     right_boarder = convert_to_screen(ball_screen, 1, -const.GRAB_OFFSET_ANGLE, ball_screen, center_boarder)
#     field.router_image.draw_line(ball_screen, right_boarder, size_in_pixels=3, need_to_scale=False)

#     left_boarder = convert_to_screen(ball_screen, 1, const.GRAB_OFFSET_ANGLE, ball_screen, center_boarder)
#     field.router_image.draw_line(ball_screen, left_boarder, size_in_pixels=3, need_to_scale=False)

#     robot_screen = convert_to_screen(ball_screen, cord_scale, angle, ball, robot_pos)
#     cropped_robot = aux.Point(
#         aux.minmax(robot_screen.x, middle.x - size / 2, middle.x + size / 2),
#         aux.minmax(robot_screen.y, middle.y - size / 2, middle.y + size / 2),
#     )
#     field.router_image.draw_circle(cropped_robot, (0, 0, 0), 80, False)

#     if cropped_robot == robot_screen:
#         vel_to_align_screen = convert_to_screen(robot_screen, vel_scale, angle, aux.Point(0, 0), vel_to_align)
#         field.router_image.draw_line(robot_screen, vel_to_align_screen, (100, 100, 200), 2, need_to_scale=False)
#         vel_to_catch_screen = convert_to_screen(robot_screen, vel_scale, angle, aux.Point(0, 0), vel_to_catch)
#         field.router_image.draw_line(robot_screen, vel_to_catch_screen, (200, 100, 100), 2, need_to_scale=False)
#         vel_screen = convert_to_screen(robot_screen, vel_scale, angle, aux.Point(0, 0), vel)
#         field.router_image.draw_line(robot_screen, vel_screen, (200, 100, 200), 3, need_to_scale=False)

#     field.router_image.draw_circle(ball_screen, (255, 100, 100), 50, False)


def spin_with_ball(w: float, flag: bool = False) -> tuple[aux.Point, float]:
    """
    Расчёт скорости робота для поворота с мячом с угловой скоростью w (рад/сек)
    """
    _w = w + 0.0
    if 0.01 < abs(w) < 0.4:
        _w = math.copysign(0.4, w)

    if _w > 0:
        delta_r = aux.Point(50, 25)
    else:
        delta_r = aux.Point(-50, 25)

    if flag:
        delta_r = aux.Point(0, 0)

    vel = delta_r * _w

    return vel, -_w


def convert_to_screen(
    ball_screen: aux.Point,
    scale: float,
    angle: float,
    ball: aux.Point,
    point: aux.Point,
) -> aux.Point:
    """Convert cord on field to cord on image"""
    vec_from_ball = point - ball
    scaled_vec = vec_from_ball * scale
    rotated_vec = aux.rotate(scaled_vec, angle)
    final_point = ball_screen + rotated_vec
    return final_point


def calc_passthrough_wp(
    domain: ActionDomain, target: aux.Point, *, avoid_ball: bool = False, ignore_ball: bool = False
) -> Optional[aux.Point]:
    """
    Рассчитать ближайшую промежуточную путевую точку
    согласно первому приближению векторного поля
    """
    robot = domain.robot
    field = domain.field

    obstacles_dist: list[tuple[Entity, float]] = []

    if not ignore_ball:
        ball = field.ball
        if avoid_ball:
            ball = Entity(
                field.ball.get_pos(),
                field.ball.get_angle(),
                const.KEEP_BALL_DIST - const.ROBOT_R,
            )

        if (
            len(aux.line_circle_intersect(robot.get_pos(), target, ball.get_pos(), const.ROBOT_R + ball.get_radius(), "S"))
            > 0
        ):
            obstacles_dist.append((ball, aux.dist(ball.get_pos(), robot.get_pos())))

    for obstacle in field.enemies + field.allies:
        dist = (obstacle.get_pos() - robot.get_pos()).mag()
        if obstacle.is_used() and obstacle.get_radius() + robot.get_radius() < dist < const.VIEW_DIST:
            obstacles_dist.append((obstacle.to_entity(), dist))

    sorted_obstacles = sorted(obstacles_dist, key=lambda x: x[1])

    obstacles = []
    for obst in sorted_obstacles:
        obstacles.append(obst[0])

    pth_point = calc_next_point(field, robot.get_pos(), target, domain.robot, obstacles)
    if pth_point is None:
        return None
    field.path_image.draw_line(robot.get_pos(), pth_point[0], color=(0, 0, 0))
    if pth_point[0] == target:
        return None

    return pth_point[0]


def calc_next_point(
    field: fld.Field,
    position: aux.Point,
    target: aux.Point,
    robot: rbt.Robot,
    obstacles: list[Entity],
) -> Optional[tuple[aux.Point, float]]:
    """Calculate next point for robot"""
    remaining_obstacles: list[Entity] = obstacles.copy()
    skipped_obstacles: list[Entity] = []
    while len(remaining_obstacles) > 0:
        obstacle = remaining_obstacles.pop(0)
        skipped_obstacles.append(obstacle)

        time_to_reach = aux.dist(obstacle.get_pos(), position) / const.MAX_SPEED
        center = obstacle.get_pos() + obstacle.get_vel() * time_to_reach
        radius = (
            obstacle.get_radius()
            + const.ROBOT_R
            + const.ROBOT_R * (robot.get_vel().mag() / const.MAX_SPEED) * 1  # <-- coefficient of fear [0; 1] for fast speed
            + time_to_reach * obstacle.get_vel().mag() * 0.5  # <-- coefficient of fear [0; 1], for moving obst
        )
        field.path_image.draw_circle(
            center,
            (127, 127, 127),
            radius,
        )
        if len(aux.line_circle_intersect(position, target, center, radius, "S")) > 0:
            tangents = aux.get_tangent_points(center, position, radius)
            if tangents is None or len(tangents) < 2:
                return None

            tangents[0] = aux.point_on_line(
                center,
                tangents[0],
                radius + const.ROBOT_R * 0.5,
            )
            tangents[1] = aux.point_on_line(
                center,
                tangents[1],
                radius + const.ROBOT_R * 0.5,
            )

            path_before0 = calc_next_point(field, position, tangents[0], robot, skipped_obstacles[:-1])
            path_before1 = calc_next_point(field, position, tangents[1], robot, skipped_obstacles[:-1])
            path_after0 = calc_next_point(field, tangents[0], target, robot, remaining_obstacles)
            path_after1 = calc_next_point(field, tangents[1], target, robot, remaining_obstacles)

            if (path_before0 is None or path_after0 is None) and (path_before1 is not None and path_after1 is not None):
                pth_point = path_before1[0]
                length = path_before1[1] + path_after1[1]
                return pth_point, length
            if (path_before0 is not None and path_after0 is not None) and (path_before1 is None or path_after1 is None):
                if path_after0 is None:
                    return None
                pth_point = path_before0[0]
                length = path_before0[1] + path_after0[1]
                return pth_point, length
            if (path_before0 is not None and path_after0 is not None) and (
                path_before1 is not None and path_after1 is not None
            ):

                length0 = path_before0[1] + path_after0[1]
                length1 = path_before1[1] + path_after1[1]
                in_zone0 = aux.is_point_inside_poly(path_before0[0], field.ally_goal.big_hull) or aux.is_point_inside_poly(
                    path_before0[0], field.enemy_goal.big_hull
                )
                in_zone1 = aux.is_point_inside_poly(path_before1[0], field.ally_goal.big_hull) or aux.is_point_inside_poly(
                    path_before1[0], field.enemy_goal.big_hull
                )

                if (length0 < length1 or in_zone1) and not in_zone0:
                    pth_point = path_before0[0]
                    length = path_before0[1] + path_after0[1]
                    field.path_image.draw_line(position, pth_point, color=(255, 0, 255))
                    return pth_point, length
                if (length1 < length0 or in_zone0) and not in_zone1:
                    pth_point = path_before1[0]
                    length = path_before1[1] + path_after1[1]
                    field.path_image.draw_line(position, pth_point, color=(255, 0, 255))
                    return pth_point, length

            return None

    field.path_image.draw_line(position, target, color=(255, 0, 127))
    return target, aux.dist(position, target)
