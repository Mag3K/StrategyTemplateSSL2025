"""
Description of the base action class
"""

from bridge import const
from bridge.auxiliary import aux, fld, rbt


class ActionValues:
    """Return values of the action"""

    vel = aux.Point(0, 0)
    angle = 0.0
    kick_up = False
    kick_forward = False
    auto_kick = 0  # 0-lower, 1-upper
    kicker_voltage = 0
    dribbler_speed = 0
    beep = 0  # MOST IMPORTANT


class ActionDomain:
    """Data to perform an action"""

    def __init__(
        self,
        field: fld.Field,
        game_state: const.State,
        we_active: bool,
        robot: rbt.Robot,
    ) -> None:
        self.field = field
        self.game_state = game_state
        self.we_active = we_active
        self.robot = robot


class Action:
    """Base class of Action"""

    def is_defined(self, _: ActionDomain) -> bool:
        """Scope"""
        return True

    def behavior(self, domain: ActionDomain, current_action: ActionValues) -> None:
        """Behavior"""

    def use_behavior_of(self, domain: ActionDomain, current_action: ActionValues) -> list["Action"]:
        """Condition for performing an action"""
        return []

    def process(self, domain: ActionDomain, current_action: ActionValues) -> None:
        """Process of Action"""
        for action in self.use_behavior_of(domain, current_action):
            action.process(domain, current_action)

        if self.is_defined(domain):
            self.behavior(domain, current_action)
            limit_action(domain, current_action)


def limit_action(_: ActionDomain, current_action: ActionValues, speed: float = const.MAX_SPEED) -> None:
    """Limit robot speed"""
    if current_action.vel.mag() > speed:
        current_action.vel = current_action.vel.unity() * speed
