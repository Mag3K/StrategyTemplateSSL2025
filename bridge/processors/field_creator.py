"""Processor that creates the field"""

from time import time
from typing import Optional

import attr
from strategy_bridge.bus import DataBus, DataReader, DataWriter
from strategy_bridge.common import config
from strategy_bridge.larcmacs.receiver import ZmqReceiver
from strategy_bridge.pb.messages_robocup_ssl_wrapper_pb2 import SSL_WrapperPacket
from strategy_bridge.processors import BaseProcessor

from bridge import const, drawing
from bridge.auxiliary import aux, fld
from bridge.processors.referee_state_processor import RefereeStateProcessor, State


@attr.s(auto_attribs=True)
class FieldCreator(BaseProcessor):
    """class that creates the field"""

    processing_pause: Optional[float] = 0.001
    reduce_pause_on_process_time: bool = False
    _ssl_converter: SSL_WrapperPacket = attr.ib(init=False)

    # for RefereeStateProcessor
    debug_mode: bool = False
    debug_game_state: State = State.STOP
    debug_active_team: const.Color = const.Color.ALL
    debug_preparation_delay: float = 5.0
    # time in seconds before command free_kick, kickoff or penalty

    def initialize(self, data_bus: DataBus) -> None:
        """
        Инициализация
        """
        super().initialize(data_bus)
        self.field_receiver = ZmqReceiver(port=config.VISION_DETECTIONS_SUBSCRIBE_PORT)

        self.box_feedback_reader = DataReader(data_bus, config.BOX_FEEDBACK_TOPIC)
        self.field_writer = DataWriter(data_bus, const.FIELD_TOPIC, 1)
        self._ssl_converter = SSL_WrapperPacket()
        self.field = fld.Field(const.COLOR)
        self.field.field_image.timer = drawing.FeedbackTimer(time(), 5, 30)

        self.referee_processor = RefereeStateProcessor(
            debug_mode=self.debug_mode,
            debug_game_state=self.debug_game_state,
            debug_active_team=self.debug_active_team,
            debug_preparation_delay=self.debug_preparation_delay,
        )

    def process(self) -> None:
        self.process_field()
        cur_state = self.referee_processor.process(self.field)
        self.field.game_state, self.field.active_team = cur_state

    def process_field(self) -> None:
        """
        Метод обратного вызова процесса
        """

        queue = []
        message = self.field_receiver.next_message()
        while message is not None:
            queue.append(message)
            message = self.field_receiver.next_message()

        if len(queue) == 0:
            return

        self.field.field_image.timer.start(time())

        # print("field delay:", time() - self.field.last_update)
        balls: list[aux.Point] = []
        b_bots_id: list[int] = []
        b_bots_pos: list[list] = [[] for _ in range(const.TEAM_ROBOTS_MAX_COUNT)]
        b_bots_ang: list[list] = [[] for _ in range(const.TEAM_ROBOTS_MAX_COUNT)]

        y_bots_id: list[int] = []
        y_bots_pos: list[list] = [[] for _ in range(const.TEAM_ROBOTS_MAX_COUNT)]
        y_bots_ang: list[list] = [[] for _ in range(const.TEAM_ROBOTS_MAX_COUNT)]
        # field_info = np.zeros(const.GEOMETRY_PACKET_SIZE)

        for ssl_package in queue:
            try:
                ssl_package_content = self._ssl_converter.FromString(ssl_package)
            except AttributeError:  # TODO понять и сделать везде
                continue

            # ssl_package_content = self._ssl_converter.FromString(ssl_package_content)
            # geometry = ssl_package_content.geometry
            # if geometry:
            #     field_info[0] = geometry.field.field_length
            #     field_info[1] = geometry.field.field_width
            #     if geometry.field.field_length != 0 and geometry.field.goal_width != 0:
            #         const.GOAL_DX = geometry.field.field_length / 2
            #         const.GOAL_DY = geometry.field.goal_width

            detection = ssl_package_content.detection
            for ball in detection.balls:
                if ball.x * const.DEBUG_HALF < 0:
                    continue
                balls.append(aux.Point(ball.x, ball.y))

            for robot_det in detection.robots_blue:
                if robot_det.x * const.DEBUG_HALF < 0:
                    continue
                b_bots_id.append(robot_det.robot_id)
                b_bots_pos[robot_det.robot_id].append(aux.Point(robot_det.x, robot_det.y))
                b_bots_ang[robot_det.robot_id].append(robot_det.orientation)

            for robot_det in detection.robots_yellow:
                if robot_det.x * const.DEBUG_HALF < 0:
                    continue
                y_bots_id.append(robot_det.robot_id)
                y_bots_pos[robot_det.robot_id].append(aux.Point(robot_det.x, robot_det.y))
                y_bots_ang[robot_det.robot_id].append(robot_det.orientation)

        new_ball_pos = filter_fake_detections(
            self.field.ball.get_pos(),
            self.field.ball_real_update_time,
            const.BALL_MAX_VISION_SPEED,
            balls,
        )
        if new_ball_pos is not None:
            self.field.update_ball(new_ball_pos[0], time())
            self.field.ball_real_update_time = time()
        else:
            cur_state = self.referee_processor.state_machine.get_state()
            if cur_state[0] == State.RUN:
                if self.field.robot_with_ball is not None:
                    ally = self.field.robot_with_ball
                    ball = ally.get_pos() + aux.rotate(aux.RIGHT, ally.get_angle()) * 90
                    self.field.update_ball(ball, time())
            else:
                if self.field.robot_with_ball is not None:
                    ally = self.field.robot_with_ball
                    ball = ally.get_pos() + aux.rotate(aux.RIGHT, ally.get_angle()) * 90
                    self.field.update_ball(ball, time())

        self.field.update_ball_history()

        for r_id in set(b_bots_id):
            blue_robot = self.field.get_blu_team()[r_id]
            new_pos = filter_fake_detections(
                blue_robot.get_pos(),
                blue_robot.last_update(),
                const.ROBOT_MAX_VISION_SPEED,
                b_bots_pos[r_id],
                b_bots_ang[r_id],
            )
            if new_pos is not None:
                self.field.update_blu_robot(r_id, new_pos[0], new_pos[1], time())

            live_time = self.field.b_team[r_id].live_time()
            if live_time is not None and time() - live_time > const.TIME_TO_BORN:
                self.field.b_team[r_id].used(1)
        for robot in self.field.b_team:
            if time() - robot.last_update() > const.TIME_TO_DIE:
                robot.used(0)

        for r_id in set(y_bots_id):
            yellow_robot = self.field.get_yel_team()[r_id]
            new_pos = filter_fake_detections(
                yellow_robot.get_pos(),
                yellow_robot.last_update(),
                const.ROBOT_MAX_VISION_SPEED,
                y_bots_pos[r_id],
                y_bots_ang[r_id],
            )
            if new_pos is not None:
                self.field.update_yel_robot(r_id, new_pos[0], new_pos[1], time())

            live_time = self.field.y_team[r_id].live_time()
            if live_time is not None and time() - live_time > const.TIME_TO_BORN:
                self.field.y_team[r_id].used(1)
        for robot in self.field.y_team:
            if time() - robot.last_update() > const.TIME_TO_DIE:
                robot.used(0)

        active_allies = []
        for r in self.field.allies:
            if r.is_used() and r.r_id != self.field.gk_id:
                active_allies.append(r)
        self.field.update_active_allies(active_allies)

        active_enemies = []
        for r in self.field.enemies:
            if r.is_used() and r.r_id != self.field.enemy_gk_id:
                active_enemies.append(r)
        self.field.update_active_enemies(active_enemies)

        ENABLE_FEEDBACK = False
        if ENABLE_FEEDBACK:
            feedback_record = self.box_feedback_reader.read_last()
            if feedback_record:
                result = {}
                for _, value in feedback_record.content.items():
                    if isinstance(value, dict) and "address" in value and "ball_checker" in value:
                        result[value["address"]] = bool(value["ball_checker"])
                for key, value in result.items():
                    if value and self.field.allies[int(key)].is_used():
                        self.field.robot_with_ball = self.field.allies[int(key)]

            if self.field.robot_with_ball is not None:
                if not self.field._is_ball_in(self.field.robot_with_ball):
                    self.field.robot_with_ball = None
            if self.field.robot_with_ball is None:
                for r in self.field.enemies:
                    if self.field._is_ball_in(r):
                        self.field.robot_with_ball = r
        else:
            self.field.robot_with_ball = None
            for r in self.field.enemies:
                if self.field._is_ball_in(r):
                    self.field.robot_with_ball = r
            for r in self.field.allies:
                if self.field._is_ball_in(r):
                    self.field.robot_with_ball = r
        self.field.last_update = time()
        self.field.field_image.timer.end(time())
        lite_field = fld.LiteField(self.field)
        self.field_writer.write(lite_field)


def filter_fake_detections(
    old_pos: aux.Point,
    last_update: float,
    max_vision_speed: float,
    new_poses: list[aux.Point],
    angles: Optional[list[float]] = None,
) -> Optional[tuple[aux.Point, float]]:
    """Filter out unrealistic coordinates from camera"""
    correct_poses: list[aux.Point] = []
    correct_angles: list[float] = []
    for i, new_pos in enumerate(new_poses):
        if const.IS_SIMULATOR_USED or (
            new_pos != old_pos or (new_pos - old_pos).mag() / (time() - last_update) < max_vision_speed
        ):
            correct_poses.append(new_pos)
            if angles is not None:
                correct_angles.append(angles[i])

    if len(correct_poses) == 0:
        return None

    new_pos = aux.average_point(correct_poses)
    new_angle = 0.0
    if angles is not None:
        new_angle = aux.average_angle(correct_angles)

    return new_pos, new_angle
