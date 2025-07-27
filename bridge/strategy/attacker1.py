import math  # type: ignore
from time import time  # type: ignore
from typing import Optional

from bridge import const
from bridge.auxiliary import aux, fld, rbt  # type: ignore
from bridge.const import State as GameStates
from bridge.router.base_actions import Action, Actions, KickActions  # type: ignore

class Attacker1:
    def __init__(self) -> None:
        self.Point52 = aux.Point(0, 0)

    def go(self, field: fld.Field, actions: list[Optional[Action]]) -> None:
        Point11 = field.y_team[1].get_pos()
        Point12 = field.ball.get_pos()

        Point22 = (Point12 - Point11).unity() * 500 + field.ball.get_pos()

        Point31 = field.ally_goal.down - aux.Point(0, -100)
        Point32 = field.ally_goal.up - aux.Point(0, 100)

        Point41 = aux.closest_point_on_line(Point11, Point31, Point22, "L")
        Point42 = aux.closest_point_on_line(Point11, Point32, Point22, "L")

        if aux.dist(Point22, Point41) > aux.dist(Point22, Point42):
            actions[1] = Actions.GoToPoint(Point42, 3.14)
        else:
            actions[1] = Actions.GoToPoint(Point41, 3.14) 
            