"""High-level strategy code"""

from bridge.strategy.attacker1 import Attacker1
from bridge.strategy.goal_keeper import GoalKeeper
from bridge.strategy.attacker2 import Attacker2

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
        self.Attacker2 = Attacker2()
        self.attacker1_id_global = 1
        self.attacker2_id_global = 2

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
            #print(GameStates)
        match field.game_state:
            case GameStates.RUN:
                self.run(field, actions)
            case GameStates.TIMEOUT:
                pass
            case GameStates.HALT:
                return [None] * const.TEAM_ROBOTS_MAX_COUNT
            case GameStates.PREPARE_PENALTY:
                if self.we_active == True:
                    if field.ally_color == const.Color.BLUE:
                        actions[const.GK] = Actions.GoToPointIgnore(field.ally_goal.center, 0)
                        actions[self.attacker1_id_global] = Actions.GoToPoint(aux.Point(500*field.polarity, 0), 0)
                        actions[self.attacker2_id_global] = Actions.GoToPoint(aux.Point(150*field.polarity, 0), 0)
                    else:
                        actions[const.GK] = Actions.GoToPointIgnore(field.ally_goal.center, 3.14)
                        actions[self.attacker1_id_global] = Actions.GoToPoint(aux.Point(500*field.polarity, 0), 3.14)
                        actions[self.attacker2_id_global] = Actions.GoToPoint(aux.Point(150*field.polarity, 0), 3.14)
                else:
                    if field.ally_color == const.Color.BLUE:
                        actions[const.GK] = Actions.GoToPointIgnore(field.ally_goal.center, 0)
                        actions[self.attacker1_id_global] = Actions.GoToPoint(aux.Point(-1000*field.polarity, 800), (field.b_team[const.GK].get_pos() - field.b_team[self.attacker1_id_global].get_pos()).arg())
                        actions[self.attacker2_id_global] = Actions.GoToPoint(aux.Point(-2000*field.polarity, 800), (field.b_team[const.GK].get_pos() - field.b_team[self.attacker2_id_global].get_pos()).arg())
                    else:
                        actions[const.GK] = Actions.GoToPointIgnore(field.ally_goal.center, 3.14)
                        actions[self.attacker1_id_global] = Actions.GoToPoint(aux.Point(-1000*field.polarity, 800), (field.y_team[const.GK].get_pos() - field.y_team[self.attacker1_id_global].get_pos()).arg())
                        actions[self.attacker2_id_global] = Actions.GoToPoint(aux.Point(-2000*field.polarity, 800), (field.y_team[const.GK].get_pos() - field.y_team[self.attacker2_id_global].get_pos()).arg())


            case GameStates.PENALTY:
                if self.we_active == True:
                    if field.ally_color == const.Color.BLUE:
                        actions[self.attacker2_id_global] = Actions.Kick(field.enemy_goal.up - aux.Point(0, 75))
                    else:
                        actions[self.attacker2_id_global] = Actions.Kick(field.enemy_goal.up - aux.Point(0, -75))
                else:
                    self.GoalKeeper.go(field, actions, attacker1_id = self.attacker1_id_global, attacker2_id = self.attacker2_id_global, goal_keeper_id = const.GK)
                
            case GameStates.PREPARE_KICKOFF:
                if self.we_active == False:
                    if field.ally_color == const.Color.YELLOW:
                        self.GoalKeeper.go(field, actions, attacker1_id = self.attacker1_id_global, attacker2_id = self.attacker2_id_global, goal_keeper_id = const.GK)
                        actions[self.attacker2_id_global] = Actions.GoToPoint(aux.Point((800)*field.polarity, 0), (field.ball.get_pos() - field.y_team[self.attacker1_id_global].get_pos()).arg())
                        actions[self.attacker1_id_global] = Actions.GoToPoint(aux.Point(2000*field.polarity, 0), (field.ball.get_pos() - field.y_team[self.attacker2_id_global].get_pos()).arg())
                    else:
                        self.GoalKeeper.go(field, actions, attacker1_id = self.attacker1_id_global, attacker2_id = self.attacker2_id_global, goal_keeper_id = const.GK)
                        actions[self.attacker2_id_global] = Actions.GoToPoint(aux.Point((800)*field.polarity, 0), (field.ball.get_pos() - field.b_team[self.attacker1_id_global].get_pos()).arg())
                        actions[self.attacker1_id_global] = Actions.GoToPoint(aux.Point(2000*field.polarity, 0), (field.ball.get_pos() - field.b_team[self.attacker2_id_global].get_pos()).arg())

                else:
                    if field.ally_color == const.Color.BLUE:
                        self.GoalKeeper.go(field, actions, attacker1_id = self.attacker1_id_global, attacker2_id = self.attacker2_id_global, goal_keeper_id = const.GK)
                        actions[self.attacker1_id_global] = Actions.GoToPoint(aux.Point(2000*field.polarity,0),(field.ball.get_pos() - field.b_team[self.attacker1_id_global].get_pos()).arg())
                        actions[self.attacker2_id_global] = Actions.GoToPointIgnore(aux.Point(120*field.polarity, 0), (field.ball.get_pos() - field.b_team[self.attacker2_id_global].get_pos()).arg())
                    else:
                        self.GoalKeeper.go(field, actions, attacker1_id = self.attacker1_id_global, attacker2_id = self.attacker2_id_global, goal_keeper_id = const.GK)
                        actions[self.attacker1_id_global] = Actions.GoToPoint(aux.Point(2000*field.polarity,0),(field.ball.get_pos() - field.y_team[self.attacker1_id_global].get_pos()).arg())
                        actions[self.attacker2_id_global] = Actions.GoToPointIgnore(aux.Point(120*field.polarity, 0), (field.ball.get_pos() - field.y_team[self.attacker2_id_global].get_pos()).arg())
            case GameStates.KICKOFF:
                if self.we_active == False:
                    self.GoalKeeper.go(field, actions, attacker1_id = self.attacker1_id_global, attacker2_id = self.attacker2_id_global, goal_keeper_id = const.GK)
                    actions[self.attacker2_id_global] = Actions.GoToPoint(aux.Point((-400)*field.polarity, 0), 0)
                    actions[self.attacker1_id_global] = Actions.GoToPoint(aux.Point(-1000*field.polarity, 0), 0)
                else:
                    self.GoalKeeper.go(field, actions, attacker1_id = self.attacker1_id_global, attacker2_id = self.attacker2_id_global, goal_keeper_id = const.GK)
                    actions[self.attacker1_id_global] = Actions.GoToPoint(aux.Point(-1000*field.polarity,0),0)
                    actions[self.attacker2_id_global] = Actions.Kick(field.enemy_goal.down + aux.Point(0, 75))
            case GameStates.FREE_KICK:
                if self.we_active == True:
                    if aux.nearest_point_in_poly(field.ball.get_pos(),[aux.Point(0, -800), aux.Point(0, 800), aux.Point(2250 * field.polarity, 800), aux.Point(2250 * field.polarity, -800)]) == field.ball.get_pos():
                        if field.ally_color == const.Color.BLUE:
                            self.GoalKeeper.go(field, actions, attacker1_id = self.attacker1_id_global, attacker2_id = self.attacker2_id_global, goal_keeper_id = const.GK)
                            actions[self.attacker2_id_global] = Actions.GoToPoint(aux.Point(-1100*field.polarity,-800*field.polarity), (field.b_team[self.attacker1_id_global].get_pos() - field.b_team[self.attacker2_id_global].get_pos()).arg())
                            actions[self.attacker1_id_global] = Actions.Kick(field.b_team[self.attacker2_id_global].get_pos(), is_pass=True)
                        else:
                            self.GoalKeeper.go(field, actions, attacker1_id = self.attacker1_id_global, attacker2_id = self.attacker2_id_global, goal_keeper_id = const.GK)
                            actions[self.attacker2_id_global] = Actions.GoToPoint(aux.Point(-1100*field.polarity,-800*field.polarity), (field.y_team[self.attacker1_id_global].get_pos() - field.y_team[self.attacker2_id_global].get_pos()).arg())
                            actions[self.attacker1_id_global] = Actions.Kick(field.y_team[self.attacker2_id_global].get_pos(), is_pass=True)
                    else:
                        if field.ally_color == const.Color.BLUE:
                            self.GoalKeeper.go(field, actions, attacker1_id = self.attacker1_id_global, attacker2_id = self.attacker2_id_global, goal_keeper_id = const.GK)
                            actions[self.attacker2_id_global] = Actions.GoToPoint(aux.Point(-1100*field.polarity,-800*field.polarity), (field.b_team[self.attacker1_id_global].get_pos() - field.b_team[self.attacker2_id_global].get_pos()).arg())
                            for i in range(0, 10):
                                if aux.nearest_point_in_poly(field.y_team[i].get_pos(), field.enemy_goal.hull) == field.y_team[i].get_pos():
                                    self.GK = field.y_team[i].get_pos()
                                    field.strategy_image.draw_circle(self.GK, (0, 0, 0), 150)
                            field.strategy_image.draw_circle(field.b_team[1].get_pos(), (127, 0, 0), 150)
                            if aux.dist(self.GK, field.enemy_goal.down) > aux.dist(self.GK, field.enemy_goal.up): 
                                actions[self.attacker1_id_global] = Actions.Kick(field.enemy_goal.down - aux.Point(0, 150 * field.polarity))
                            else:
                                actions[self.attacker1_id_global] = Actions.Kick(field.enemy_goal.up - aux.Point(0, -150 * field.polarity))
                        else:
                            self.GoalKeeper.go(field, actions, attacker1_id = self.attacker1_id_global, attacker2_id = self.attacker2_id_global, goal_keeper_id = const.GK)
                            actions[self.attacker2_id_global] = Actions.GoToPoint(aux.Point(-1100*field.polarity,-800*field.polarity), (field.y_team[self.attacker1_id_global].get_pos() - field.y_team[self.attacker2_id_global].get_pos()).arg())
                            for i in range(0, 10):
                                if aux.nearest_point_in_poly(field.b_team[i].get_pos(), field.enemy_goal.hull) == field.b_team[i].get_pos():
                                    self.GK = field.b_team[i].get_pos()
                                    field.strategy_image.draw_circle(self.GK, (0, 0, 0), 150)
                            field.strategy_image.draw_circle(field.y_team[1].get_pos(), (127, 0, 0), 150)
                            if aux.dist(self.GK, field.enemy_goal.down) > aux.dist(self.GK, field.enemy_goal.up): 
                                actions[self.attacker1_id_global] = Actions.Kick(field.enemy_goal.down - aux.Point(0, 150*  field.polarity))
                            else:
                                actions[self.attacker1_id_global] = Actions.Kick(field.enemy_goal.up - aux.Point(0, -150 * field.polarity))
                else:
                    if field.ally_color == const.Color.BLUE:
                        self.GoalKeeper.go(field, actions, attacker1_id = self.attacker1_id_global, attacker2_id = self.attacker2_id_global, goal_keeper_id = const.GK)
                        actions[self.attacker1_id_global] = Actions.GoToPoint(aux.Point(-1000,0), (field.ball.get_pos()-field.b_team[self.attacker1_id_global].get_pos()).arg())
                        actions[self.attacker2_id_global] = Actions.GoToPoint(aux.Point(-500,0), (field.ball.get_pos()-field.b_team[self.attacker2_id_global].get_pos()).arg())
                    else:
                        self.GoalKeeper.go(field, actions, attacker1_id = self.attacker1_id_global, attacker2_id = self.attacker2_id_global, goal_keeper_id = const.GK)
                        actions[self.attacker1_id_global] = Actions.GoToPoint(aux.Point(-1000,0), (field.ball.get_pos()-field.y_team[self.attacker1_id_global].get_pos()).arg())
                        actions[self.attacker2_id_global] = Actions.GoToPoint(aux.Point(-500,0), (field.ball.get_pos()-field.y_team[self.attacker2_id_global].get_pos()).arg())
            case GameStates.STOP:
                # The router will automatically prevent robots from getting too close to the ball
                self.run(field, actions)
                #WW WW WW WW WW WW WW WW WW WW WW WW WW WW WW WW WW WW WW WW WW WW WW WW WW WW WW WW WW

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

        if field.ally_color == const.Color.BLUE:

            
            self.Attacker2.checker_b(field)
            self.Attacker1.go(field, actions, attacker1_id = self.attacker1_id_global, attacker2_id = self.attacker2_id_global, goal_keeper_id = const.GK)
            self.GoalKeeper.go(field, actions, attacker1_id = self.attacker1_id_global, attacker2_id = self.attacker2_id_global, goal_keeper_id = const.GK)
            self.Attacker2.kick_b(field, actions)

        else:
            self.Attacker2.checker_y(field)
            self.Attacker1.go(field, actions, attacker1_id = self.attacker1_id_global, attacker2_id = self.attacker2_id_global, goal_keeper_id = const.GK)
            self.GoalKeeper.go(field, actions, attacker1_id = self.attacker1_id_global, attacker2_id = self.attacker2_id_global, goal_keeper_id = const.GK)
            self.Attacker2.kick_y(field, actions)