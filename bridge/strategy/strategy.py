"""High-level strategy code"""

from bridge.strategy.attacker1 import Attacker1
from bridge.strategy.goal_keeper import GoalKeeper

# !v DEBUG ONLY
import math  # type: ignore
from time import time  # type: ignore
from typing import Optional

from bridge import const
from bridge.auxiliary import aux, fld, rbt  # type: ignore
from bridge.const import State as GameStates
from bridge.router.base_actions import Action, Actions, KickActions  # type: ignore


class Strategy:
    """Main class of strategy"""

    def __init__(
        self,
    ) -> None:
        self.we_active = False
        self.Attacker1 = Attacker1()
        self.GoalKeeper = GoalKeeper()

    def process(self, field: fld.Field) -> list[Optional[Action]]:
        """Game State Management"""
        if field.game_state not in [GameStates.KICKOFF, GameStates.PENALTY]:
            if field.active_team in [const.Color.ALL, field.ally_color]:
                self.we_active = True
            else:
                self.we_active = False

        actions: list[Optional[Action]] = []
        for _ in range(const.TEAM_ROBOTS_MAX_COUNT):
            actions.append(None)

        if field.ally_color == const.COLOR:
            text = str(field.game_state) + "  we_active:" + str(self.we_active)
            field.strategy_image.print(aux.Point(600, 780), text, need_to_scale=False)
        match field.game_state:
            case GameStates.RUN:
                self.run(field, actions)
            case GameStates.TIMEOUT:
                pass
            case GameStates.HALT:
                return [None] * const.TEAM_ROBOTS_MAX_COUNT
            case GameStates.PREPARE_PENALTY:
                pass
            case GameStates.PENALTY:
                pass
            case GameStates.PREPARE_KICKOFF:
                pass
            case GameStates.KICKOFF:
                pass
            case GameStates.FREE_KICK:
                pass
            case GameStates.STOP:
                # The router will automatically prevent robots from getting too close to the ball
                self.run(field, actions)

        return actions

    def run(self, field: fld.Field, actions: list[Optional[Action]]) -> None:
        """
        ONE ITERATION of strategy
        NOTE: robots will not start acting until this function returns an array of actions,
              if an action is overwritten during the process, only the last one will be executed)

        Examples of getting coordinates:
        - field.allies[8].get_pos(): aux.Point -   coordinates  of the 8th  robot from the allies
        - field.enemies[14].get_angle(): float - rotation angle of the 14th robot from the opponents

        - field.ally_goal.center: Point - center of the ally goal
        - field.enemy_goal.hull: list[Point] - polygon around the enemy goal area


        Examples of robot control:
        - actions[2] = Actions.GoToPoint(aux.Point(1000, 500), math.pi / 2)
                The robot number 2 will go to the point (1000, 500), looking in the direction π/2 (up, along the OY axis)

        - actions[3] = Actions.Kick(field.enemy_goal.center)
                The robot number 3 will hit the ball to 'field.enemy_goal.center' (to the center of the enemy goal)

        - actions[9] = Actions.BallGrab(0.0)
                The robot number 9 grabs the ball at an angle of 0.0 (it looks to the right, along the OX axis)
        """
        #actions[1] = Actions.GoToPointIgnore(aux.Point(0, 0), 0)
        #actions[1] = Actions.GoToPointIgnore(aux.Point(0, 0), (field.ball.get_pos() - field.b_team[1].get_pos()).arg())
        #actions[1] = Actions.GoToPointIgnore(aux.point_on_line(field.b_team[0].get_pos(), field.y_team[0].get_pos(), aux.dist(field.b_team[0].get_pos(), field.y_team[0].get_pos()) / 8 * 1), ((field.y_team[0].get_pos() - field.b_team[1].get_pos()).arg()))
        #actions[1] = Actions.GoToPointIgnore(aux.rotate(aux.Point(500, 0), (3.14 / 4 * 1) + time() / 3) + field.ball.get_pos(), (field.ball.get_pos() - field.b_team[1].get_pos()).arg())
        #field.strategy_image.draw_circle(aux.Point(0, 0), (255, 0, 0), 300)

        '''
        if self.stade == 0:
            if aux.dist(aux.nearest_point_in_poly(field.b_team[1].get_pos(), field.ally_goal.hull), field.b_team[1].get_pos()) < aux.dist(aux.nearest_point_in_poly(field.b_team[1].get_pos(), field.enemy_goal.hull), field.b_team[1].get_pos()):
                actions[1] = Actions.GoToPointIgnore(aux.nearest_point_in_poly(field.b_team[1].get_pos(), field.ally_goal.hull), 0)
            else:
                actions[1] = Actions.GoToPointIgnore(aux.nearest_point_in_poly(field.b_team[1].get_pos(), field.enemy_goal.hull), 0)

        if aux.dist(aux.nearest_point_in_poly(field.b_team[1].get_pos(), field.ally_goal.hull), field.b_team[1].get_pos()) < 150 or aux.dist(aux.nearest_point_in_poly(field.b_team[1].get_pos(), field.enemy_goal.hull), field.b_team[1].get_pos()) < 150:
            self.stade = 1

        if self.stade == 1:
            actions[1] = Actions.GoToPointIgnore(field.ball.get_pos(), 0)

        if aux.dist(field.ball.get_pos(), field.b_team[1].get_pos()) < 150:
            self.stade = 0
        '''

        '''
        self.Point11 = field.y_team[0].get_pos()
        self.Point12 = aux.rotate(aux.Point(self.dist, 0), (field.y_team[0].get_angle())) + field.y_team[0].get_pos()

        self.Point21 = field.b_team[0].get_pos()
        self.Point22 = aux.rotate(aux.Point(self.dist, 0), (field.b_team[0].get_angle())) + field.b_team[0].get_pos()

        self.Point41 = field.y_team[4].get_pos()
        self.Point42 = aux.rotate(aux.Point(self.dist, 0), (field.y_team[4].get_angle())) + field.y_team[4].get_pos()

        field.strategy_image.draw_line(self.Point11, self.Point12, (255, 0, 0), 15)
        field.strategy_image.draw_line(self.Point21, self.Point22, (0, 255, 0), 15)
        field.strategy_image.draw_line(self.Point41, self.Point42, (255, 255, 0), 15)

        self.Point31 = aux.get_line_intersection(self.Point11, self.Point12, self.Point21, self.Point22, "LL")
        self.Point32 = aux.get_line_intersection(self.Point11, self.Point12, self.Point41, self.Point42, "LL")
        self.Point33 = aux.get_line_intersection(self.Point41, self.Point42, self.Point21, self.Point22, "LL")

        if self.Point31 is not None:
            field.strategy_image.draw_circle(self.Point31, (0, 0, 0), 20)
        if self.Point32 is not None:
            field.strategy_image.draw_circle(self.Point32, (0, 0, 0), 20)
        if self.Point33 is not None:
            field.strategy_image.draw_circle(self.Point33, (0, 0, 0), 20)

        if self.Point31 is not None and self.Point32 is not None and self.Point33 is not None:
            self.Point5 = (self.Point31 + self.Point32 + self.Point33) / 3

            if self.Point5 is not None:
                field.strategy_image.draw_circle(self.Point5, (255, 255, 255), 20)
        '''

        '''
        self.Point11 = field.b_team[0].get_pos()
        self.Point12 = field.ball.get_pos()
        field.strategy_image.draw_line(self.Point11, self.Point12, (0, 255, 255), 15)

        #self.Point21 = aux.nearest_point_on_poly(field.b_team[1].get_pos(), (self.Point11, self.Point12))
        self.Point22 = (self.Point12 - self.Point11).unity() * 500 + field.ball.get_pos()

        self.Point31 = field.y_team[0].get_pos()
        self.Point32 = field.y_team[5].get_pos()

        field.strategy_image.draw_line(self.Point11, self.Point31, (255, 0, 255), 15)
        field.strategy_image.draw_line(self.Point11, self.Point32, (255, 0, 255), 15)

        self.Point41 = aux.closest_point_on_line(self.Point11, self.Point31, self.Point22, "L")

        field.strategy_image.draw_line(self.Point22, self.Point41, (255, 255, 0), 15)
        field.strategy_image.draw_circle(self.Point41, (0, 0, 0), 30)

        self.Point42 = aux.closest_point_on_line(self.Point11, self.Point32, self.Point22, "L")

        field.strategy_image.draw_line(self.Point22, self.Point42, (255, 255, 0), 15)
        field.strategy_image.draw_circle(self.Point42, (0, 0, 0), 30)

        if aux.dist(self.Point22, self.Point41) > aux.dist(self.Point22, self.Point42):
            actions[1] = Actions.GoToPointIgnore(self.Point42, 0)
        else:
            actions[1] = Actions.GoToPointIgnore(self.Point41, 0)
        '''

        if field.ally_color == const.Color.BLUE:

            self.Attacker1.go(field, actions)
            self.GoalKeeper.go(field, actions)

        else:
            None
            #self.GoalKeeper.go(field, actions)


'''
def choose_on_goal(field: fld.Field, actions: list[Action]) -> None:
    field.strategy_image.draw_circle(field.enemy_goal.down - aux.Point(0, -50), (0, 0, 0), 10)
    field.strategy_image.draw_circle(field.enemy_goal.up - aux.Point(0, 50), (0, 0, 0), 10)

    if aux.dist(field.y_team[1].get_pos(), field.enemy_goal.down) > aux.dist(field.y_team[1].get_pos(), field.enemy_goal.up): 
        actions[1] = Actions.Kick(field.enemy_goal.down - aux.Point(0, -50))
    else:
        actions[1] = Actions.Kick(field.enemy_goal.up - aux.Point(0, 50)
'''