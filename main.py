"""
Точка входа в стратегию
"""

from strategy_bridge.runner import Runner

from bridge import const
from bridge.processors.drawing_processor import Drawer
from bridge.processors.field_creator import FieldCreator
from bridge.processors.python_controller import SSLController
from bridge.processors.router_processor import CommandSink

if __name__ == "__main__":
    # config.init_logging("./logs")

    PROCESSORS = [
        FieldCreator(
            debug_mode=True,  # True => ignore commands from referee
            debug_game_state=const.State.RUN,  # for other states (except STOP and HALT) add "debug_active_team" param
            # debug_active_team=const.Color.ALL,
        ),
        SSLController(
            ally_color=const.COLOR,
        ),
        SSLController(
            ally_color=const.COLOR.reverse(),
        ),
        Drawer(),
        CommandSink(),
    ]

    RUNNER = Runner(processors=PROCESSORS)
    RUNNER.run()
