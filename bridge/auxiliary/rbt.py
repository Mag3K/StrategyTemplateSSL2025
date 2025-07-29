"""
Описание полей и интерфейсов взаимодействия с роботом
"""

import typing
from time import time

from bridge import const
from bridge.auxiliary import aux, entity, tau


class Robot(entity.Entity):
    """
    Описание робота
    """

    def __init__(
        self,
        pos: aux.Point,
        angle: float,
        R: float,
        color: const.Color,
        r_id: int,
    ) -> None:
        super().__init__(pos, angle, R)

        self.r_id = r_id
        self._is_used = 0
        self.color = color
        self.last_update_ = 0.0
        self.live_time_: typing.Optional[float] = None

        self.speed_x = 0.0
        self.speed_y = 0.0
        self.speed_r = 0.0
        self.delta_angle = 0.0
        self.kick_up_ = 0
        self.kick_forward_ = 0
        self.auto_kick_ = 0
        self.kicker_voltage_ = 0
        self.dribbler_enable_ = 0
        self.dribbler_speed_ = 0
        self.kicker_charge_enable_ = 0
        self.beep = 0

        # v! SIM
        if const.IS_SIMULATOR_USED:
            self.k_wy = -0.001
            self.t_wy = 0.15
            self.r_comp_f_dy = tau.FOD(self.t_wy, const.Ts)
            self.r_comp_f_fy = tau.FOLP(self.t_wy, const.Ts)

        # v! REAL
        else:
            self.k_wy = 0
            self.t_wy = 0.15
            self.r_comp_f_dy = tau.FOD(self.t_wy, const.Ts)
            self.r_comp_f_fy = tau.FOLP(self.t_wy, const.Ts)

        self.xx_t = 0.1
        self.xx_flp = tau.FOLP(self.xx_t, const.Ts)
        self.yy_t = 0.1
        self.yy_flp = tau.FOLP(self.yy_t, const.Ts)

        # !v REAL
        gains_full = [2.5, 0.07, 0.05, const.MAX_SPEED]
        gains_soft = gains_full
        a_gains_full = [15, 0.5, 0, const.MAX_SPEED_R]
        if const.IS_SIMULATOR_USED:
            # gains_full = [8, 0.35, 0, const.MAX_SPEED]
            #            Prop  Diff  Int
            gains_full = [1.8, 0.06, 0.0, const.MAX_SPEED]
            gains_soft = gains_full
            a_gains_full = [8, 0.1, 0.1, const.MAX_SPEED_R]

        a_gains_soft = a_gains_full

        self.pos_reg_x = tau.PISD(
            const.Ts,
            [gains_full[0], gains_soft[0]],
            [gains_full[1], gains_soft[1]],
            [gains_full[2], gains_soft[2]],
            [gains_full[3], gains_soft[3]],
        )
        self.pos_reg_y = tau.PISD(
            const.Ts,
            [gains_full[0], gains_soft[0]],
            [gains_full[1], gains_soft[1]],
            [gains_full[2], gains_soft[2]],
            [gains_full[3], gains_soft[3]],
        )
        self.angle_reg = tau.PISD(
            const.Ts,
            [a_gains_full[0], a_gains_soft[0]],
            [a_gains_full[1], a_gains_soft[1]],
            [a_gains_full[2], a_gains_soft[2]],
            [a_gains_full[3], a_gains_soft[3]],
        )

        self.is_kick_committed = False

        self.prev_sended_vel = aux.Point(0, 0)
        self.prev_sended_time = time()
        self.prev_sended_angle = 0.0

    def __eq__(self, robo: typing.Any) -> bool:
        if not isinstance(robo, Robot):
            return False
        return self.r_id == robo.r_id and self.color == robo.color

    def to_entity(self) -> entity.Entity:
        """convert to entity"""
        ent = entity.Entity(self._pos, self._angle, self._radius)
        ent._vel = self._vel
        # ent._acc = self._acc
        return ent

    def used(self, a: int) -> None:
        """
        Выставить флаг использования робота
        """
        self._is_used = a

        if a == 0:
            self.live_time_ = None

    def is_used(self) -> int:
        """returns true if the robot is used"""
        return self._is_used

    def last_update(self) -> float:
        """get the robot's last update time"""
        return self.last_update_

    def live_time(self) -> typing.Optional[float]:
        """get the robot's lifetime"""
        return self.live_time_

    def update(self, pos: aux.Point, angle: float, t: float) -> None:
        """
        Обновить состояние робота согласно SSL Vision
        """
        super().update(pos, angle, t)
        self.kick_forward_ = 0
        self.kick_up_ = 0
        self.last_update_ = t

        if self.live_time_ is None:
            self.live_time_ = t

    def update_(self, lite_robot: "LiteRobot") -> None:
        """
        Обновить состояние робота используя готовые данные
        """
        self._pos = lite_robot.pos
        self._vel = lite_robot.vel
        self._angle = lite_robot.angle
        self._anglevel = lite_robot.anglevel

        self._is_used = lite_robot.is_used
        self.last_update_ = lite_robot.is_used

    def kick_forward(self) -> None:
        """
        Ударить вперед
        """
        self.kick_forward_ = 1

    def kick_up(self) -> None:
        """
        Ударить вверх
        """
        self.kick_up_ = 1

    def set_dribbler_speed(self, speed: float) -> None:
        """
        Включить дриблер и задать его скорость
        """
        self.dribbler_enable_ = True
        self.dribbler_speed_ = round(aux.minmax(speed, 0.0, 15.0))

    def clear_fields(self) -> None:
        """
        Очистить поля управления
        """
        self.speed_x = 0.0
        self.speed_y = 0.0
        self.speed_r = 0.0
        self.delta_angle = 0.0
        self.kick_up_ = 0
        self.kick_forward_ = 0
        self.auto_kick_ = 0
        self.kicker_voltage_ = 0
        self.dribbler_enable_ = 0
        self.dribbler_speed_ = 0
        self.kicker_charge_enable_ = 0
        self.beep = 0

    def is_kick_aligned(self, pos: aux.Point, angle: float) -> bool:
        """
        Определить, выровнен ли робот относительно путевой точки target
        """

        commit_scale = 1.2 if self.is_kick_committed else 1
        is_dist = (self.get_pos() - pos).mag() < const.KICK_ALIGN_DIST * const.KICK_ALIGN_DIST_MULT * commit_scale
        is_angle = self.is_kick_aligned_by_angle(angle)
        is_offset = (
            aux.dist(
                aux.closest_point_on_line(
                    pos,
                    pos - aux.rotate(aux.RIGHT, angle) * const.KICK_ALIGN_DIST,
                    self._pos,
                ),
                self._pos,
            )
            < const.KICK_ALIGN_OFFSET * commit_scale
        )
        is_aligned = is_dist and is_angle and is_offset

        if is_aligned:
            self.is_kick_committed = True
        else:
            self.is_kick_committed = False

        return is_aligned

    def is_kick_aligned_by_angle(self, angle: float, *, angle_bounds: float = const.KICK_ALIGN_ANGLE) -> bool:
        """
        Определить, выровнен ли робот относительно путевой точки target
        """
        commit_scale = 1.2 if self.is_kick_committed else 1
        return abs(aux.wind_down_angle(self._angle - angle)) < angle_bounds * commit_scale

    def update_vel_xy(self, vel: aux.Point) -> None:
        """
        Выполнить тик низкоуровневых регуляторов скорости робота

        vel - требуемый вектор скорости [мм/с]
        """
        global_speed_x = self.xx_flp.process(vel.x)
        global_speed_y = self.yy_flp.process(vel.y)

        global_speed = aux.Point(global_speed_x, global_speed_y)

        speed = -aux.rotate(global_speed, -self._angle)
        self.speed_x = -speed.x
        self.speed_y = speed.y

        # if abs(self.speed_r) > const.MAX_SPEED_R:
        #     self.speed_r = math.copysign(const.MAX_SPEED_R, self.speed_r)

        # vec_speed = math.sqrt(self.speed_x**2 + self.speed_y**2)
        # r_speed = abs(self.speed_r)
        # if not const.IS_SIMULATOR_USED:
        #     vec_speed *= abs((const.MAX_SPEED_R - r_speed) / const.MAX_SPEED_R) ** 2
        # ang = math.atan2(self.speed_y, self.speed_x)

        # self.speed_x = vec_speed * math.cos(ang)
        # self.speed_y = vec_speed * math.sin(ang)

    def update_vel_w(self, wvel: float) -> None:
        """Update robot angle vel"""
        self.speed_r = wvel

    def update_vel_xy_(self, vel: aux.Point, dT: float) -> None:
        """
        Выполнить тик низкоуровневых регуляторов скорости робота

        vel - требуемый вектор скорости [мм/с]
        """
        global_speed_x = self.xx_flp.process_(vel.x, dT)
        global_speed_y = self.yy_flp.process_(vel.y, dT)

        global_speed = aux.Point(global_speed_x, global_speed_y)

        speed = -aux.rotate(global_speed, -self._angle)

        self.speed_x = -speed.x
        self.speed_y = speed.y

        # if abs(self.speed_r) > const.MAX_SPEED_R:
        #     self.speed_r = math.copysign(const.MAX_SPEED_R, self.speed_r)

        # vec_speed = math.sqrt(self.speed_x**2 + self.speed_y**2)
        # r_speed = abs(self.speed_r)
        # if not const.IS_SIMULATOR_USED:
        #     vec_speed *= abs((const.MAX_SPEED_R - r_speed) / const.MAX_SPEED_R) ** 2
        # ang = math.atan2(self.speed_y, self.speed_x)

        # self.speed_x = vec_speed * math.cos(ang)
        # self.speed_y = vec_speed * math.sin(ang)

    def __str__(self) -> str:
        return (
            str(
                str(self.color)
                + " "
                + str(self.r_id)
                + " "
                + str(self.get_pos())
                + " "
                + str(self.speed_x)
                + " "
                + str(self.speed_y)
            )
            + " "
            + str(self.speed_r)
        )


class LiteRobot:
    """Lite class, to moving information about robot between processes"""

    def __init__(self, robot: Robot) -> None:
        self.r_id = robot.r_id

        self.pos = robot.get_pos()
        self.vel = robot.get_vel()
        self.angle = robot.get_angle()
        self.anglevel = robot.get_anglevel()

        self.is_used = robot.is_used()
        self.last_update = robot.last_update()
