from player_abalone import PlayerAbalone
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from seahorse.utils.custom_exceptions import MethodNotImplementedError

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
        # [print(*x) for x in current_state.get_rep().get_grid()] 
        # [print(a,b.__dict__) for a,b in current_state.get_rep().env.items()]
        # print(current_state.get_rep())
        # print(current_state.get_rep().get_grid())
        # print(current_state.get_rep().env.items())

        """
        Function to implement the logic of the player.

        Args:
            current_state (GameState): Current game state representation
            **kwargs: Additional keyword arguments

        Returns:
            Action: selected feasible action
        """
        # Prendre les actions possibles de l'état initial     
        possible_actions = current_state.get_possible_actions()
        # Initialiser la meilleure action à None ainsi que le meilleur score à -inf (valeur la plus basse pour le maximiseur)
        best_action = None
        best_score = float('-inf')
        # Itérer sur toutes les actions possibles pour descendre dans l'arbre d'états
        for action in possible_actions:
            # Passer au prochain état après avoir appliquer l'action
            next_state = action.get_next_game_state()
            # Utiliser l'algorithme de minimax pour récursivement traverser les états de l'arbre
            # Depth est la profondeur de la recherche avant de remonter un score
            score = self.minimax(next_state, depth=1, maximizing_player=True)

            # Si un meilleur score est trouvé, mettre à jour le meilleur score avec l'action associée
            if score > best_score:
                best_score = score
                best_action = action
        # print(best_score)
        # print(best_action)
        # Retourner la meilleure action à faire
        return best_action
    
    # Algorithme minimax
    def minimax(self, state: GameState, depth: int, maximizing_player: bool) -> int:
        # Si nous avons fini de découvrir ou il n'y a plus d'états à découvrir (fin de partie)
        if depth == 0 or state.is_done():
            # On évalue le score de l'état avec la fonction heuristique
            return self.value_state(state)
        # Si le tour est au maximiseur, on maximise le score
        if maximizing_player:
            max_score = float('-inf')
            for action in state.get_possible_actions():
                next_state = action.get_next_game_state()
                score = self.minimax(next_state, depth - 1, False)
                max_score = max(max_score, score)
            return max_score
        else:
            # Si le tour est au minimiseur, on minimise le score
            min_score = float('inf')
            for action in state.get_possible_actions():
                next_state = action.get_next_game_state()
                score = self.minimax(next_state, depth - 1, True)
                min_score = min(min_score, score)
            return min_score

    # Fonction heuristique pour l'évaluation d'un état
    def value_state(self, state: GameState) -> int:
        # Coefficient d'importance attribué à chaque critère heuristique
        piece_count_weight = 1.0
        center_control_weight = 1.5
        # mobility_weight = 0.5

        # Critère pour le compte de pièces de notre joueur vs le joueur adverse
        piece_count_player = 14 - abs(state.get_player_score(self))
        piece_count_adversary = 14 - abs(next(value for key, value in state.get_scores().items() if key != self.get_id()))
        piece_count_heuristic = piece_count_player - piece_count_adversary

        # Nombre de pièces dans le centre stratégique de notre joueur vs le joueur adverse
        coordinates_list = [(coordinates, piece.__dict__) for coordinates, piece in state.get_rep().env.items()]
        center_control_player = sum(1 for key, value_dict in coordinates_list if in_center(key) and value_dict["owner_id"] == self.get_id())
        center_control_adversary = sum(1 for key, value_dict in coordinates_list if in_center(key) and value_dict["owner_id"] != self.get_id())
        center_control_heuristic = center_control_player-center_control_adversary

        # Somme des coefficients des pièces dans terme de proximité du centre??

        # Evaluate mobility
        # mobility = sum(len(state.get_valid_moves(piece)) for piece in state.get_rep().get_pieces())

        # # Combine the components with their respective weights
        score = (
            piece_count_weight*piece_count_heuristic+
            center_control_weight * center_control_heuristic
        #     + mobility_weight * mobility
        )
        return score
    
def in_center(coordinates):
    center_row_beginning, center_row_end = 6, 10
    center_col_beginning, center_col_end = 2, 6
    row, col = coordinates
    return center_row_beginning <= row <= center_row_end and center_col_beginning <= col <= center_col_end