import os
import datetime
import matplotlib.pyplot as plt
import numpy as np

RATING_FILE = "ratings.txt"
HISTORY_FILE = "history.txt"
DEFAULT_RATING = 1200
ELO_K = 24 # Sensitivity of rating changes

def load_scores():
    players = {}
    try:
        with open(RATING_FILE) as f:
            lines = f.readlines()

        for line in lines:
            name = line[:line.find(":")]
            score_str = line[line.find(":")+1:]
            elo, tour, n_played = score_str.split()
            elo, tour = map(float, (elo, tour))
            n_played = int(n_played)
            players[name] = (elo, tour, n_played)
    except:
        pass

    return players


def save_scores(scores):
    with open(RATING_FILE, "w") as f:
        for player in scores:
            f.write(f"{player}:{' '.join(map(str, scores[player]))}\n")


def print_scores(scores: dict[str, float]):
    print("Spiller      ELO    Turnering   Antall partier")
    for player, tup in sorted(scores.items(), key = lambda tup: (tup[1][1], tup[1][0], tup[1][2]), reverse=True):
        elo, tour, n_played = tup
        print(f'{player.capitalize():<10} | {int(round(elo)):04d} | {tour:6.1f}    |       {n_played}')

def add_player(scores):
    name = input("Player name: ").lower()

    if not name:
        return

    if name in scores:
        print("Name exists (not case sensitive)")
        add_player(scores)
        return
    scores[name] = (DEFAULT_RATING, 0, 0)

def get_player(player_list):
    while True:
        print("Please enter the number of the player")
        for idx, player in enumerate(player_list):
            print(f"{idx+1}: {player}")

        print(f"{len(player_list)+1}: Cancel")
        
        ans = input("> ").lower()
        try:
            i = int(ans) - 1
            if 0 <= i < len(player_list):
                return player_list[i]
            elif i == len(player_list):
                return None
        except:
            if ans in player_list:
                return player_list.index(ans)
        print("Invalid input!")

def input_winner():
    while True:
        print("Please enter who won")
        print("1. White")
        print("2. Black")
        print("3. Remis")
        print("4. Cancel")
        ans = input("> ").strip()

        if ans not in ["1", "2", "3", "4"]:
            print("Invalid input!")
            continue

        if ans == "4":
            return None, None

        if ans == "1":
            return 1, 0
        elif ans == "2":
            return 0, 1
        return 0.5, 0.5

def register_game(scores: dict):
    print("Who played white?")
    players = list(scores.keys())
    white = get_player(players)
    if white is None:
        print("Aborted")
        return
    print()
    print("Who played black?")
    black = get_player(players)
    if black is None:
        print("Aborted")
        return
    print()
    if black == white:
        print("You cannot play yourself")
        return

    S_A, S_B = input_winner()
    if S_A is None:
        print("Aborted")
        return
    R_A, score_A, n_played_A = scores[white]
    R_B, score_B, n_played_B = scores[black]

    E_A = 1 / (1 + 10**((R_B - R_A)/400))
    E_B = 1 / (1 + 10**((R_A - R_B)/400))

    scores[white] = (R_A + ELO_K * (S_A - E_A), score_A + S_A, n_played_A + 1)
    scores[black] = (R_B + ELO_K * (S_B - E_B), score_B + S_B, n_played_B + 1)

    with open(HISTORY_FILE, "w+") as f:
        t = datetime.datetime.now().isoformat()
        f.write(f"{white} {black} {S_A} {S_B} {scores[white]} {scores[black]} {t}\n")

def stats(scores: dict):
    players = list(scores.keys())
    player = get_player(players)

    n_white = 0
    n_black = 0

    score_hist = []
    times = []

    with open(HISTORY_FILE, "r") as f:
        for line in f.readlines():
            st = line.replace("(", "").replace(")", "")
            white, black, sa, ta, na, sb, tb, nb, score_wh, score_bl, t = st.split()

            if white != player and black != player:
                continue

            if white == player:
                score_hist.append(float(score_wh))
            else:
                score_hist.append(float(score_bl))

            times.append(datetime.datetime.fromisoformat(t).timestamp())

    plt.plot(times, score_hist)
    plt.suptitle("")
    plt.show()



if __name__ == "__main__":
    while True:
        #os.system("clear")
        scores = load_scores()
        print("--------------- CURRENT SCORES ---------------")
        print_scores(scores)
        print("----------------------------------------------")
        print()

        print("1. Add player")
        print("2. Register game")
        print("3. Stats")
        print("q. Exit")

        ans = input("> ").lower()

        if ans[0] == "1":
            add_player(scores)
        elif ans[0] == "2":
            register_game(scores)
        elif ans[0] == "3":
            stats(scores)
        elif ans[0] == "q":
            exit(0)

        save_scores(scores)
