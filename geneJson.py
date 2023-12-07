import random
import json

def generate_weights():
    weight_categories = [
        ("piece_count_weight", 35, 100),
        ("center_control_weight", 10, 100),
        ("exactly_three_weight", 1, 100),
        ("groups_weight", 1, 100),
        ("neighbours_weight", 1, 100)
    ]

    total_weight = 100
    generated_weights = {}

    for category, min_weight, max_weight in weight_categories[:-1]:  # Exclude the last category for now
        max_allocatable = min(max_weight, total_weight - sum(min_w for _, min_w, _ in weight_categories[weight_categories.index((category, min_weight, max_weight))+1:]))
        allocated_weight = random.randint(min_weight, max_allocatable)
        generated_weights[category] = allocated_weight
        total_weight -= allocated_weight

    # Ensure the last category gets the remaining weight
    last_category, last_min, _ = weight_categories[-1]
    generated_weights[last_category] = max(last_min, total_weight)

    return generated_weights


def generate_json_data(min_id, max_id):
    dataset = []
    for player_id in range(min_id, max_id + 1):
        weight = generate_weights()
        entry = {
            'id': player_id,  # Use player_id instead of id
            'piece_count_weight': weight['piece_count_weight'],
            'center_control_weight': weight['center_control_weight'],
            'exactly_three_weight': weight['exactly_three_weight'],
            'groups_weight': weight['groups_weight'],
            'neighbours_weight': weight['neighbours_weight'],
        }
        dataset.append(entry)
    return dataset

def save_to_json_file(data, file_name):
    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4)

data = generate_json_data(1, 40)
save_to_json_file(data, "dataset1.json")