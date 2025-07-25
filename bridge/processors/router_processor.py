"""
Модуль-прослойка между стратегией и отправкой пакетов на роботов
"""

from time import time
from typing import Optional

import attr
import zmq
from cattrs import unstructure
from strategy_bridge.bus import DataBus, DataReader, DataWriter
from strategy_bridge.processors import BaseProcessor

import bridge.robot_command_model as rcm
from bridge import const, drawing
from bridge.auxiliary import aux, fld
from bridge.processors.python_controller import RobotCommand
from bridge.router.action import Action, ActionDomain, ActionValues


@attr.s(auto_attribs=True)
class CommandSink(BaseProcessor):
    """
    Прослойка между стратегией и отправкой пакетов на роботов
    """

    processing_pause: Optional[float] = 0.001
    reduce_pause_on_process_time: bool = False

    def initialize(self, data_bus: DataBus) -> None:
        """
        Инициализация
        """
        super().initialize(data_bus)
        self.field_reader = DataReader(data_bus, const.FIELD_TOPIC)
        self.commands_sink_reader = DataReader(data_bus, const.CONTROL_TOPIC)
        self.image_writer = DataWriter(data_bus, const.IMAGE_TOPIC, 20)

        self.tmp_timer = time()

        self.field_b = fld.Field(const.Color.BLUE)
        self.field_y = fld.Field(const.Color.YELLOW)
        self.field: dict[const.Color, fld.Field] = {
            const.Color.BLUE: self.field_b,
            const.Color.YELLOW: self.field_y,
        }

        self.field[const.COLOR].router_image.timer = drawing.FeedbackTimer(time(), 10, 50)

        self.waypoints_b: list[Optional[Action]] = [None for _ in range(const.TEAM_ROBOTS_MAX_COUNT)]
        self.waypoints_y: list[Optional[Action]] = [None for _ in range(const.TEAM_ROBOTS_MAX_COUNT)]
        self.actions: dict[const.Color, list[Optional[Action]]] = {
            const.Color.BLUE: self.waypoints_b,
            const.Color.YELLOW: self.waypoints_y,
        }

        context = zmq.Context()
        self.s_control = context.socket(zmq.PUB)
        self.s_control.connect("tcp://192.168.1.131:5051")

    def process(self) -> None:
        """
        Метод обратного вызова процесса
        """
        updated = False

        new_field = self.field_reader.read_last()
        if new_field is not None:
            updated_field: fld.Field = new_field.content
            if self.field_b.last_update != updated_field.last_update:
                self.field_b.update_field(updated_field)
                self.field_y.update_field(updated_field)
                updated = True

        cmds = self.commands_sink_reader.read_new()
        for cmd in cmds:
            command: RobotCommand = cmd.content
            if command.color == const.Color.BLUE:
                self.waypoints_b[command.r_id] = command.action
            else:
                self.waypoints_y[command.r_id] = command.action
            updated = True

        if updated:
            self.field[const.COLOR].router_image.timer.start(time())
            for color in [const.Color.BLUE, const.Color.YELLOW]:
                team_commands: list[rcm.RobotCommand] = []
                for i in range(const.TEAM_ROBOTS_MAX_COUNT):
                    cur_action = self.actions[color][i]
                    if self.field[color].allies[i].is_used() and cur_action is not None:
                        self.field[color].allies[i].clear_fields()

                        domain = ActionDomain(
                            field=self.field[color],
                            game_state=self.field[color].game_state,
                            we_active=self.field[color].active_team in [const.Color.ALL, color],
                            robot=self.field[color].allies[i],
                        )
                        values = ActionValues()
                        cur_action.process(domain, values)

                        team_commands.append(command_from_values(i, values, domain))

                if len(team_commands) > 0:
                    control_data = rcm.RobotControlExt(
                        isteamyellow=color == const.Color.YELLOW, robot_commands=team_commands
                    )

                    self.s_control.send_json({"transnet": "actuate_robot", "data": unstructure(control_data)})

            self.field[const.COLOR].router_image.timer.end(time())
            self.image_writer.write(self.field[const.COLOR].router_image)
            self.image_writer.write(self.field[const.COLOR].path_image)
            self.field_b.clear_images()
            self.field_y.clear_images()


def command_from_values(r_id: int, values: ActionValues, domain: ActionDomain) -> rcm.RobotCommand:
    """Turn ActionValues to commands for robots"""

    if values.beep == 0:
        domain.robot.update_vel_xy(values.vel)
        aerr = aux.wind_down_angle(values.angle - domain.robot.get_angle())
        if const.IS_SIMULATOR_USED:
            ang_vel = domain.robot.angle_reg.process(aerr, -domain.robot.get_anglevel())
            domain.robot.update_vel_w(ang_vel)
        else:
            domain.robot.delta_angle = aerr

        reg_vel = aux.Point(domain.robot.speed_x, -domain.robot.speed_y)
        domain.field.router_image.draw_line(
            domain.robot.get_pos(),
            domain.robot.get_pos() + aux.rotate(reg_vel, domain.robot.get_angle()) * 10,
        )
    else:
        # print("manual speeds: ", values.vel, values.angle)

        domain.robot.speed_x = -1 / domain.robot.k_xx * values.vel.x
        domain.robot.speed_y = 1 / domain.robot.k_yy * values.vel.y
        if const.IS_SIMULATOR_USED:
            domain.robot.update_vel_w(values.angle)
        else:
            domain.robot.delta_angle = values.angle

    kick_speed = values.kicker_voltage / 2 if (values.kick_forward or values.kick_up or values.auto_kick) else 0
    kick_angle = 40 if (values.kick_up or values.auto_kick == 2) else 0

    return rcm.RobotCommand(
        id=r_id,
        move_command=rcm.RobotMoveCommand(
            # wheel_velocity=rcm.MoveWheelVelocity(
            #     front_right=0,
            #     back_right=0,
            #     back_left=0,
            #     front_left=1,
            # )
            local_velocity=rcm.MoveLocalVelocity(
                forward=-domain.robot.speed_x,
                left=-domain.robot.speed_y,
                angular=domain.robot.speed_r,
            ),
            # global_velocity=rcm.MoveGlobalVelocity(
            #     x=1,
            #     y=0,
            #     angular=0,
            # ),
        ),
        kick_speed=kick_speed,
        kick_angle=kick_angle,
        dribbler_speed=values.dribbler_speed,
    )
