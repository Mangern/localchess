import os
from threading import local
from time import time
from fasthtml.common import Button, CheckboxX, Fieldset, Input, Label, Main, NotStr, Option, Redirect, Script, Select, Style, fast_app, Div, P, picolink, serve, H1, A, Form, H2
from dataclasses import dataclass
from localchess import LocalChess
from constants import DEFAULT_ELO

css = Style(':root {--pico-font-size:90%,--pico-font-family: Pacifico, cursive;}')

app, rt = fast_app(hdrs=(picolink, css))
localchess = LocalChess()

def home(error: str):
    return Main(
        H1("Localchess"), 
        tournament_view(),
        (P(error, style="color: red") if len(error) else None),
        localchess.player_list(),
        Div(
            Form(
                Fieldset( # TODO: fix PicoCSS stuff
                    Input(placeholder="Username", name="username", ariaLabel="Username"),
                    Button("Add player"),
                ),
                action="/add_player", method="post",
            ),
        ),
        Form(
            Fieldset(
                localchess.player_select("player_white"),
                localchess.player_select("player_black"),
                Select(Option("White won", value=1), Option("Black won", value=-1), Option("Remis", value="0"), name="result"),
                CheckboxX(checked=True, name="add_to_active") if localchess.tournament_table.get_active_id() is not None else None,
                Button("Register game"),
            ),
            action="/register_game", method="post",
            cls="row"
        ),
        H2("Recent games"),
        localchess.games_list(),
        Script("window.history.replaceState({}, document.title, '/')"),
        cls="container-fluid"
    )

def tournament_view():
    active_tournament_id = localchess.tournament_table.get_active_id()
    if active_tournament_id is None:
        return Form(
            Input(placeholder="Tournament name", name="tournament_name"),
            Button("Start tournament"),
            action="/tournament_start", method="post"
        )
    else:
        active_tournament = localchess.tournament_table[active_tournament_id]
        assert active_tournament is not None
        return A(f"Tournament {active_tournament.name} is ongoing", href="/tournament")

@rt("/")
def get(error:str=""): 
    return home(error)

@rt("/add_player")
def post(username: str):
    if not localchess.player_table.add_player(username):
        return Redirect("/?error=Player+already+exists")
    return Redirect("/")

@rt("/register_game")
def post(player_white: int, player_black: int, result: int, add_to_active: bool = False, redir_to: str = ""):
    if player_white == player_black:
        return Redirect(f"/{redir_to}?error=You+cannot+play+yourself")
    if result not in [-1, 0, 1]:
        return Redirect(f"/{redir_to}?error=Invalid+request")
    if not localchess.register_game(player_white, player_black, result, add_to_active):
        return Redirect(f"/{redir_to}?error=Failed+to+register+game")
    return Redirect(f"/{redir_to}")

import matplotlib.pyplot as plt
import numpy as np

@rt("/stats/{player_id}")
def get(player_id: int):
    player = localchess.player_table[player_id]
    if player is None:
        return Redirect("/")

    elo_hist = localchess.player_elo_history(player_id)

    score_hist, times = zip(*elo_hist)

    game_num = list(range(len(score_hist)))

    fig, ax = plt.subplots(figsize = (8, 6), facecolor = "teal")
    ax.plot(game_num, score_hist,
            color = "magenta",
            label = f"{player.name.capitalize()}' ELO-rating over time")
    ax.set_ylabel("ELO")
    #ax.set_xlabel("time (seconds since January 1st 1970)")
    ax.set_xlabel("# Games played") #ca
    ax.axhline(1200, color = "red", label = "Start rating: 1200", linestyle = "dashed", zorder = 0)
    
    ax.scatter(game_num[np.argmax(score_hist)], np.max(score_hist), 
               label = f'Peak rating: {np.max(score_hist):.0f}', zorder = 3,
               marker = '*', color = 'green')
    current_ELO = score_hist[-1]
    ax.scatter(game_num[score_hist.index(current_ELO)], current_ELO, 
               label = f"Current ELO: {current_ELO:.0f}", marker = "+", zorder = 2,
               color = "orange", )
    
    ax.legend(fontsize = 12, framealpha = 0.1)
    fig.suptitle(f"ELO-rating for {player.name.capitalize()}", fontweight = "bold")

    plt.savefig("tmp.svg")
    with open("tmp.svg") as f:
        svg_txt = f.read()

    os.remove("tmp.svg")

    return Div(H1(f"Stats for {player.name}"), NotStr(svg_txt))

@rt("/tournament_start")
def post(tournament_name: str):
    localchess.tournament_table.start_tournament(tournament_name)
    return Redirect("/")

@rt("/tournament_end")
def post():
    localchess.tournament_table.end_active_tournament()
    return Redirect("/")

@rt("/tournament")
def get():
    active_tournament = localchess.tournament_table.get_active()
    if active_tournament is None:
        return Redirect("/")
    return Main(
        H1(f"{active_tournament.name}"),
        localchess.active_tournament_scoreboard(),
        Form(
            Fieldset(
                localchess.player_select("player_white"),
                localchess.player_select("player_black"),
                Select(Option("White won", value=1), Option("Black won", value=-1), Option("Remis", value="0"), name="result"),
                Button("Register game"),
                Input(name="add_to_active", value="1", style="visibility: hidden;"),
                Input(name="redir_to", value="tournament", style="visibility: hidden;")
            ),
            action="/register_game", method="post",
            cls="row"
        ),
        NotStr("<br>"),
        Form(
            Button("End tournament"),
            action="/tournament_end", method="post"
        )
    )

if __name__ == "__main__":
    serve()
