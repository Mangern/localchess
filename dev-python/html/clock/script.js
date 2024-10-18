var playing = false;

var clocks = [];

var time_left = [
    3 * 60 * 1000, // ms
    3 * 60 * 1000 // ms
];

var prev_time = -1;
var current_clock;
var clock_interval;
var players_list;
var current_players = [null, null];
var paused = false;

const FLAG_ICON = "&#x2690;";
const PAUSE_ICON = "&#x23F8;";
const PLAY_ICON = "&#x25B6;";

const INCREMENT = 2000;
var dialog_container = null;

function game_running() {
    // Cursed
    return !(prev_time == -1 || prev_time == -2);
}

async function register_result(result) {
    if (dialog_container === null)return;
    const player_white = get_player_by_id(current_players[0]);
    const player_black = get_player_by_id(current_players[1]);
    const result_str = result == "remis" ? "Remis" : 
        (result == "white" ? "Hvit" : "Sort") + " vant";

    if (!confirm("Er du sikker på at du vil registrere resultat? Hvit: " 
        + player_white.name + ", Sort: " + 
          player_black.name + ". Resultat: " + result_str))return;

    dialog_container.innerHTML = "Sender...";

    const response = await fetch("/register_result", {method: "POST", body: JSON.stringify({
        white: player_white.id,
        black: player_black.id,
        result: result
    })});

    if (response.status != 200) {
        dialog_container.innerHTML = "Sending mislyktes.";
        return;
    }
    dialog_container.innerHTML = "";
    dialog_container.appendChild(text_element("Sending vellykket"));

    const restart_btn = document.createElement("button");
    restart_btn.classList.add("flag_btn");

    restart_btn.addEventListener("click", () => window.location.reload());
    restart_btn.innerText = "Start på nytt";
    restart_btn.style.width = "80%";
    dialog_container.appendChild(restart_btn);
}

function dialog_button(text, class_name, onclick) {
    const div = document.createElement("div");
    div.innerText = text;
    div.classList.add("dialog_button");
    div.classList.add(class_name);
    div.addEventListener("click", onclick);
    return div;
}

function finish_game_dialog() {
    if (dialog_container !== null)return;
    paused = true;
    dialog_container = document.createElement("div");
    dialog_container.classList.add("dialog");

    dialog_container.appendChild(text_element("Registrer resultat", "dialog_title"));
    dialog_container.appendChild(dialog_button(
        get_player_by_id(current_players[0]).name,
        "result_white",
        () => {
            register_result("white");
        }
    ));
    dialog_container.appendChild(dialog_button(
        "Remis",
        "result_remis",
        () => {
            register_result("remis");
        }
    ));
    dialog_container.appendChild(dialog_button(
        get_player_by_id(current_players[1]).name,
        "result_black",
        () => {
            register_result("black");
        }
    ));
    dialog_container.appendChild(dialog_button(
        "Cancel",
        "result_cancel",
        () => {
            dialog_container.remove();
            dialog_container = null;
            paused = false;
        }
    ));

    document.body.appendChild(dialog_container);
}

function clock_click(clock_id) {
    if (dialog_container !== null)return;
    if (prev_time == -2) {
        finish_game_dialog();
        return;
    }
    if (prev_time != -1) {
        if (clock_id == current_clock)switch_clock();
        return;
    }

    prev_time = new Date();
    current_clock = 1 - clock_id;
    clock_interval = setInterval(update_clock, 100);
}


function end_clocks() {
    console.log("woooo");
    clocks[current_clock].innerHTML = FLAG_ICON;
    clocks[current_clock].classList.remove("current");
    clocks[current_clock].classList.add("flagged");
    clearInterval(clock_interval);
    prev_time = -2;
}

function switch_clock() {
    time_left[current_clock] += INCREMENT;
    update_clock();
    current_clock = 1 - current_clock;
    update_clock();
}

function format_time(time_ms) {
    let mins = Math.floor(time_ms / (60 * 1000));
    let secs = Math.round((time_ms - mins * 60 * 1000) / 1000);

    if (secs == 60) {
        ++mins;
        secs = 0;
    }
    let minstr = mins.toString();
    while (minstr.length < 2)minstr = "0" + minstr;

    let secstr = secs.toString();
    while (secstr.length < 2)secstr = "0" + secstr;
    return minstr + ":" + secstr;
}

function update_clock() {
    if (prev_time == -1 || prev_time == -2)return;
    var delta = paused ? 0 : (new Date()) - prev_time;

    if (delta >= time_left[current_clock]) {
        end_clocks();
        return;
    }

    time_left[current_clock] -= delta;

    const tl = time_left[current_clock];

    clocks[current_clock].innerText = format_time(tl);
    clocks[current_clock].classList.add("current");
    clocks[1 - current_clock].classList.remove("current");

    prev_time = new Date();
}

function get_player_by_id(player_id) {
    for (const player of players_list) {
        if (player.id == player_id)return player;
    }
}

function text_element(str, classname) {
    const el = document.createElement("div");
    el.className = classname;
    el.innerText = str;
    return el;
}

function flag_button() {
    const btn_el = document.createElement("button");
    btn_el.classList.add("flag_btn");
    btn_el.innerHTML = FLAG_ICON;
    btn_el.addEventListener("click", (evt) => finish_game_dialog());
    return btn_el;
}

function pause_button() {
    const btn_el = document.createElement("button");
    btn_el.classList.add("flag_btn");
    btn_el.innerHTML = PAUSE_ICON;

    function pause_click() {
        if (!game_running())return;
        paused = !paused;

        if (paused) {
            btn_el.innerHTML = PLAY_ICON;
        } else {
            btn_el.innerHTML = PAUSE_ICON;
        }
    }

    btn_el.addEventListener("click", pause_click);
    return btn_el;
}

function set_status_area() {
    const status_container = document.getElementById("status_container");
    status_container.classList.add("status_container");
    
    status_container.appendChild(
        text_element("Hvit: " + get_player_by_id(current_players[0]).name, "left"),
    );

    status_container.appendChild(flag_button());
    status_container.appendChild(pause_button());

    status_container.appendChild(
        text_element("Sort: " + get_player_by_id(current_players[1]).name, "right"),
    );
}

function set_player(clock_id, player_id) {
    current_players[clock_id] = player_id;
    const my_container = clocks[clock_id];
    const other_container = clocks[clock_id ^ 1];
    my_container.innerHTML = "";
    const time_el = text_element(format_time(time_left[clock_id]));
    my_container.appendChild(time_el);
    my_container.classList.add("playing");

    if (current_players[clock_id ^ 1] === null) {
        for (const el of other_container.children) {
            if (el.player_id == player_id) {
                el.remove();
            }
        }
    } else {
        // Both players are selected and ready
        set_status_area();
        clocks[0].addEventListener("click", (evt) => clock_click(0));
        clocks[1].addEventListener("click", (evt) => clock_click(1));
    }
}

// TODO: Might change if we have a lot of players
function populate_players(players, clock_id) {
    container = clocks[clock_id];

    container.innerHTML = "";
    for (const player of players) {
        const player_el = document.createElement("div");
        player_el.classList.add("player_select");
        player_el.innerText = player.name;
        player_el.addEventListener("click", (evt) => {
            evt.stopPropagation();
            set_player(clock_id, player.id);
        });
        player_el.player_id = player.id;
        container.appendChild(player_el);
    }
}

async function main() {

    players_list = await get_players();

    const clock_one = document.getElementById("clock_one")
    const clock_two = document.getElementById("clock_two")

    clocks.push(clock_one);
    clocks.push(clock_two);

    populate_players(players_list, 0);
    populate_players(players_list, 1);

    //set_player(0, 0);
    //set_player(1, 1);
}

main()
