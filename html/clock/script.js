var playing = false;

var clocks = [];

var time_left = [
    5 * 1000, // ms
    5 * 1000 // ms
];

var prev_time = -1;
var current_clock;
var clock_interval;

const INCREMENT = 2000;

function clock_click(clock_id) {
    if (prev_time == -2) {
        if (confirm("Vil du starte på nytt?")) {
            window.location.reload();
        }
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

function query_players_and_submit() {
}

function end_clocks() {
    console.log("woooo");
    clocks[current_clock].innerHTML = "&#x2690;";
    clocks[current_clock].classList.remove("current");
    clocks[current_clock].classList.add("flagged");
    clearInterval(clock_interval);
    query_players_and_submit();
    prev_time = -2;
}

function switch_clock() {
    time_left[current_clock] += INCREMENT;
    update_clock();
    current_clock = 1 - current_clock;
    update_clock();
}

function update_clock() {
    if (prev_time == -1 || prev_time == -2)return;
    var delta = (new Date()) - prev_time;

    if (delta >= time_left[current_clock]) {
        end_clocks();
        return;
    }

    time_left[current_clock] -= delta;

    const tl = time_left[current_clock];

    let mins = Math.floor(tl / (60 * 1000));
    let secs = Math.round((tl - mins * 60 * 1000) / 1000);

    if (secs == 60) {
        ++mins;
        secs = 0;
    }

    let minstr = mins.toString();
    while (minstr.length < 2)minstr = "0" + minstr;

    let secstr = secs.toString()
    while (secstr.length < 2)secstr = "0" + secstr;

    clocks[current_clock].innerText = minstr + ":" + secstr;
    clocks[current_clock].classList.add("current");
    clocks[1 - current_clock].classList.remove("current");



    prev_time = new Date();
}

function main() {
    const clock_one = document.getElementById("clock_one")
    const clock_two = document.getElementById("clock_two")

    clocks.push(clock_one);
    clocks.push(clock_two);

    clock_one.addEventListener("click", (evt) => clock_click(0));
    clock_two.addEventListener("click", (evt) => clock_click(1));
}

main()
