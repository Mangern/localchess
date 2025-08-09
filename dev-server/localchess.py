from datetime import datetime
from fasthtml.common import A, Div, Option, Select, Table, Td, Tr, H1
from database import Database
from player import PlayerTable, Player
from game import GameTable
from tournament import TournamentTable, TournamentPlayerTable
from itertools import product
import random

class LocalChess:
    def __init__(self):
        self.db = Database()
        self.player_table            = PlayerTable(self.db)
        self.game_table              = GameTable(self.db)
        self.tournament_table        = TournamentTable(self.db)
        self.tournament_player_table = TournamentPlayerTable(self.db)

    def player_list(self):
        players = self.player_table.get_all()

        players.sort(key=lambda player: player.elo, reverse=True)

        return Table(*[Tr(Td(player.name.capitalize()), Td(f"{player.elo:.0f}"), Td(A("Stats", href=f"/stats/{player.id}"))) for player in players])

    def games_list(self):
        games = self.game_table.get_all()
        players = self.player_table.get_all()
        # TODO: JOIN sql operator instead of 'Python-join'
        id_to_player = {}
        for player in players:
            id_to_player[player.id] = player.name

        games.sort(key=lambda game: datetime.fromisoformat(game.timestamp_iso).timestamp(), reverse=True)

        return Table(
            *[Tr(
                Td(f"{id_to_player[game.white_id]}"), 
                Td(f"{id_to_player[game.black_id]}"), 
                Td("1-0" if game.result == 1 else "0-1" if game.result == -1 else "½-½")) 
              for game in games
            ]
        )

    def player_select(self, name: str):
        return Select(*[Option(player.name.capitalize(), value=player.id) for player in self.player_table.get_all()], name=name),

    # result: 1: white won, -1: black won, 0: remis
    def register_game(self, id_white: int, id_black: int, result: int, add_to_active_tournament: bool) -> bool:
        try:
            elo_white = self.player_table.get_elo(id_white)
            elo_black = self.player_table.get_elo(id_black)
            active_tournament_id = self.tournament_table.get_active_id()
            if active_tournament_id is None or not add_to_active_tournament:
                elo_white, elo_black = self.game_table.register_game(id_white, id_black, elo_white, elo_black, result, None)
            else:
                elo_white, elo_black = self.game_table.register_game(id_white, id_black, elo_white, elo_black, result, active_tournament_id)

            self.player_table.set_elo(id_white, elo_white)
            self.player_table.set_elo(id_black, elo_black)
            return True
        except:
            return False

    # Pair of float elo and unix time
    def player_elo_history(self, player_id) -> list[tuple[float, float]]:
        games = self.game_table.games_of_player(player_id)

        result = []
        for game in games:
            assert game.white_id == player_id or game.black_id == player_id
            elo = game.elo_black if player_id == game.black_id else game.elo_white
            result.append((elo, datetime.fromisoformat(game.timestamp_iso).timestamp()))

        return result

    def get_best_worst_opponent(self, player_id) -> tuple[tuple[Player, int, int, int], tuple[Player, int, int, int]]:
        games = self.game_table.games_of_player(player_id)
        points: dict[int, int] = {}
        wins: dict[int, int] = {}
        draws: dict[int, int] = {}
        losses: dict[int, int] = {}

        for game in games:
            pt = 0
            if player_id == game.white_id:
                if game.result == 1:
                    points[game.black_id] = points.get(game.black_id, 0) + 1
                    wins[game.black_id] = wins.get(game.black_id, 0) + 1
                elif game.result == -1:
                    points[game.black_id] = points.get(game.black_id, 0) - 1
                    losses[game.black_id] = losses.get(game.black_id, 0) + 1
                else:
                    draws[game.black_id] = draws.get(game.black_id, 0) + 1
            else:
                if game.result == -1:
                    points[game.white_id] = points.get(game.white_id, 0) + 1
                    wins[game.white_id] = wins.get(game.white_id, 0) + 1
                elif game.result == 1:
                    points[game.white_id] = points.get(game.white_id, 0) - 1
                    losses[game.white_id] = losses.get(game.white_id, 0) + 1
                else:
                    draws[game.white_id] = draws.get(game.white_id, 0) + 1

        best_id = max(points.keys(), key=lambda k: points[k])
        worst_id = min(points.keys(), key=lambda k: points[k])

        best = self.player_table[best_id]
        worst = self.player_table[worst_id]
        assert best is not None
        assert worst is not None
        return (
            (best, wins.get(best_id, 0), draws.get(best_id, 0), losses.get(best_id, 0)), 
            (worst, wins.get(worst_id, 0), draws.get(worst_id, 0), losses.get(worst_id, 0))
        )


    def active_tournament_scoreboard(self):
        active_tournament_id = self.tournament_table.get_active_id()
        if active_tournament_id is None:
            return H1("No tournament")
        games = self.game_table.get_tournament_games(active_tournament_id)
        scores = {}

        for game in games:
            white_add = 1 if game.result == 1 else 0.5 if game.result == 0 else 0
            black_add = 1 if game.result ==-1 else 0.5 if game.result == 0 else 0
            scores[game.white_id] = scores.get(game.white_id, 0) + white_add
            scores[game.black_id] = scores.get(game.black_id, 0) + black_add

        player_scores = [(self.player_table[k], v) for k, v in scores.items() if self.player_table[k] is not None]
        player_scores.sort(key = lambda t: (t[1], t[0].elo), reverse=True) #pyright: ignore
        return Table(
                *[Tr(Td(A(f"{player.name.capitalize()}", href=f"/stats/{player.id}")), Td(f"{score:.1f}"), Td(f"{player.elo:.0f}")) for player, score in player_scores]
        )

    def get_next_game(self, num_games = 1):
        """
        Returns list of tuples [(id_white, id_black)] as a suggestion for the next games to play.
        """
        games = self.game_table.get_all()
        games.sort(key=lambda game: datetime.fromisoformat(game.timestamp_iso).timestamp(), reverse=True)

        active_player_ids: set[int]
        active_tournament_id = self.tournament_table.get_active_id()

        if active_tournament_id is not None:
            games = self.game_table.get_tournament_games(active_tournament_id)
            active_player_ids = set(game.white_id for game in games) | set(game.black_id for game in games)
        else:
            active_player_ids = set(player.id for player in self.player_table.get_all())

        games = [g for g in games if g.white_id in active_player_ids and g.black_id in active_player_ids]

        player_pairs = set((min(id1, id2), max(id1, id2)) for id1, id2 in product(active_player_ids, active_player_ids) if id1 != id2)

        it = 0
        for g in games[::-1]:
            # WTF :(
            if it == 2:
                break
            pair = (min(g.white_id, g.black_id), max(g.white_id, g.black_id))
            if pair in player_pairs:
                player_pairs.remove((min(g.white_id, g.black_id), max(g.white_id, g.black_id)))
            else:
                continue
            it += 1

        if not player_pairs:
            if not games:
                return []
            game = games[:2][-1]
            return [(game.black_id, game.white_id)]


        ret = []
        for _ in range(num_games):
            player1, player2 = random.choice(list(player_pairs))

            player1, player2 = self.get_player_order(player1, player2, games)
            ret.append((player1, player2))

            player_pairs = [(a, b) for (a, b) in player_pairs if a not in (player1, player2) and b not in (player1, player2)]

        return ret

    def get_player_order(self, player1, player2, games):
        player1_counts = [0, 0]
        player2_counts = [0, 0]
        for game in games:
            if game.white_id == player1:
                player1_counts[0] += 1
            if game.black_id == player1:
                player1_counts[1] += 1
            if game.white_id == player2:
                player2_counts[0] += 1
            if game.black_id == player2:
                player2_counts[1] += 1
        
        # Player with lowest white count gets white
        if player1_counts[0] > player2_counts[0] or (player1_counts[0] == player2_counts[0] and random.randint(1,2)==1):
            player1, player2 = player2, player1

        return player1, player2
