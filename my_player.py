from player_abalone import PlayerAbalone
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from seahorse.utils.custom_exceptions import MethodNotImplementedError
import random

class MyPlayer(PlayerAbalone):
    """
    Player class for Abalone game.

    Attributes:
        piece_type (str): piece type of the player
    """

    def __init__(self, piece_type: str, name: str = "bob", time_limit: float=60*15,*args) -> None:
        """
        Initialize the PlayerAbalone instance.

        Args:
            piece_type (str): Type of the player's game piece
            name (str, optional): Name of the player (default is "bob")
            time_limit (float, optional): the time limit in (s)
        """
        super().__init__(piece_type,name,time_limit,*args)


    def compute_action(self, current_state: GameState, **kwargs) -> Action:
        """
        Function to implement the logic of the player.

        Args:
            current_state (GameState): Current game state representation
            **kwargs: Additional keyword arguments

        Returns:
            Action: selected feasible action
        """
        # print(current_state.is_done())
        # # print(current_state.check_action())
        # print(current_state.compute_next_player())
        # print(current_state.generate_possible_actions())
        # print(current_state.get_next_player())
        # print(current_state.get_players())


        # possible_actions = current_state.get_possible_actions()
        # random.seed("seahorse")
        # if kwargs:
        #     pass
        # return random.choice(list(possible_actions))
        
        possible_actions = current_state.get_possible_actions()
        best_action = None
        best_score = float('-inf')  # Initialize with negative infinity for maximization
        print("1111111")
        for action in possible_actions:
            # Apply the action to get the next state
            next_state = action.get_next_game_state()
            print("22222222")
            # Use minimax to find the score for this move
            score = self.minimax(next_state, depth=3, maximizing_player=False)

            # Update the best move if a higher score is found
            if score > best_score:
                best_score = score
                best_action = action

        return best_action

    def minimax(self, state: GameState, depth: int, maximizing_player: bool) -> int:
        if depth == 0 or state.is_done():
            # Base case: evaluate the state
            return self.evaluate_state(state)

        if maximizing_player:
            # Maximize the score for the maximizing player
            print("333333333")
            max_score = float('-inf')
            for action in state.get_possible_actions():
                next_state = action.get_next_game_state()
                score = self.minimax(next_state, depth - 1, False)
                max_score = max(max_score, score)
            return max_score
        else:
            # Minimize the score for the minimizing player
            print("44444444")
            min_score = float('inf')
            for action in state.get_possible_actions():
                next_state = action.get_next_game_state()
                score = self.minimax(next_state, depth - 1, True)
                min_score = min(min_score, score)
            return min_score

    def evaluate_state(self, state: GameState) -> int:
        # heuristic function
        # This function should return a numerical score indicating the desirability of the state
        # Positive values indicate an advantage for the maximizing player, and negative values for the minimizing player
        return random.randint(1,100)