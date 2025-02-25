from datetime import datetime
from fasthtml.common import A, Div, Option, Select, Table, Td, Tr, H1
from database import Database
from player import PlayerTable, Player
from game import GameTable
from tournament import TournamentTable, TournamentPlayerTable

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
                *[Tr(Td(f"{player.name.capitalize()}"), Td(f"{score:.1f}"), Td(f"{player.elo:.0f}")) for player, score in player_scores]
        )
