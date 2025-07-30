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

        if field.ally_color == const.Color.BLUE:

            goal_keeper_id_global = const.GK
            attacker1_id_global = 1
            attacker2_id_global = 2
            
            #self.Attacker2.checker_b(field)
            #self.Attacker1.go(field, actions, attacker1_id = attacker1_id_global, attacker2_id = attacker2_id_global, goal_keeper_id = goal_keeper_id_global)
            #self.GoalKeeper.go(field, actions, attacker1_id = attacker1_id_global, attacker2_id = attacker2_id_global, goal_keeper_id = goal_keeper_id_global)
            actions[0] = Actions.GoToPointIgnore(aux.Point(0, 0), 0)
            #self.Attacker2.kick_b(field, actions)

        else:

            goal_keeper_id_global = const.ENEMY_GK
            attacker1_id_global = 1
            attacker2_id_global = 2
            
            #self.Attacker2.checker_y(field)
            #self.Attacker1.go(field, actions, attacker1_id = attacker1_id_global, attacker2_id = attacker2_id_global, goal_keeper_id = goal_keeper_id_global)
            #self.GoalKeeper.go(field, actions, attacker1_id = attacker1_id_global, attacker2_id = attacker2_id_global, goal_keeper_id = goal_keeper_id_global)
            #self.Attacker2.kick_y(field, actions)
            actions[0] = Actions.GoToPointIgnore(aux.Point(0, 0), 0)