async function get_players() {
    const response = await fetch("/players", {method: "POST"});
    if (response.status != 200)return [];
    const json = await response.json();
    return json;
}
