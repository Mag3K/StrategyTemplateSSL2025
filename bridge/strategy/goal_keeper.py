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


    def go(self, field: fld.Field, actions: list[Optional[Action]], attacker1_id: int, attacker2_id: int, goal_keeper_id: int) -> None:
        if field.ally_color == const.Color.YELLOW: #-------------YELLOW--------------------------------------------------
            Point51 = field.ball.get_pos()
            field.strategy_image.draw_line(Point51, self.Point52, (255, 255, 0), 10)
            
            settingsСrossbar1 = aux.Point(-(-120 * field.polarity), -(-50 * field.polarity))
            settingsСrossbar2 = aux.Point(-(-120 * field.polarity), -(50 * field.polarity))
            settingsСrossbarCenter = aux.Point(120 * field.polarity, 0)

            baseAngle = 3.14
            
            attacker1_pos = field.y_team[attacker1_id].get_pos()
            attacker2_pos = field.y_team[attacker2_id].get_pos()
            goal_keeper_pos = field.y_team[goal_keeper_id].get_pos()

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

                    actions[goal_keeper_id] = Actions.CatchBall(Point53, baseAngle)
                    field.strategy_image.draw_circle(Point53, (255, 0, 255), 30)
                else:
                    actions[goal_keeper_id] = Actions.CatchBall(self.LastPoint53, baseAngle)
                    field.strategy_image.   draw_circle(self.LastPoint53, (0, 255, 0), 30)
            else:
                actions[goal_keeper_id] = Actions.GoToPointIgnore(field.ally_goal.center - settingsСrossbarCenter, baseAngle)
                field.strategy_image.draw_circle(field.ally_goal.center - settingsСrossbarCenter, (255, 0, 0), 30)

            self.Point52 = Point51

            if aux.nearest_point_in_poly(Point51, field.ally_goal.hull) == Point51:
                if aux.dist(attacker1_pos, aux.Point(1000 * field.polarity, -800 * field.polarity)) < 30:
                    actions[goal_keeper_id] = Actions.Kick(attacker1_pos, is_pass = True)
                    field.strategy_image.draw_circle(Point51, (0, 0, 255), 50)

        else:  #--------------------------------------------------BLUE--------------------------------------------------
            Point51 = field.ball.get_pos()
            field.strategy_image.draw_line(Point51, self.Point52, (255, 255, 0), 10)
            
            settingsСrossbar1 = aux.Point(-(-120 * field.polarity), -(50 * field.polarity))
            settingsСrossbar2 = aux.Point(-(-120 * field.polarity), -(-50 * field.polarity))
            settingsСrossbarCenter = aux.Point(-120, 0)

            baseAngle = 0

            attacker1_pos = field.b_team[attacker1_id].get_pos()
            attacker2_pos = field.b_team[attacker2_id].get_pos()
            goal_keeper_pos = field.b_team[goal_keeper_id].get_pos()
            
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

                    actions[goal_keeper_id] = Actions.CatchBall(Point53, baseAngle)
                    field.strategy_image.draw_circle(Point53, (255, 0, 255), 30)
                else:
                    actions[goal_keeper_id] = Actions.CatchBall(self.LastPoint53, baseAngle)
                    field.strategy_image.   draw_circle(self.LastPoint53, (0, 255, 0), 30)
            else:
                actions[goal_keeper_id] = Actions.GoToPointIgnore(field.ally_goal.center - settingsСrossbarCenter, baseAngle)
                field.strategy_image.draw_circle(field.ally_goal.center - settingsСrossbarCenter, (255, 0, 0), 30)

            self.Point52 = Point51

            if aux.nearest_point_in_poly(Point51, field.ally_goal.hull) == Point51:
                if aux.dist(attacker1_pos, aux.Point(1000 * field.polarity, -800 * field.polarity)) < 30:
                    actions[goal_keeper_id] = Actions.Kick(attacker1_pos, is_pass = True)
                    field.strategy_image.draw_circle(Point51, (0, 0, 255), 50)

