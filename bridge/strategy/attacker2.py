import math  # type: ignore
from time import time  # type: ignore
from typing import Optional

from bridge import const
from bridge.auxiliary import aux, fld, rbt  # type: ignore
from bridge.const import State as GameStates
from bridge.router.base_actions import Action, Actions, KickActions  # type: ignore


class Attacker2:
    def __init__(self) -> None:
        self.GK = aux.Point(0,0)
        self.attacker2 = 3
        self.attacker1 = 5

    def kick_b(self, field: fld.Field, actions: list[Optional[Action]]) -> None:
            if aux.nearest_point_in_poly(field.ball.get_pos(), [aux.Point(0, -800), aux.Point(0, 800), aux.Point(2250 * field.polarity, 800), aux.Point(2250 * field.polarity, -800)]) == field.ball.get_pos():
                actions[self.attacker2] = Actions.GoToPoint(aux.Point(-1100*field.polarity,-800*field.polarity), (field.b_team[self.attacker1].get_pos() - field.b_team[self.attacker2].get_pos()).arg())
            else:
                if aux.dist(self.GK, field.enemy_goal.down) > aux.dist(self.GK, field.enemy_goal.up): 
                    actions[self.attacker2] = Actions.Kick(field.enemy_goal.up - aux.Point(0, -100*field.polarity))
                else:
                    actions[self.attacker2] = Actions.Kick(field.enemy_goal.down - aux.Point(0, 100*field.polarity))                

    def checker_b(self, field:fld.Field) -> None:
        for i in range(0, 10):
            if aux.nearest_point_in_poly(field.y_team[i].get_pos(), field.enemy_goal.hull) == field.y_team[i].get_pos():
                self.GK = field.y_team[i].get_pos()
                field.strategy_image.send_telemetry("enemy_gk", str(i))

    def checker_y(self, field:fld.Field) -> None:
        for i in range(0, 10):
            if aux.nearest_point_in_poly(field.b_team[i].get_pos(), field.enemy_goal.hull) == field.b_team[i].get_pos():
                self.GK = field.b_team[i].get_pos()
                field.strategy_image.send_telemetry("enemy_gk", str(i))

    def kick_y(self, field: fld.Field, actions: list[Optional[Action]]) -> None:
        if aux.nearest_point_in_poly(field.ball.get_pos(), [aux.Point(0, -800), aux.Point(0, 800), aux.Point(2250 * field.polarity, 800), aux.Point(2250 * field.polarity, -800)]) == field.ball.get_pos():
                actions[self.attacker2] = Actions.GoToPoint(aux.Point(-1100*field.polarity,-800*field.polarity), (field.ball.get_pos() - field.y_team[self.attacker2].get_pos()).arg())
        else:
            if aux.dist(self.GK, field.enemy_goal.down) > aux.dist(self.GK, field.enemy_goal.up): 
                actions[self.attacker2] = Actions.Kick(field.enemy_goal.down - aux.Point(0, 150*field.polarity))
            else:
                actions[self.attacker2] = Actions.Kick(field.enemy_goal.up - aux.Point(0, -150*field.polarity))