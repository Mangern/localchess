async function refresh() {
    const players = await get_players();

    document.body.innerHTML = "";

    for (const player of players) {
        document.body.innerHTML += player.name + " " + player.elo + "<br>";
    }
}

async function main() {
    setInterval(refresh, 200);
}

main();
