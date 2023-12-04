import pandas as pd

def export_data(gameId, player1, player2, winner, end_game_score1, end_game_score2):
    df = pd.read_excel('stats.xlsx')
    new_line = [{
        "Game ID": gameId,
        "Player 1": player1,
        "Player 2": player2,
        "Winner": winner,
        "End Game Score Player1": end_game_score1,
        "End Game Score Player2": end_game_score2
    }]
    new_df = pd.DataFrame(new_line)
    df = pd.concat([df, new_df], ignore_index=True)
    df.to_excel('stats.xlsx', index=False)