"""
draw field with robots and trajectory
"""

import math
import time
from enum import Enum
from typing import Any

from bridge.auxiliary import aux


class ImageTopic(Enum):
    """Topic for commands to draw"""

    STRATEGY = 0
    ROUTER = 1
    PATH_GENERATION = 2

    FIELD = 10


class Image:
    """
    class with image's specs
    """

    def __init__(self, topic: ImageTopic) -> None:
        self.topic: ImageTopic = topic
        self.timer: FeedbackTimer = FeedbackTimer(0, 1, 1)
        self.telemetry: list[tuple[str, str]] = []  # name and line

        self.data: list[dict[str, Any]] = []

    def clear(self) -> None:
        """clear the image"""
        self.data = []

    def draw_circle(
        self,
        pos: aux.Point,
        color: tuple[int, int, int] = (255, 0, 0),
        size_in_mms: float = 10,
    ) -> None:
        """draw single point"""
        self.data.append(
            {
                "type": "circle",
                "x": pos.x,
                "y": pos.y,
                "radius": size_in_mms,
                "color": "#{:02X}{:02X}{:02X}".format(*color),
            }
        )

    def draw_line(
        self,
        dot1: aux.Point,
        dot2: aux.Point,
        color: tuple[int, int, int] = (200, 200, 200),
        size_in_pixels: int = 10,
    ) -> None:
        """draw line"""
        self.data.append(
            {
                "type": "line",
                "x_list": [dot1.x, dot2.x],
                "y_list": [dot1.y, dot2.y],
                "color": "#{:02X}{:02X}{:02X}".format(*color),
                "width": size_in_pixels,
            }
        )

    def draw_poly(
        self,
        dots: list[aux.Point],
        color: tuple[int, int, int] = (255, 255, 255),
        size_in_pixels: int = 2,
    ) -> None:
        """Connect nearest dots with line"""
        x_list = [dot.x for dot in dots]
        y_list = [dot.y for dot in dots]
        self.data.append(
            {
                "type": "polygon",
                "x_list": x_list,
                "y_list": y_list,
                "color": "#{:02X}{:02X}{:02X}".format(*color),
                "width": size_in_pixels,
            }
        )

    def draw_rect(
        self,
        left: float,
        top: float,
        width: float,
        heigh: float,
        color: tuple[int, int, int] = (127, 127, 127),
    ) -> None:
        """Draw and fill the rectangle"""
        self.data.append(
            {
                "type": "rect",
                "x": left,
                "y": top,
                "width": width,
                "height": heigh,
                "color": "#{:02X}{:02X}{:02X}".format(*color),
            }
        )

    # def draw_robot(
    #     self,
    #     pos: aux.Point,
    #     angle: float = 0.0,
    #     color: tuple[int, int, int] = (0, 0, 255),
    # ) -> None:
    #     """draw robot"""
    #     robot_type = "robot_blu"
    #     if color == (255, 255, 0):
    #         robot_type = "robot_yel"
    #     self.data.append(
    #         {
    #             "type": robot_type,
    #             "x": pos.x,
    #             "y": pos.y,
    #             "rotation": angle,
    #         }
    #     )

    def print(
        self,
        pos: aux.Point,
        text: str,
        color: tuple[int, int, int] = (255, 255, 255),
        need_to_scale: bool = True,
    ) -> None:
        """print text"""
        # TODO
        return

    def send_telemetry(self, name: str, new_telemetry: str) -> None:
        """Send new string to telemetry console"""
        self.telemetry.append((name, new_telemetry))


class FeedbackTimer:
    """Class for timers on screen"""

    def __init__(self, time: float, delay_lim: float, tps_lim: float) -> None:
        """
        delay_lim - limit of min process long
        tps_lim - limit of min tics per second for processor
        """

        self.delay = 0.0
        self.delay_lim = delay_lim  # in seconds
        self.delay_timer = 0.0
        self.delay_warning = False

        self.tps = 0.0
        self.tps_lim = tps_lim  # in ticks per seconds
        self.tps_timer = 0.0
        self.tps_warning = False

        self.memory: list[float] = []
        self.memory_long = 2.0  # in seconds

        self.last_update = time

    def start(self, time: float) -> None:
        """Start timer when processor starts"""
        self.last_update = time
        self.clean_memory()
        self.memory.append(time)
        if len(self.memory) > 1:
            self.tps = (len(self.memory) - 1) / (self.memory[-1] - self.memory[0])
            if self.tps < self.tps_lim:
                self.tps_timer = time

    def end(self, time: float) -> None:
        """End timer when processor ends"""
        self.delay = time - self.last_update
        if self.delay > self.delay_lim:
            self.delay_timer = time

        self.delay_warning = time - self.delay_timer < self.memory_long
        self.tps_warning = time - self.tps_timer < self.memory_long

    def clean_memory(self) -> None:
        """Clean old data from 'self.memory'"""
        memory = self.memory.copy()
        for data in self.memory:
            if data < self.last_update - self.memory_long:
                memory.pop(0)
            else:
                break
        self.memory = memory


def get_wave() -> str:
    wave_chars = "_▁▂▃▄▅▆▇█"

    width = 40  # ширина строки
    length = len(wave_chars)

    line = ""
    for x in range(width):
        # Для плавного волнообразного эффекта используем синус с фазовым сдвигом по позиции
        height_index = int((math.sin(time.time() + (x / width) * 2 * math.pi) + 1) / 2 * (length - 1))
        line += wave_chars[height_index]

    return line
