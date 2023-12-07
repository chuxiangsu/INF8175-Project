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
        """
        Function to implement the logic of the player.

        Args:
            current_state (GameState): Current game state representation
            **kwargs: Additional keyword arguments

        Returns:
            Action: selected feasible action
        """
        # Prendre les actions possibles de l'état initial
        initial_possible_actions = current_state.get_possible_actions()
        # Initialiser la meilleure action à None ainsi que le meilleur score à -inf (valeur la plus basse pour le maximiseur)
        best_action = None
        best_score = float('-inf')
        # Initialiser le alpha et le beta
        alpha = float('-inf')
        beta = float('inf')
        # Itérer sur toutes les actions possibles pour descendre dans l'arbre d'états
        for action in initial_possible_actions:
            # Passer au prochain état après avoir appliquer l'action
            next_state = action.get_next_game_state()
            # Utiliser l'algorithme de minimax pour traverser récursivement les états de l'arbre
            # Depth est la profondeur de la recherche avant de remonter un score
            score = self.minimax(current_state, next_state, depth=3, alpha = alpha, beta = beta, maximizing_player=True)
            # Si un meilleur score est trouvé, mettre à jour le meilleur score avec l'action associée
            if score:
                if score > best_score:
                    best_score = score
                    best_action = action
        # Retourner la meilleure action à faire
        return best_action

    # Algorithme minimax
    def minimax(self, current_state: GameState, next_state: GameState, depth: int, alpha: float, beta: float, maximizing_player: bool) -> int:
        # Chercher la liste des coordonnées des pièces de l'agent de l'état initial et du prochain état
        current_state_coordinates = player_state_coordinates(current_state,self.get_id())
        next_state_coordinates = player_state_coordinates(next_state,self.get_id())
        # On élimine la possibilité de faire une action qui élimine une de nos pièces volontairement
        if len(next_state_coordinates) == len(current_state_coordinates):
            # Si nous avons fini de découvrir ou il n'y a plus d'états à découvrir (fin de partie)
            if depth == 1 or next_state.is_done():
                # On évalue le score de l'état avec la fonction heuristique
                return self.value_state(next_state)
            
            # Si le tour est au maximiseur, on maximise le score
            if maximizing_player:
                max_score = float('-inf')
                # On va chercher les prochaines actions possibles du prochain état
                next_possible_actions = next_state.get_possible_actions()
                for action in next_possible_actions:
                    following_state = action.get_next_game_state()
                    score = self.minimax(next_state, following_state, depth - 1, alpha, beta, False)
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
                # On va chercher les prochaines actions possibles du prochain état
                next_possible_actions = next_state.get_possible_actions()
                for action in next_possible_actions:
                    following_state = action.get_next_game_state()
                    score = self.minimax(next_state, following_state, depth - 1, alpha, beta, True)
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
        # Heuristique du nombre de pièces
        player_score = abs(state.get_player_score(self))
        adversary_score = abs(next(value for key, value in state.get_scores().items() if key != player_id))
        piece_count_heuristic = (14 - player_score) - (14 - adversary_score)
        # Heuristique contrôle du centre
        coordinates_list = [(coordinates, piece.__dict__) for coordinates, piece in state.get_rep().env.items()]
        center_control_heuristic = sum(
            in_center(key) and value_dict["owner_id"] == player_id for key, value_dict in coordinates_list) - sum(
            in_center(key) and value_dict["owner_id"] != player_id for key, value_dict in coordinates_list)
        # Heuristique 3 pièces de suite
        coordinates_player = {coordinate for coordinate, piece in coordinates_list if piece['owner_id'] == player_id}
        exactly_three_heuristic = sum(have_three(piece, coordinates_player) for piece in coordinates_player)
        # Heuristiques groupes et voisins
        groups = []
        numbers_neighbours = 0
        for piece in coordinates_player:
            neighbours = {neighbour for _, neighbour in state.get_neighbours(*piece).values() if neighbour in coordinates_player}
            add_to_group(groups, piece, neighbours)
            numbers_neighbours += len(neighbours)

        groups_heuristic = 14 - len(groups)
        neighbours_heuristic = numbers_neighbours
        # Score calculé à partir de du poids et de la valeur de chaque heuristique
        score = (
            piece_count_weight * piece_count_heuristic +
            center_control_weight * center_control_heuristic +
            exactly_three_weight * exactly_three_heuristic +
            groups_weight * groups_heuristic +
            neighbours_weight * neighbours_heuristic
        )
        return score

# Utils
# Savoir si une coordonnée est dans le centre
def in_center(coordinates):
    return 6 <= coordinates[0] <= 10 and 2 <= coordinates[1] <= 6

# Savoir si il y a 3 pièces collées
def have_three(position, position_list):
    i, j = position
    return any([
        (i+1, j+1) in position_list and (i-1, j-1) in position_list,
        (i+1, j-1) in position_list and (i-1, j+1) in position_list,
        (i+2, j) in position_list and (i-2, j) in position_list
    ])

# Grouping
def add_to_group(groups, piece, neighbours):
    neighbours_list = list(neighbours)  # Convertir l'ensemble en liste
    for group in groups:
        if piece in group or any(neighbour in group for neighbour in neighbours):
            group.update([piece] + neighbours_list)  # Concaténer la liste
            return
    groups.append(set([piece] + neighbours_list))  # Ajouter sous forme d'ensemble

# Retourner les coordonnées des pièces de l'agent selon un état
def player_state_coordinates(state, player_id):
    all_states = [(coordinates, piece.__dict__) for coordinates, piece in state.get_rep().env.items()]
    return {coordinate for coordinate, piece in all_states if piece['owner_id'] == player_id}