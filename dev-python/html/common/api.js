async function get_players() {
    const response = await fetch("/players", {method: "POST"});
    if (response.status != 200)return [];
    const json = await response.json();
    return json;
}

async function get_game_state() {
    const response = await fetch("/game_state", {method: "POST"});
    if (response.status != 200)return [];
    const json = await response.json();
    return json;
}
