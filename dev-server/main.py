import os
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
def post(player_white: int, player_black: int, result: int, add_to_active: bool = False):
    if player_white == player_black:
        return Redirect("/?error=You+cannot+play+yourself")
    if result not in [-1, 0, 1]:
        return Redirect("/?error=Invalid+request")
    if not localchess.register_game(player_white, player_black, result, add_to_active):
        return Redirect("/?error=Failed+to+register+game")
    return Redirect("/")

import matplotlib.pyplot as plt
@rt("/stats/{player_id}")
def get(player_id: int):
    player = localchess.player_table[player_id]
    if player is None:
        return Redirect("/")

    elo_hist = localchess.player_elo_history(player_id)

    score_hist, times = zip(*elo_hist)

    fig, ax = plt.subplots(figsize = (8, 6), facecolor = "teal")
    ax.plot(times, score_hist,
            color = "magenta",
            label = f"{player.name.capitalize()}' ELO-rating over time")
    ax.set_ylabel("ELO")
    ax.set_xlabel("time (seconds since January 1st 1970)")
    ax.axhline(DEFAULT_ELO, color = "purple", label = f"Start rating: {DEFAULT_ELO}", linestyle = "dashed")
    ax.legend(loc = "upper left", fontsize = 12, framealpha = 0.1)
    fig.suptitle(f"Scoren til {player.name.capitalize()}", fontweight = "bold")
    plt.savefig("tmp.svg")
    with open("tmp.svg") as f:
        svg_txt = f.read()

    os.remove("tmp.svg")

    return Div(H1(f"Stats for {player.name}"), NotStr(svg_txt))

@rt("/tournament_start")
def post(tournament_name: str):
    localchess.tournament_table.start_tournament(tournament_name)
    return Redirect("/")

@rt("/tournament")
def get():
    return H1("Tournament")

if __name__ == "__main__":
    serve()
