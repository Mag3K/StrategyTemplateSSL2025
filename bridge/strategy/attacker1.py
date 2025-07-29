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
        self.GK = aux.Point(0, 0)
        self.attack = 0
        self.timer: Optional[float] = None

    def go(self, field: fld.Field, actions: list[Optional[Action]], attacker1_id: int, attacker2_id: int, goal_keeper_id: int) -> None:
        if field.ally_color == const.Color.YELLOW: #-------------YELLOW--------------------------------------------------
            ATTACKER_A = aux.Point(0, 0)
            ATTACKER_A_DIST = 5000.0
            for i in range(0, 10):
                if aux.dist(field.b_team[i].get_pos(), field.ball.get_pos()) < ATTACKER_A_DIST:
                    ATTACKER_A_DIST = aux.dist(field.b_team[i].get_pos(), field.ball.get_pos())
                    ATTACKER_A = field.b_team[i].get_pos()

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
                self.attack = 1
            if aux.nearest_point_in_poly(Point51, field.enemy_goal.hull) == Point51:
                self.attack = 0   
            if ATTACKER_A_DIST < 300:
                self.attack = 0  
            #if ATTACKER_A_DIST < aux.dist(field.b_team[attacker1_id].get_pos(), field.ball.get_pos()) and aux.dist(field.b_team[attacker2_id].get_pos(), field.ball.get_pos()) > 500 and aux.dist(field.b_team[attacker1_id].get_pos(), field.ball.get_pos()) > 300 and aux.dist(field.b_team[goal_keeper_id].get_pos(), field.ball.get_pos()) > 1000:
            #    self.attack = 2  
            if aux.dist(field.y_team[attacker1_id].get_pos(), field.ball.get_pos()) < 300 and ((field.y_team[attacker1_id].get_pos()).x > 1 * field.polarity):
                self.attack = 3  

            if self.attack == 0:
                field.strategy_image.draw_circle(field.y_team[1].get_pos(), (255, 255, 255), 150)
                if aux.dist(Point22, Point41) > aux.dist(Point22, Point42):
                    actions[attacker1_id] = Actions.GoToPoint(Point42, 3.14)
                else:
                    actions[attacker1_id] = Actions.GoToPoint(Point41, 3.14)
                if  ATTACKER_A == aux.Point(0, 0):
                    actions[attacker1_id] = Actions.GoToPoint(field.ally_goal.center + aux.Point(1000, 0), 3.14)

            elif self.attack == 1:
                #actions[1] = Actions.CatchBall(field.b_team[attacker1_id].get_pos(), field.b_team[attacker1_id].get_angle())
                
                field.strategy_image.draw_circle(field.y_team[attacker1_id].get_pos(), (255, 0, 0), 130)
                if aux.dist(field.y_team[attacker1_id].get_pos(), field.ball.get_pos()) < 300 and aux.nearest_point_in_poly(Point51, field.ally_goal.hull) != Point51:
                    actions[attacker1_id] = Actions.Kick(field.y_team[attacker2_id].get_pos(), is_pass = True)
                    #if (self.timer is None):
                    #    actions[attacker1_id] = Actions.CatchBall(field.b_team[attacker1_id].get_pos(), 0)
                    #    self.timer = time()
                    #elif (self.timer + 1 < time()):
                    #    self.timer = None
                    #    actions[attacker1_id] = Actions.Kick(field.b_team[2].get_pos(), is_pass = True)
                    #else:
                    #    actions[attacker1_id] = Actions.CatchBall(field.b_team[attacker1_id].get_pos(), (field.b_team[attacker2_id].get_pos() - field.b_team[attacker1_id].get_pos()).arg())
                else:
                    actions[1] = Actions.CatchBall(aux.Point(1000 * field.polarity, -800 * field.polarity), (field.y_team[goal_keeper_id].get_pos() - field.y_team[attacker1_id].get_pos()).arg())
                '''
                field.strategy_image.draw_circle(field.b_team[1].get_pos(), (255, 0, 0), 130)
                if aux.dist(field.b_team[attacker1_id].get_pos(), field.ball.get_pos()) < 400:
                        actions[attacker1_id] = Actions.Kick(field.b_team[attacker2_id].get_pos(), is_pass = True)
                else:
                    actions[attacker1_id] = Actions.CatchBall(aux.Point(1000 * field.polarity, -800 * field.polarity), (field.b_team[goal_keeper_id].get_pos() - field.b_team[attacker1_id].get_pos()).arg())
                '''
                     
            #elif self.attack == 2:
            #    field.strategy_image.draw_circle(field.b_team[1].get_pos(), (255, 0, 255), 150)
            #    actions[attacker1_id] = Actions.Kick(field.b_team[goal_keeper_id].get_pos(), is_pass = True)
            

            elif self.attack == 3:
                for i in range(0, 10):
                    if aux.nearest_point_in_poly(field.b_team[i].get_pos(), field.enemy_goal.hull) == field.b_team[i].get_pos():
                        self.GK = field.b_team[i].get_pos()
                        field.strategy_image.draw_circle(self.GK, (0, 0, 0), 150)
                field.strategy_image.draw_circle(field.y_team[1].get_pos(), (127, 0, 0), 150)
                if aux.dist(self.GK, field.enemy_goal.down) > aux.dist(self.GK, field.enemy_goal.up): 
                    actions[attacker1_id] = Actions.Kick(field.enemy_goal.down - aux.Point(0, 100*field.polarity))
                else:
                    actions[attacker1_id] = Actions.Kick(field.enemy_goal.up - aux.Point(0, -100*field.polarity))






        else:  #--------------------------------------------------BLUE--------------------------------------------------
            ATTACKER_A = aux.Point(0, 0)
            ATTACKER_A_DIST = 5000.0
            for i in range(0, 10):
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
                self.attack = 1
            if aux.nearest_point_in_poly(Point51, field.enemy_goal.hull) == Point51:
                self.attack = 0   
            if ATTACKER_A_DIST < 300:
                self.attack = 0  
            #if ATTACKER_A_DIST < aux.dist(field.b_team[attacker1_id].get_pos(), field.ball.get_pos()) and aux.dist(field.b_team[attacker2_id].get_pos(), field.ball.get_pos()) > 500 and aux.dist(field.b_team[attacker1_id].get_pos(), field.ball.get_pos()) > 300 and aux.dist(field.b_team[goal_keeper_id].get_pos(), field.ball.get_pos()) > 1000:
            #    self.attack = 2  
            if aux.dist(field.b_team[attacker1_id].get_pos(), field.ball.get_pos()) < 300 and ((field.b_team[attacker1_id].get_pos()).x > 1 * field.polarity):
                self.attack = 3  

            if self.attack == 0:
                field.strategy_image.draw_circle(field.b_team[1].get_pos(), (255, 255, 255), 150)
                if aux.dist(Point22, Point41) > aux.dist(Point22, Point42):
                    actions[attacker1_id] = Actions.GoToPoint(Point42, 0)
                else:
                    actions[attacker1_id] = Actions.GoToPoint(Point41, 0)
                if  ATTACKER_A == aux.Point(0, 0):
                    actions[attacker1_id] = Actions.GoToPoint(field.ally_goal.center + aux.Point(1000, 0), 0)

            elif self.attack == 1:
                #actions[1] = Actions.CatchBall(field.b_team[attacker1_id].get_pos(), field.b_team[attacker1_id].get_angle())
                
                field.strategy_image.draw_circle(field.b_team[attacker1_id].get_pos(), (255, 0, 0), 130)
                if aux.dist(field.b_team[attacker1_id].get_pos(), field.ball.get_pos()) < 300 and aux.nearest_point_in_poly(Point51, field.ally_goal.hull) != Point51:
                    actions[attacker1_id] = Actions.Kick(field.b_team[attacker2_id].get_pos(), is_pass = True)
                    #if (self.timer is None):
                    #    actions[attacker1_id] = Actions.CatchBall(field.b_team[attacker1_id].get_pos(), 0)
                    #    self.timer = time()
                    #elif (self.timer + 1 < time()):
                    #    self.timer = None
                    #    actions[attacker1_id] = Actions.Kick(field.b_team[2].get_pos(), is_pass = True)
                    #else:
                    #    actions[attacker1_id] = Actions.CatchBall(field.b_team[attacker1_id].get_pos(), (field.b_team[attacker2_id].get_pos() - field.b_team[attacker1_id].get_pos()).arg())
                else:
                    actions[1] = Actions.CatchBall(aux.Point(1000 * field.polarity, -800 * field.polarity), (field.b_team[0].get_pos() - field.b_team[1].get_pos()).arg())
                '''
                field.strategy_image.draw_circle(field.b_team[1].get_pos(), (255, 0, 0), 130)
                if aux.dist(field.b_team[attacker1_id].get_pos(), field.ball.get_pos()) < 400:
                        actions[attacker1_id] = Actions.Kick(field.b_team[attacker2_id].get_pos(), is_pass = True)
                else:
                    actions[attacker1_id] = Actions.CatchBall(aux.Point(1000 * field.polarity, -800 * field.polarity), (field.b_team[goal_keeper_id].get_pos() - field.b_team[attacker1_id].get_pos()).arg())
                '''
                     
            #elif self.attack == 2:
            #    field.strategy_image.draw_circle(field.b_team[1].get_pos(), (255, 0, 255), 150)
            #    actions[attacker1_id] = Actions.Kick(field.b_team[goal_keeper_id].get_pos(), is_pass = True)
            

            elif self.attack == 3:
                for i in range(0, 10):
                    if aux.nearest_point_in_poly(field.y_team[i].get_pos(), field.enemy_goal.hull) == field.y_team[i].get_pos():
                        self.GK = field.y_team[i].get_pos()
                        field.strategy_image.draw_circle(self.GK, (0, 0, 0), 150)
                field.strategy_image.draw_circle(field.b_team[1].get_pos(), (127, 0, 0), 150)
                if aux.dist(self.GK, field.enemy_goal.down) > aux.dist(self.GK, field.enemy_goal.up): 
                    actions[attacker1_id] = Actions.Kick(field.enemy_goal.down - aux.Point(0, 100*field.polarity))
                else:
                    actions[attacker1_id] = Actions.Kick(field.enemy_goal.up - aux.Point(0, -100*field.polarity))