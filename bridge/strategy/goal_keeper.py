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


    def go(self, field: fld.Field, actions: list[Optional[Action]]) -> None:
        Point51 = field.ball.get_pos()
        Point53 = aux.get_line_intersection(Point51, self.Point52, field.ally_goal.up - aux.Point(150, -100), field.ally_goal.up - aux.Point(150, 100), "LL")

        if field.is_ball_moves_to_goal():
            self.Point52 = Point51
            
            if Point53 is not None:

                '''
                if Point53.x > (field.ally_goal.up).x:
                    Point53.x = field.ally_goal.up.x 
                if Point53.x < (field.ally_goal.down).x:
                    Point53.x = field.ally_goal.down.x 
                '''

                actions[0] = Actions.GoToPointIgnore(Point53, 0)
            else:
                actions[0] = Actions.GoToPointIgnore(field.ally_goal.center + field.ally_goal.eye_forw * 500, 0)
        else:
            if Point53 is not None:
                actions[0] = Actions.GoToPointIgnore(Point53, 0)
                self.Point52 = field.ball.get_pos()
            else:
                actions[0] = Actions.GoToPointIgnore(field.ally_goal.center, 0)
                self.Point52 = field.ball.get_pos()
            

