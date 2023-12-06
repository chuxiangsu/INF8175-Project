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
        # Initialiser le alpha et le beta
        alpha = float('-inf')
        beta = float('inf')
        # Itérer sur toutes les actions possibles pour descendre dans l'arbre d'états
        for action in possible_actions:

            # Passer au prochain état après avoir appliquer l'action
            next_state = action.get_next_game_state()

            # Utiliser l'algorithme de minimax pour récursivement traverser les états de l'arbre
            # Depth est la profondeur de la recherche avant de remonter un score

            player_id = self.get_id()
            all_states_current = [(coordinates, piece.__dict__) for coordinates, piece in
                                  next_state.get_rep().env.items()]
            my_states_current = len({coordinate for coordinate, piece in all_states_current if
                                 piece['owner_id'] == player_id})

            score = self.minimax(my_states_current, next_state, depth=2, alpha = alpha, beta = beta, maximizing_player=True)

            # Si un meilleur score est trouvé, mettre à jour le meilleur score avec l'action associée
            if score > best_score:
                best_score = score
                best_action = action
        # Retourner la meilleure action à faire
        return best_action



    # Algorithme minimax
    def minimax(self, my_states_current: int, state: GameState, depth: int, alpha: float, beta: float, maximizing_player: bool) -> int:

        player_id = self.get_id()
        all_states_next = [(coordinates, piece.__dict__) for coordinates, piece in state.get_rep().env.items()]
        my_states_next = len({coordinate for coordinate, piece in all_states_next if
                          piece['owner_id'] == player_id})
        # Si nous avons fini de découvrir ou il n'y a plus d'états à découvrir (fin de partie)
        if my_states_next == my_states_current:
            if depth == 1 or state.is_done():
                # On évalue le score de l'état avec la fonction heuristique
                return self.value_state(state)

            # Si le tour est au maximiseur, on maximise le score
            if maximizing_player:
                max_score = float('-inf')
                for action in state.get_possible_actions():
                    next_state = action.get_next_game_state()
                    score = self.minimax(my_states_next, next_state, depth - 1, alpha, beta, False)
                    if score:
                        max_score = max(max_score, score)
                        alpha = max(alpha, score)
                        # Élagage alpha-beta
                        if beta <= alpha:
                            break
                return max_score
            else:
                # Si le tour est au minimiseur, on minimise le score
                min_score = float('inf')
                for action in state.get_possible_actions():
                    next_state = action.get_next_game_state()
                    score = self.minimax(my_states_next, next_state, depth - 1, alpha, beta, True)
                    if score:
                        min_score = min(min_score, score)
                        beta = min(beta, score)
                        # Élagage alpha-beta
                        if beta <= alpha:
                            break
                return min_score

    # Fonction heuristique pour l'évaluation d'un état
    def value_state(self, state: GameState) -> int:
        # Coefficient d'importance attribué à chaque critère heuristique
        piece_count_weight = 10.0
        center_control_weight = 3.0
        exactly_three_weight = 1.5
        groups_weight = 0.1
        neighbours_weight = 0.01

        player_id = self.get_id()
        player_score = abs(state.get_player_score(self))
        adversary_score = abs(next(value for key, value in state.get_scores().items() if key != player_id))

        piece_count_heuristic = (14 - player_score) - (14 - adversary_score)

        coordinates_list = [(coordinates, piece.__dict__) for coordinates, piece in state.get_rep().env.items()]
        center_control_heuristic = sum(
            in_center(key) and value_dict["owner_id"] == player_id for key, value_dict in coordinates_list) - sum(
            in_center(key) and value_dict["owner_id"] != player_id for key, value_dict in coordinates_list)

        coordinates_player = {coordinate for coordinate, piece in coordinates_list if piece['owner_id'] == player_id}
        exactly_three_heuristic = sum(have_three(piece, coordinates_player) for piece in coordinates_player)

        groups = []
        numbers_neighbours = 0
        for piece in coordinates_player:
            neighbours = {neighbour for _, neighbour in state.get_neighbours(*piece).values() if
                          neighbour in coordinates_player}
            add_to_group(groups, piece, neighbours)
            numbers_neighbours += len(neighbours)

        groups_heuristic = 14 - len(groups)
        neighbours_heuristic = numbers_neighbours

        '''
        print(
            piece_count_heuristic, center_control_heuristic, exactly_three_heuristic, groups_heuristic,
            neighbours_heuristic
        )'''

        score = (
            piece_count_weight * piece_count_heuristic +
            center_control_weight * center_control_heuristic +
            exactly_three_weight * exactly_three_heuristic +
            groups_weight * groups_heuristic +
            neighbours_weight * neighbours_heuristic
        )
        return score


def in_center(coordinates):
    return 6 <= coordinates[0] <= 10 and 2 <= coordinates[1] <= 6


def have_three(position, position_list):
    i, j = position
    return any([
        (i+1, j+1) in position_list and (i-1, j-1) in position_list,
        (i+1, j-1) in position_list and (i-1, j+1) in position_list,
        (i+2, j) in position_list and (i-2, j) in position_list
    ])


def add_to_group(groups, piece, neighbours):
    neighbours_list = list(neighbours)  # Convertir l'ensemble en liste
    for group in groups:
        if piece in group or any(neighbour in group for neighbour in neighbours):
            group.update([piece] + neighbours_list)  # Concaténer la liste
            return
    groups.append(set([piece] + neighbours_list))  # Ajouter sous forme d'ensemble


