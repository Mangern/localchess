REFRESH_INTERVAL = 500

var creating_tournament = false;

function set_global_content(players) {
    const container = document.getElementById("container_global_content");
    container.innerHTML = "";

    const player_data = [];

    players.sort((a,b) => a.name < b.name ? -1 : 1);
    players.sort((a,b) => b.elo - a.elo);

    for (const [idx, player] of enumerate(players)) {
        player_data.push([idx + 1, player.name, fmt_elo(player.elo)]);
    }

    container.appendChild(table(player_data, ["Plass", "Navn", "Rating"]));
}

function set_tournament_content(tournament_data) {
}

function set_create_tournament_dialog(players) {
    const container = document.getElementById("container_tournament");
    container.innerHTML = "";

    container.appendChild(json_form(
        "/create_tournament",
        "Ny turnering",
        input("text", "tournament_name", "Tittel på turnering"),
        input("list", "tournament_players", "Spillere", players, "id", "name"),
    ));

    creating_tournament = true;
}

function set_create_tournament_button(players) {
    if (creating_tournament)return;
    const container = document.getElementById("container_tournament");
    container.innerHTML = "";

    container.appendChild(standard_button("Ny turnering", () => {
        set_create_tournament_dialog(players);
    }));
}

async function refresh() {
    const game_state = await get_game_state();

    set_global_content(game_state.players);

    if (game_state.active_tournament !== null) {
        set_tournament_content(game_state.tournament_data);
    } else {
        set_create_tournament_button(game_state.players);
    }
}

async function main() {
    refresh();
    setInterval(refresh, REFRESH_INTERVAL);
}

main();
