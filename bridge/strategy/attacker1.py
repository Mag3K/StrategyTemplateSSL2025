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
        self.attack = False
        self.timer: Optional[float] = None

    def go(self, field: fld.Field, actions: list[Optional[Action]]) -> None:
        if field.ally_color == const.Color.YELLOW: #-------------YELLOW--------------------------------------------------
            None
        else:  #--------------------------------------------------BLUE--------------------------------------------------
            ATTACKER_A = aux.Point(0, 0)
            ATTACKER_A_DIST = 5000.0
            for i in range(0, 3):
                if aux.dist(field.y_team[i].get_pos(), field.ball.get_pos()) < ATTACKER_A_DIST:
                    ATTACKER_A_DIST = aux.dist(field.y_team[i].get_pos(), field.ball.get_pos())
                    ATTACKER_A = field.y_team[i].get_pos()

            Point11 = ATTACKER_A
            field.strategy_image.draw_circle(Point11, (0, 255, 0), 130)
            Point12 = field.ball.get_pos()

            Point22 = (Point12 - Point11).unity() * 200 + field.ball.get_pos()

            Point31 = field.ally_goal.down - aux.Point(0, 100 * field.polarity)
            Point32 = field.ally_goal.up - aux.Point(0, -100 * field.polarity)

            field.strategy_image.draw_circle(Point31, (0, 255, 0), 40)
            field.strategy_image.draw_circle(Point32, (0, 255, 0), 40)

            Point41 = aux.closest_point_on_line(Point11, Point31, Point22, "R")
            Point42 = aux.closest_point_on_line(Point11, Point32, Point22, "R")

            Point51 = field.ball.get_pos()

            if aux.nearest_point_in_poly(Point51, field.ally_goal.hull) == Point51:
                self.attack = True
            if aux.nearest_point_in_poly(Point51, field.enemy_goal.hull) == Point51:
                self.attack = False   

            if ATTACKER_A_DIST < 300:
                self.attack = False  

            if self.attack == False:
                field.strategy_image.draw_circle(field.b_team[1].get_pos(), (255, 255, 255), 150)
                if aux.dist(Point22, Point41) > aux.dist(Point22, Point42):
                    actions[1] = Actions.GoToPoint(Point42, 0)
                else:
                    actions[1] = Actions.GoToPoint(Point41, 0)
                if  ATTACKER_A == aux.Point(0, 0):
                    actions[1] = Actions.GoToPoint(field.ally_goal.center + aux.Point(1000, 0), 0)

            elif self.attack == True:
                #actions[1] = Actions.CatchBall(field.b_team[1].get_pos(), field.b_team[1].get_angle())
                '''
                field.strategy_image.draw_circle(field.b_team[1].get_pos(), (255, 0, 0), 130)
                if aux.dist(field.b_team[1].get_pos(), field.ball.get_pos()) < 150:
                    if (self.timer is None):
                        actions[1] = Actions.CatchBall(field.b_team[1].get_pos(), 0)
                        self.timer = time()
                    elif (self.timer + 1 < time()):
                        self.timer = None
                        actions[1] = Actions.Kick(field.b_team[2].get_pos(), is_pass = True)
                    else:
                        actions[1] = Actions.CatchBall(field.b_team[1].get_pos(), (field.b_team[7].get_pos() - field.b_team[1].get_pos()).arg())
                else:
                    actions[1] = Actions.CatchBall(aux.Point(1000 * field.polarity, -800 * field.polarity), (field.b_team[0].get_pos() - field.b_team[1].get_pos()).arg())
                '''
                if aux.dist(field.b_team[1].get_pos(), field.ball.get_pos()) < 400:
                        actions[1] = Actions.Kick(field.b_team[7].get_pos(), is_pass = True)
                else:
                    actions[1] = Actions.CatchBall(aux.Point(1000 * field.polarity, -800 * field.polarity), (field.b_team[0].get_pos() - field.b_team[1].get_pos()).arg())
                