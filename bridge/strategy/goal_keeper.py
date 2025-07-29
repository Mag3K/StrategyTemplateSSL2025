import math  # type: ignore
from time import time  # type: ignore
from typing import Optional

from bridge import const
from bridge.auxiliary import aux, fld, rbt  # type: ignore
from bridge.const import State as GameStates
from bridge.router.base_actions import Action, Actions, KickActions  # type: ignore


class GoalKeeper:
    def __init__(self) -> None:
        self.Point52 = aux.Point(0, 0)
        self.LastPoint53 = aux.Point(0, 0)


    def go(self, field: fld.Field, actions: list[Optional[Action]]) -> None:
        if field.ally_color == const.Color.YELLOW: #-------------YELLOW--------------------------------------------------
            Point51 = field.ball.get_pos()
            field.strategy_image.draw_line(Point51, self.Point52, (255, 255, 0), 10)
            
            settingsСrossbar1 = aux.Point(-(120 * field.polarity), -(-50 * field.polarity))
            settingsСrossbar2 = aux.Point(-(20 * field.polarity), -(50 * field.polarity))
            settingsСrossbarCenter = aux.Point(120 * field.polarity, 0)
            
            Point53 = aux.get_line_intersection(Point51, self.Point52, field.ally_goal.up - settingsСrossbar2, field.ally_goal.down - settingsСrossbar1, "LL")
            field.strategy_image.draw_circle(field.ally_goal.up - settingsСrossbar2, (0, 0, 0), 10)
            field.strategy_image.draw_circle(field.ally_goal.down - settingsСrossbar1, (0, 0, 0), 10)

            if field.is_ball_moves_to_goal():
                
                if Point53 is not None:

                    self.LastPoint53 = Point53

                    if Point53.y > (field.ally_goal.up).y:
                        Point53.y = field.ally_goal.up.y 
                        field.strategy_image.draw_circle(Point53, (100, 100, 100), 50)
                    if Point53.y < (field.ally_goal.down).y:
                        Point53.y = field.ally_goal.down.y 
                        field.strategy_image.draw_circle(Point53, (100, 100, 100), 50)

                    actions[0] = Actions.GoToPointIgnore(Point53, 3.14)
                    field.strategy_image.draw_circle(Point53, (255, 0, 255), 30)
                else:
                    actions[0] = Actions.GoToPointIgnore(self.LastPoint53, 3.14)
                    field.strategy_image.   draw_circle(self.LastPoint53, (0, 255, 0), 30)
            else:
                actions[0] = Actions.GoToPointIgnore(field.ally_goal.center - settingsСrossbarCenter, 3.14)
                field.strategy_image.draw_circle(field.ally_goal.center - settingsСrossbarCenter, (255, 0, 0), 30)

            self.Point52 = Point51

            if aux.nearest_point_in_poly(Point51, field.ally_goal.hull) == Point51:
                if aux.dist(field.b_team[1].get_pos(), aux.Point(1000 * field.polarity, -800 * field.polarity)) < 10:
                    actions[0] = Actions.Kick(field.b_team[1].get_pos())
                    field.strategy_image.draw_circle(Point51, (0, 0, 255), 50)

        else:  #--------------------------------------------------BLUE--------------------------------------------------
            Point51 = field.ball.get_pos()
            field.strategy_image.draw_line(Point51, self.Point52, (255, 255, 0), 10)
            
            settingsСrossbar1 = aux.Point(-(-120 * field.polarity), -(50 * field.polarity))
            settingsСrossbar2 = aux.Point(-(-120 * field.polarity), -(-50 * field.polarity))
            settingsСrossbarCenter = aux.Point(-120, 0)
            
            Point53 = aux.get_line_intersection(Point51, self.Point52, field.ally_goal.up - settingsСrossbar2, field.ally_goal.down - settingsСrossbar1, "LL")
            field.strategy_image.draw_circle(field.ally_goal.up - settingsСrossbar2, (0, 0, 0), 10)
            field.strategy_image.draw_circle(field.ally_goal.down - settingsСrossbar1, (0, 0, 0), 10)

            if field.is_ball_moves_to_goal():
                
                if Point53 is not None:

                    self.LastPoint53 = Point53

                    if Point53.y < (field.ally_goal.up).y:
                        Point53.y = field.ally_goal.up.y 
                        field.strategy_image.draw_circle(Point53, (100, 100, 100), 50)
                    if Point53.y > (field.ally_goal.down).y:
                        Point53.y = field.ally_goal.down.y 
                        field.strategy_image.draw_circle(Point53, (100, 100, 100), 50)

                    actions[0] = Actions.GoToPointIgnore(Point53, 0)
                    field.strategy_image.draw_circle(Point53, (255, 0, 255), 30)
                else:
                    actions[0] = Actions.GoToPointIgnore(self.LastPoint53, 0)
                    field.strategy_image.   draw_circle(self.LastPoint53, (0, 255, 0), 30)
            else:
                actions[0] = Actions.GoToPointIgnore(field.ally_goal.center - settingsСrossbarCenter, 0)
                field.strategy_image.draw_circle(field.ally_goal.center - settingsСrossbarCenter, (255, 0, 0), 30)

            self.Point52 = Point51

            if aux.nearest_point_in_poly(Point51, field.ally_goal.hull) == Point51:
                if aux.dist(field.b_team[1].get_pos(), aux.Point(1000 * field.polarity, -800 * field.polarity)) < 30:
                    actions[0] = Actions.Kick(field.b_team[1].get_pos(), is_pass = True)
                    field.strategy_image.draw_circle(Point51, (0, 0, 255), 50)

