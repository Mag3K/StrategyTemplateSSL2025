"""Processor for drawing"""

from typing import Any, Optional

import attr
import zmq
from strategy_bridge.bus import DataBus, DataReader
from strategy_bridge.processors import BaseProcessor

from bridge import const, drawing
from bridge.auxiliary import fld


@attr.s(auto_attribs=True)
class Drawer(BaseProcessor):
    """Class for drawing"""

    processing_pause: Optional[float] = 1 / 60
    reduce_pause_on_process_time: bool = True
    commands_sink_reader: DataReader = attr.ib(init=False)

    def initialize(self, data_bus: DataBus) -> None:
        """
        Инициализация
        """
        super().initialize(data_bus)
        self.field_reader = DataReader(data_bus, const.FIELD_TOPIC)
        self.image_reader = DataReader(data_bus, const.IMAGE_TOPIC)

        self.field = fld.Field(const.COLOR)

        self.images: dict[drawing.ImageTopic, drawing.Image] = {}
        for topic in drawing.ImageTopic:
            self.images.update({topic: drawing.Image(topic)})

        context = zmq.Context()
        self.draw_socket = context.socket(zmq.PUB)
        self.draw_socket.connect("ipc:///tmp/ether.draw.xsub")

        self.telemetry_socket = context.socket(zmq.PUB)
        self.telemetry_socket.connect("ipc:///tmp/ether.telemetry.xsub")

    def process(self) -> None:
        message_img = self.image_reader.read_new()
        message_fld = self.field_reader.read_last()
        if len(message_img) == 0 and message_fld is None:
            return

        for ext_image in message_img:
            image: drawing.Image = ext_image.content
            self.images[image.topic] = image

        if message_fld is not None:
            new_field: fld.LiteField = message_fld.content
            self.field.update_field(new_field)
            image = self.field.field_image
            self.images[image.topic] = image

        all_data: dict[str, dict[str, Any]] = {}
        telemetries: dict[str, str] = {}

        for topic, image in self.images.items():
            if topic == drawing.ImageTopic.FIELD:
                continue
            all_data.update(
                {
                    str(topic.name): {
                        "data": image.data,
                        "is_visible": topic in [drawing.ImageTopic.ROUTER, drawing.ImageTopic.STRATEGY],
                    }
                }
            )
            for name, message in image.telemetry:
                telemetries.update({name: message})
        self.draw_socket.send_json(all_data)

        boarder_pos = 16
        boarder_text = " | "

        all_timers = " " * (boarder_pos - len("DELAY"))
        all_timers += "DELAY |   TPS\n"
        for image_topic in [
            drawing.ImageTopic.FIELD,
            drawing.ImageTopic.STRATEGY,
            drawing.ImageTopic.ROUTER,
        ]:
            image = self.images[image_topic]
            # if image.timer.delay_warning:
            #     delay_color = (255, 0, 0)
            # else:
            #     delay_color = (255, 255, 255)
            topic_name = image_topic.name
            delay_text = f"{image.timer.delay * 1000:.1f}"
            tps_text = f"{image.timer.tps:5.1f}"

            all_timers += " " * 2 + topic_name + " " * (boarder_pos - len(topic_name + delay_text) - 2)

            all_timers += delay_text + boarder_text + tps_text + "\n"

        telemetries.update({"PROCESSORS TIMERS": all_timers})
        self.telemetry_socket.send_json(telemetries)
