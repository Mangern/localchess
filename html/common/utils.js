
function fmt_elo(elo) {
    return Math.round(elo).toString()
}

function *enumerate(iterable) {
    let it = 0;

    for (const el of iterable) {
        yield [it++, el];
    }
}

function element(tag, attrs, ...children) {
    const el = document.createElement(tag);

    for (const key in attrs) {
        el.setAttribute(key, attrs[key]);
    }

    for (const child of children) {
        if (typeof child == "string") {
            el.innerHTML += child;
        } else {
            el.appendChild(child);
        }
    }
    return el;
}

function table(data, column_names = null) {
    const table = document.createElement("table");


    if (column_names !== null) {
        const header_row = document.createElement("tr");
        for (const column_name of column_names) {
            const th = document.createElement("th");
            th.innerHTML = column_name;
            header_row.appendChild(th);
        }
        table.appendChild(header_row);
    }

    for (const row of data) {
        const tr = document.createElement("tr");

        for (const el of row) {
            const td = document.createElement("td");
            td.innerHTML = el;
            tr.appendChild(td);
        }
        table.appendChild(tr);
    }
    return table;
}

function standard_button(text, onclick) {
    const btn = document.createElement("button");
    btn.innerHTML = text;
    btn.classList.add("standard_button");
    btn.addEventListener("click", onclick);
    return btn;
}

function title_element(text) {
    const el = document.createElement("h1");
    el.innerHTML = text;
    el.classList.add("title_element");
    return el;
}

function input_text(name, hint) {
    const input_el = document.createElement("input");
    input_el.classList.add("input_text");
    input_el.name = name;
    input_el.placeholder = hint;
    return input_el;
}

function input_list(name, title, dataset, id_key, display_key) {
    const container = element("div", {class: "container_input_list"});

    container.append(
        element("h2", {}, title),
        ...dataset.map(obj => 
            element(
                "div",
                {class: "input_list_row"},
                element("input", {type: "checkbox"}),
                obj[display_key]
            )
        )
    );

    return container;
}

function input(type, name, ...args) {
    if (type == "text") {
        return input_text(name, ...args);
    } else if (type == "list") {
        return input_list(name, ...args);
    } else {
        console.error("Input not implemented for type:", type);
        return null;
    }
}

function json_form(endpoint, title, ...inputs) {
    const container = document.createElement("div");
    container.classList.add("container_json_form");

    container.appendChild(title_element(title));
    for (const input of inputs) {
        input.classList.add("form_element");
        container.appendChild(input);
    }
    container.appendChild(standard_button("Send inn", () => {
        console.log("Submittt");
    }));
    return container;
}
