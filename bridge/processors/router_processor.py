"""
Модуль-прослойка между стратегией и отправкой пакетов на роботов
"""

from time import sleep, time
from typing import List, Optional

import attr
import attrs
import zmq
from cattrs import unstructure
from strategy_bridge.bus import DataBus, DataReader, DataWriter
from strategy_bridge.processors import BaseProcessor

from bridge import const, drawing
from bridge.auxiliary import aux, fld, rbt
from bridge.processors.python_controller import RobotCommand
from bridge.router.action import Action, ActionDomain, ActionValues

UDP_IP = "10.0.120.210"
UDP_PORT = 10000


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
        self.s_control.connect("tcp://127.0.0.1:5051")

    def process(self) -> None:
        """
        Метод обратного вызова процесса
        """
        telemetry_message = drawing.get_wave() + "\n"
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
                team_message: str = (
                    f"TEAM {str(color)}\n \tr_id\tvelX\tvelY\tvelR\tangle\tkickUP\tkickFRW\tautoUP\tautoFRW\tvolt\tdrib\n"
                )
                team_commands: list[DecoderCommand] = []
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

                        cur_command = command_from_values(domain.field, domain.robot, values)
                        team_commands.append(cur_command)
                        team_message += create_telemetry(cur_command)

                if len(team_commands) > 0:
                    control_data = DecoderTeamCommand(
                        robot_commands=team_commands,
                        isteamyellow=(color == const.Color.YELLOW),
                    )

                    self.s_control.send_json({"control": "actuate_robot", "data": unstructure(control_data)})

                telemetry_message += team_message

            self.field[const.COLOR].router_image.timer.end(time())
            self.image_writer.write(self.field[const.COLOR].path_image)
            self.field_b.clear_images()
            self.field_y.clear_images()

        self.field[const.COLOR].router_image.send_telemetry("COMMANDS TO ROBOTS", telemetry_message)
        self.image_writer.write(self.field[const.COLOR].router_image)

    def finalize(self) -> None:

        team_commands: list[DecoderCommand] = []
        for r_id in range(const.TEAM_ROBOTS_MAX_COUNT):
            team_commands.append(
                DecoderCommand(
                    robot_id=r_id,
                    kick_up=False,
                    kick_forward=False,
                    auto_kick_up=False,
                    auto_kick_forward=False,
                    kicker_setting=0,
                    dribbler_setting=0,
                    forward_vel=0,
                    left_vel=0,
                    angular_vel=0,
                )
            )

        for _ in range(5):
            for team in [True, False]:
                control_data = DecoderTeamCommand(robot_commands=team_commands, isteamyellow=team)
                self.s_control.send_json({"control": "actuate_robot", "data": unstructure(control_data)})
            sleep(0.002)

        self.s_control.close()


def command_from_values(field: fld.Field, robot: rbt.Robot, values: ActionValues) -> "DecoderCommand":
    """Turn ActionValues to commands for robots"""

    if values.beep == 0:
        robot.update_vel_xy(values.vel)
        aerr = aux.wind_down_angle(values.angle - robot.get_angle())
        if const.IS_SIMULATOR_USED:
            ang_vel = robot.angle_reg.process(aerr, -robot.get_anglevel())
            robot.update_vel_w(ang_vel)
        else:
            robot.delta_angle = aerr

        reg_vel = aux.Point(robot.speed_x, -robot.speed_y)
        field.router_image.draw_line(
            robot.get_pos(),
            robot.get_pos() + aux.rotate(reg_vel, robot.get_angle()) * 50,
        )
    else:
        # print("manual speeds: ", values.vel, values.angle)

        robot.speed_x = -1 / robot.k_xx * values.vel.x
        robot.speed_y = 1 / robot.k_yy * values.vel.y
        if const.IS_SIMULATOR_USED:
            robot.update_vel_w(values.angle)
        else:
            robot.delta_angle = values.angle

    # return RobotCommand(
    #     id=r_id,
    #     move_command=RobotMoveCommand(
    #         # wheel_velocity=MoveWheelVelocity(
    #         #     front_right=0,
    #         #     back_right=0,
    #         #     back_left=0,
    #         #     front_left=1,
    #         # )
    #         local_velocity=MoveLocalVelocity(
    #             forward=-domain.robot.speed_x,
    #             left=-domain.robot.speed_y,
    #             angular=domain.robot.speed_r,
    #         ),
    #         # global_velocity=MoveGlobalVelocity(
    #         #     x=1,
    #         #     y=0,
    #         #     angular=0,
    #         # ),
    #     ),
    #     kick_speed=kick_speed,
    #     kick_angle=kick_angle,
    #     dribbler_speed=values.dribbler_speed,
    # )

    return DecoderCommand(
        robot_id=robot.r_id,
        kick_up=values.kick_up,
        kick_forward=values.kick_forward,
        auto_kick_up=values.auto_kick == 2,
        auto_kick_forward=values.auto_kick == 1,
        kicker_setting=values.kicker_voltage,
        dribbler_setting=values.dribbler_speed,
        forward_vel=robot.speed_x,
        left_vel=-robot.speed_y,
        angular_vel=robot.speed_r,
    )


def create_telemetry(cmd: "DecoderCommand") -> str:
    """Create line for telemetry for single robot"""
    values = [
        str(cmd.robot_id),
        f"{cmd.forward_vel:.2f}",
        f"{cmd.left_vel:.2f}",
        f"{cmd.angular_vel:.2f}" if cmd.angular_vel is not None else "None",
        f"{cmd.angle:.2f}" if cmd.angle is not None else "None",
        str(cmd.kick_up),
        str(cmd.kick_forward),
        str(cmd.auto_kick_up),
        str(cmd.auto_kick_forward),
        str(cmd.kicker_setting),
        str(cmd.dribbler_setting),
    ]
    return "\t" + "\t".join(values) + "\n"


@attrs.define
class DecoderCommand:
    robot_id: int = attrs.field()

    kick_up: bool = attrs.field()
    kick_forward: bool = attrs.field()
    auto_kick_up: bool = attrs.field()
    auto_kick_forward: bool = attrs.field()

    kicker_setting: int = attrs.field()  # 0-15 [popugi]
    dribbler_setting: float = attrs.field()  # 0-15 [popugi]

    forward_vel: float = attrs.field()  # [m/s]
    left_vel: float = attrs.field()  # [m/s]
    angular_vel: Optional[float] = attrs.field(default=None)  # [rad/s]
    angle: Optional[float] = attrs.field(default=None)  # [rad]


@attrs.define
class DecoderTeamCommand:
    robot_commands: List[DecoderCommand] = attrs.field(factory=list)
    isteamyellow: bool = attrs.field(default=False)
