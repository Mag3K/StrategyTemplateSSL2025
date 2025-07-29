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

    def go_b(self, field:fld.Field, actions: list[Optional[Action]]) -> None:
        actions[7] = Actions.GoToPoint(aux.Point(-500 ,-800), (field.b_team[1].get_pos() - field.b_team[7].get_pos()).arg())

    def kick_b(self, field: fld.Field, actions: list[Optional[Action]]) -> None:
        if aux.dist(field.b_team[7].get_pos(), field.ball.get_pos()) < 400:
            if aux.dist(self.GK, field.ally_goal.down) > aux.dist(self.GK, field.ally_goal.up): 
                actions[7] = Actions.Kick(field.ally_goal.down - aux.Point(0, 100))
            else:
                actions[7] = Actions.Kick(field.ally_goal.up - aux.Point(0, -100))
        else:
            field.strategy_image.send_telemetry("krhwsdhjgvbs", "ukdfsjgcbku")

    def checker_b(self, field:fld.Field) -> None:
        for i in range(0, 3):
            if aux.nearest_point_in_poly(field.b_team[i].get_pos(), field.ally_goal.hull) == field.b_team[i].get_pos():
                self.GK = field.b_team[i].get_pos()
                field.strategy_image.send_telemetry("enemy_gk", str(i))

    def checker_y(self, field:fld.Field) -> None:
        for i in range(0, 3):
            if aux.nearest_point_in_poly(field.b_team[i].get_pos(), field.enemy_goal.hull) == field.b_team[i].get_pos():
                self.GK = field.b_team[i].get_pos()
                field.strategy_image.send_telemetry("enemy_gk", str(i))

    def go_y(self, field:fld.Field, actions: list[Optional[Action]]) -> None:
        actions[7] = Actions.GoToPoint(aux.Point(-500*field.polarity,-800), (field.y_team[1].get_pos() - field.y_team[2].get_pos()).arg())

    def kick_y(self, field: fld.Field, actions: list[Optional[Action]]) -> None:
        if aux.dist(field.y_team[7].get_pos(), field.ball.get_pos()) < 250:
            if aux.dist(self.GK, field.enemy_goal.down) > aux.dist(self.GK, field.enemy_goal.up): 
                actions[2] = Actions.Kick(field.enemy_goal.down - aux.Point(0, 75))
            else:
                actions[2] = Actions.Kick(field.enemy_goal.up - aux.Point(0, -75))
        else:
            pass

    def pressing_y(self, field:fld.Field, actions: list[Optional[Action]]) -> None:        
        self.Point0 = field.y_team[2].get_pos()
        self.Point1 = field.ball.get_pos()

        self.Point7 = (self.Point1 - self.Point0).unity() * 300

        self.Point2 = field.ally_goal.up - aux.Point(0, 100)
        self.Point3 = field.ally_goal.down - aux.Point(0, -100)

        #field.strategy_image.draw_line(self.Point0, self.Point2, (255, 255, 0), 10)
        #field.strategy_image.draw_line(self.Point0, self.Point3, (255, 255, 0), 10)

        self.Point5 = aux.closest_point_on_line(self.Point0, self.Point2, self.Point7, "L")

        #field.strategy_image.draw_line(self.Point4, self.Point5, (255, 255, 0), 15)

        self.Point6 = aux.closest_point_on_line(self.Point0, self.Point3, self.Point7, "L")

        #field.strategy_image.draw_line(self.Point4, self.Point6, (255, 0, 255), 30)

        if aux.dist(self.Point7, self.Point5)>aux.dist(self.Point7, self.Point6):
            actions[2] = Actions.GoToPoint(self.Point6, (field.ball.get_pos()-field.b_team[2].get_pos()).arg())
        else:
            actions[2] = Actions.GoToPoint(self.Point5, (field.ball.get_pos()-field.b_team[2].get_pos()).arg())


    def pressing_b(self, field:fld.Field, actions: list[Optional[Action]]) -> None:
        self.Point0 = field.b_team[2].get_pos()
        self.Point1 = field.ball.get_pos()

        self.Point7 = (self.Point1 - self.Point0).unity() * 1000 + field.ball.get_pos()

        self.Point2 = field.ally_goal.up - aux.Point(0, 100)
        self.Point3 = field.ally_goal.down - aux.Point(0, -100)

        #field.strategy_image.draw_line(self.Point0, self.Point2, (255, 255, 0), 10)
        #field.strategy_image.draw_line(self.Point0, self.Point3, (255, 255, 0), 10)

        self.Point5 = aux.closest_point_on_line(self.Point0, self.Point2, self.Point7, "L")

        #field.strategy_image.draw_line(self.Point4, self.Point5, (255, 255, 0), 15)

        self.Point6 = aux.closest_point_on_line(self.Point0, self.Point3, self.Point7, "L")

        #field.strategy_image.draw_line(self.Point4, self.Point6, (255, 0, 255), 30)

        if aux.dist(self.Point7, self.Point5)>aux.dist(self.Point7, self.Point6):
            actions[2] = Actions.GoToPoint(self.Point6, 0)
        else:
            actions[2] = Actions.GoToPoint(self.Point5, 0)