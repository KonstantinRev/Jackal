document.addEventListener('DOMContentLoaded', function() {
    modal() // load modal window
    if (play == 'False') {
        load_ships(empty); // load board without ability to move
    } else {
        if (current_user == 1) {
            main(); // Call main function
            pass_turn(); // Call pass turn function
        } else {
            load_ships(empty); // load board without ability to move
        }
    }
});

function main() {
    fetch(`/events/` + board)
    .then(response => response.json())
    .then(data => {
        if (data.event === 1 || data.event === 2 || data.event === 3 || data.event === 4) { // lighthouse event and times to choose tiles to open
            load_ships(empty); // load board
            lighthouse_event();
        } else if (data.event === 5) {
            fetch('/end_lighthouse/' + board, { // end lighthouse event
                method: 'PUT'
            }).then(function() {
                location.reload()
            });
        } else if (data.event === 6 || data.event === 7) {
            load_ships(empty); // load board
            earthquake_event();
        } else if (data.event === 8) {
            fetch('/end_earthquake/' + board, { // end earthquake event
                method: 'PUT'
            }).then(function() {
                location.reload()
            });
        } else {
            fetch(`/return_moves_or_not/` + board)
            .then(response => response.json())
            .then(data => {
                if (data.moves === 0) {
                    load_ships(pirat_move); // load board
                } else {
                    load_ships(moves); // load moves
                }
            });
        }
    });
}


function with_coin() {
    fetch(`/with_coin_return/` + board)
    .then(response => response.json())
    .then(data => {
        if (data.with_coin == 0) {
            let x = document.getElementById('with_coin');
            x.className = "action"; // make button - regualar (if without coin)
            x.innerHTML = "без монеты";
        } else {
            let x = document.getElementById('with_coin');
            x.className = "action_with"; // make button green (if with coin)
            x.innerHTML = "с монетой";
        }
    });
    let y = document.getElementById('with_coin');
    y.addEventListener('click', function() {
        fetch('/with_coin_change/' + board, { // change movement with coin or not
            method: 'PUT'
        }).then(function() {
            location.reload();
        });
    });
}


function with_treasure() {
    fetch(`/with_treasure_return/` + board)
    .then(response => response.json())
    .then(data => {
        if (data.with_treasure == 0) {
            let x = document.getElementById('with_treasure');
            x.className = "action"; // make button - regualar (if without coin)
            x.innerHTML = "без сокровища";
        } else {
            let x = document.getElementById('with_treasure');
            x.className = "action_with"; // make button green (if with coin)
            x.innerHTML = "с сокровищем";
        }
    });
    let y = document.getElementById('with_treasure');
    y.addEventListener('click', function() {
        fetch('/with_treasure_change/' + board, { // change movement with treasure or not
            method: 'PUT'
        }).then(function() {
            location.reload();
        });
    });
}


function empty() {
    let x = 1
}


function load_ships(callback) {
    fetch(`/load_ships/` + board)
    .then(response => response.json())
    .then(data => {
        count = 1
        data.ships.forEach( function(x) {
            tile = document.getElementById(x);
            tile.outerHTML = '<button class="TILE ship' + count + '" id="' + x + '"></button>';
            count += 1;
        });
    }).then(function() {
        load_pirats(callback);
    })
}


function load_pirats(callback) {
    fetch(`/load_pirats/` + board)
    .then(response => response.json())
    .then(data => {
        count = 1
        data.pirats.forEach( function(x) {
            x.forEach( function(y) {
                // If pirat is dead - don't print him
                if (y[0] != 0) {
                    tile = document.getElementById(y[0]);
                    tile.innerHTML = '<a class="pirat' + count + '"></a>';
                }
            });
            count += 1;
        });
        if (data.bengan != 0) {
            tile = document.getElementById(data.bengan);
            temp = tile.innerHTML
            tile.innerHTML = temp + '<a class="bengan"></a>';
        }
        if (data.missioner != 0) {
            tile = document.getElementById(data.missioner);
            temp = tile.innerHTML
            tile.innerHTML = temp + '<a class="missioner"></a>';
        }
        if (data.missioner_pirat != 0) {
            tile = document.getElementById(data.missioner_pirat);
            temp = tile.innerHTML
            tile.innerHTML = temp + '<a class="missioner_pirat"></a>';
        }
        if (data.friday != 0) {
            tile = document.getElementById(data.friday);
            temp = tile.innerHTML
            tile.innerHTML = temp + '<a class="friday"></a>';
        }
    }).then(function() {
        load_coins();
    }).then(function() {
        callback();
    });
}

function load_coins() {
    fetch(`/load_coins/` + board)
    .then(response => response.json())
    .then(data => {
        data.coins.forEach( function(x) {
            if (x[0] != 0 && x[0] != 1 && x[0] != 2 && x[0] != 3 && x[0] != 4 && x[0] != 5) {
                tile = document.getElementById(x[0]);
                let temp = tile.innerHTML
                if (x[3] == 0) {
                    tile.innerHTML = temp + '<a class="coin">' + x[1] + '</a>';
                } else {
                    if (x[1] === 1) {
                        tile.innerHTML = temp + '<a class="mini-mini-coin layer_coin_' + x[2] + '_' + x[3] + '"></a>';
                    } else {
                        tile.innerHTML = temp + '<a class="mini-mini-coin layer_coin_' + x[2] + '_' + x[3] + '">' + x[1] + '</a>';
                    }
                }
            }
        });
    }).then(function() {
        fetch(`/load_treasure/` + board)
        .then(response => response.json())
        .then(data => {
            if (data.treasure != 0 && data.treasure != 1 && data.treasure != 2 && data.treasure != 3 && data.treasure != 4) {
                tile = document.getElementById(data.treasure);
                let temp = tile.innerHTML
                if (data.layer === 0) {
                    tile.innerHTML = temp + '<a class="treasure"></a>';
                } else {
                    tile.innerHTML = temp + '<a class="mini-mini-treasure layer_treasure_' + data.tile + '_' + data.layer + '"></a>';
                }
                }
            });
    }).then(function() {
    fetch(`/load_rum/` + board)
    .then(response => response.json())
    .then(data => {
        data.rum.forEach( function(x) {
            tile = document.getElementById(x[0]);
            for (var i = 0; i < x[1]; i++) {
                temp = tile.innerHTML
                tile.innerHTML = temp + '<a class="rum" style="left:' + (3 * i) + '0%"></a>';
            }
            });
        });
    });
}

function pirat_move() {
    load_possible_pirats(hover, choose_pirat); // load pirats that can move
    //hover(); // Load possible moves when mouse hover over pirat
    //choose_pirat(); // Load pirat choose and get possible moves
}


function moves() {
    load_possible_pirats(moves_move, empty)
}


function load_possible_pirats(callback1, callback2) {
    fetch(`/pirats_that_can_move/` + board)
    .then(response => response.json())
    .then(data => {
        data.live.forEach(function(pirat) {
            let x = document.getElementById(pirat);
            x.className = 'pirats live choose';
        });
    }).then(function() {
        callback1();
        callback2();
    });
}

function choose_pirat() {

    // get all available pirats
    pirats = document.querySelectorAll('.live');

    for (let i = 0; i < pirats.length; i++) {
        // take 1 pirat at a time
        const pirat = pirats[i];
        // make red border for pirats on board
        document.getElementById(pirat.value).style.border = "2px solid red";
        // add click function
        pirat.addEventListener('click', PiratMove);
    }

    function PiratMove(e) {

        let data = e.target.closest('data'); // Look for children of tile be clicked
        if (!data) return;

        // get all available pirats
        pirats = document.querySelectorAll('.live');

        for (let i = 0; i < pirats.length; i++) {
            // take 1 pirat at a time
            const pirat = pirats[i];
            // remove click function
            pirat.removeEventListener('click', PiratMove);
        }

        // Load tile into tile_info
        tile_info(this.value);

        let tile_value = this.value
        // Make pirat chosen for move
        fetch(`/make_mover/` + this.id + '/' + board)
        .then( function () {

            // Look for coins or treasure on tile
            fetch(`/have_coin/` + tile_value + '/' + board)
            .then(response => response.json())
            .then(data => {
                if (data.coin === 1) {
                    let t = document.getElementById('with_coin'); // make button appear (to move with coin)
                    t.style.display = 'block'
                    with_coin();
                }
                if (data.treasure === 1) {
                    let b = document.getElementById('with_treasure'); // make button appear (to move with treasure)
                    b.style.display = 'block'
                    with_treasure();
                }
            });
            // if pirat is in fortress and can ressurect
            fetch(`/can_ressurect/` + board)
            .then(response => response.json())
            .then(data => {
                if (data.ressurect === 1) {
                    let res = document.getElementById('ressurect');
                    res.style.display = 'block'
                    ressurect()
                }
            });
            // if pirat can drink rum
            fetch(`/can_drink_rum/` + tile_value + '/' + board)
            .then(response => response.json())
            .then(data => {
                if (data.drink === 1) {
                    let rum = document.getElementById('drink_rum');
                    rum.style.display = 'block'
                    drink_rum(tile_value)
                }
            });
        });

        // Get possible moves
        fetch(`/possible_moves/` + this.value + this.getAttribute("name") + '/' + board + '/' + '0' + '/' + this.id)
        .then(response => response.json())
        .then(data => {
            all_tiles = document.querySelectorAll('.TILE')
            all_tiles.forEach( function(x) {
                x.style.opacity = '0.5';
            });
            document.getElementById(this.value).style.opacity = '1';
            data.moves.forEach( function(g) {
                tile = document.getElementById(g);
                tile.removeAttribute("disabled");
                tile.style.bottom = '3px';
                tile.style.right = '3px';
                tile.style.opacity = '1';
                tile.style.border = '2px purple solid';
                tile.style.borderRadius = '30%';
                if (tile.className.includes('tile_inv')) {
                    tile.className = 'tile_inv water'
                }
                tile.addEventListener('click', function() {
                    fetch('/move_pirat/' + data.from + this.id + '/' + board, { // move pirat
                        method: 'PUT'
                    }).then(function () {
                        document.querySelectorAll('button').forEach(function (h) {
                            h.setAttribute('disabled', 'true');
                        });
                    }).then( function() {
                        location.reload()
                    });
                });
            });
        });

        // Make ability to re-choose the pirat
        document.getElementById(this.id).addEventListener('click', function() {
            fetch('/remove_mover/' + board, { // remove selection and movement with coin
                method: 'PUT'
            }).then( function() {
                location.reload()
            });
        });
    }
}


function moves_move() {
    // Load pirat (mover)
    fetch(`/load_pirats_turn/` + board)
    .then(response => response.json())
    .then(data => {
        let pirats = document.querySelectorAll('.live');
        for (let i = 0; i < pirats.length; i++) {
            const pirat = pirats[i];
            if (pirat.id == data.name) {
                pirat.className = "pirats live green";
                // Make ability to re-choose the pirat
                document.getElementById(pirat.id).addEventListener('click', function() {
                    fetch('/remove_mover/' + board, { // remove selection and movement with coin
                        method: 'PUT'
                    }).then( function() {
                        location.reload()
                    });
                });
            } else {
                pirat.className = "pirats live";
            }
        }
        tile = document.getElementById(data.pirat);
        tile.style.border = "1px solid yellow";
        tile_info(tile.id); // Load tile into tile_info

        // Look for coins or treasure on tile
        fetch(`/have_coin/` + tile.id + '/' + board)
        .then(response => response.json())
        .then(data => {
            if (data.coin === 1) {
                let t = document.getElementById('with_coin'); // make button appear (to move with coin)
                t.style.display = 'block'
                with_coin();
            }
            if (data.treasure === 1) {
                let b = document.getElementById('with_treasure'); // make button appear (to move with treasure)
                b.style.display = 'block'
                with_treasure();
            }
        });

        // if pirat is in fortress and can ressurect
        fetch(`/can_ressurect/` + board)
        .then(response => response.json())
        .then(data => {
            if (data.ressurect === 1) {
                let res = document.getElementById('ressurect');
                res.style.display = 'block'
                ressurect()
            }
        });
        // if pirat can drink rum
        fetch(`/can_drink_rum/` + tile.id + '/' + board)
        .then(response => response.json())
        .then(data => {
            if (data.drink === 1) {
                let rum = document.getElementById('drink_rum');
                rum.style.display = 'block'
                drink_rum(tile.id)
            }
        });

        // Get possible moves
        fetch(`/possible_moves/` + tile.id + document.querySelector('.green').getAttribute("name") + '/' + board + '/' + '0' + '/' + '0')
        .then(response => response.json())
        .then(data => {
            all_tiles = document.querySelectorAll('.TILE')
            all_tiles.forEach( function(x) {
                x.style.opacity = '0.5';
            });
            document.getElementById(tile.id).style.opacity = '1';
            data.moves.forEach( function(g) {
                new_tile = document.getElementById(g);
                new_tile.removeAttribute("disabled");
                new_tile.style.bottom = '3px';
                new_tile.style.right = '3px';
                new_tile.style.opacity = '1';
                new_tile.style.border = '2px purple solid';
                new_tile.style.borderRadius = '30%';
                if (new_tile.className.includes('tile_inv')) {
                    new_tile.className = 'tile_inv water'
                }
                new_tile.addEventListener('click', function() {
                    fetch('/move_pirat/' + data.from + this.id + '/' + board, { // move pirat
                        method: 'PUT'
                    }).then(function () {
                        document.querySelectorAll('button').forEach(function (h) {
                            h.setAttribute('disabled', 'true');
                        });
                    }).then( function() {
                        location.reload()
                    });
                });
            });
        });
    });
}


function hover() {

    buttons = document.querySelectorAll('.live'); // Get all pirat buttons

    for (let i = 0; i < buttons.length; i++) {
        const button = buttons[i];
        button.addEventListener("mouseenter", mouseEnter);
        button.addEventListener("mouseleave", mouseLeave);
        button.addEventListener("click", Remove);
    }
    function mouseEnter(e) {
        fetch(`/possible_moves/` + e.target.value + e.target.getAttribute("name") + '/' + board + '/' + '0' + '/' + e.target.id)
        .then(response => response.json())
        .then(data => {                
            all_tiles = document.querySelectorAll('.TILE')
            all_tiles.forEach( function(x) {
                x.style.opacity = '0.5';
            });
            document.getElementById(e.target.value).style.opacity = '1';
            data.moves.forEach( function(g) {
                new_tile = document.getElementById(g);
                new_tile.style.bottom = '3px';
                new_tile.style.right = '3px';
                new_tile.style.opacity = '1';
                new_tile.style.border = '2px purple solid';
                new_tile.style.borderRadius = '30%';
                if (new_tile.className.includes('tile_inv')) {
                    new_tile.className = 'tile_inv water'
                }
            });
        });
        tile_info(e.target.value);
    }
    function mouseLeave(e) {
        fetch(`/possible_moves/` + e.target.value + e.target.getAttribute("name") + '/' + board + '/' + '0' + '/' + '0')
        .then(response => response.json())
        .then(data => {
            all_tiles = document.querySelectorAll('.TILE')
            all_tiles.forEach( function(x) {
                x.style.opacity = '1';
            });
            data.moves.forEach( function(g) {
                new_tile = document.getElementById(g);
                new_tile.style.bottom = '';
                new_tile.style.right = '';
                new_tile.style.border = '';
                new_tile.style.borderRadius = '';
                if (new_tile.className.includes('tile_inv')) {
                    new_tile.className = 'tile_inv'
                }
            });
        });
        tile_info_clear();
    }
    function Remove(e) {
        tile_info_clear();
        pirats = document.querySelectorAll('.choose'); // Remove hover ability
        pirats.forEach(function(x) {
            x.className = "pirats live"
        })
        let data = e.target.closest('data'); // Look for children of tile be clicked
        if (!data) return;
        data.className = 'pirats live green'; // make highlight of chosen pirat
        for (let i = 0; i < buttons.length; i++) { // Remove Event Listeners
            const button = buttons[i];
            button.removeEventListener("click", Remove);
            button.removeEventListener("mouseenter", mouseEnter);
            button.removeEventListener("mouseleave", mouseLeave);
        }
    }
}


function lighthouse_event() {
    fetch(`/lighthouse_event/` + board)
    .then(response => response.json())
    .then(data => {
        all_tiles = document.querySelectorAll('.TILE')
        all_tiles.forEach( function(x) {
            x.style.opacity = '0.5';
        });
        data.closed_tiles.forEach( function(x) {
            closed_tile = document.getElementById(x);
            closed_tile.removeAttribute("disabled");
            closed_tile.style.bottom = '3px';
            closed_tile.style.right = '3px';
            closed_tile.style.opacity = '1';
            closed_tile.style.border = '2px purple solid';
            closed_tile.style.borderRadius = '30%';
            closed_tile.addEventListener('click', function() {
                fetch('/open_tile_light/' + this.id + '/' + board, { // open tile
                    method: 'PUT'
                }).then(function () {
                    document.querySelectorAll('button').forEach(function (h) {
                        h.setAttribute('disabled', 'true');
                    });
                }).then(function() {
                    location.reload()
                });
            });
        });
    });
}


function earthquake_event() {
    fetch(`/earthquake_event/` + board)
    .then(response => response.json())
    .then(data => {
        all_tiles = document.querySelectorAll('.TILE')
        all_tiles.forEach( function(x) {
            x.style.opacity = '0.5';
        });
        data.empty_tiles.forEach( function(x) {
            empty_tile = document.getElementById(x);
            empty_tile.removeAttribute("disabled");
            empty_tile.style.bottom = '3px';
            empty_tile.style.right = '3px';
            empty_tile.style.opacity = '1';
            empty_tile.style.border = '2px purple solid';
            empty_tile.style.borderRadius = '30%';
            empty_tile.addEventListener('click', function() {
                fetch('/change_tile_earth/' + this.id + '/' + board, { // change tile
                    method: 'PUT'
                }).then(function () {
                    document.querySelectorAll('button').forEach(function (h) {
                        h.setAttribute('disabled', 'true');
                    });
                }).then(function () {
                    location.reload()
                });
            });
        });
    });
}


function pass_turn() {
    button = document.getElementById("pass_turn");
    button.style.display = 'block'
    button.addEventListener('click', function() {
        fetch(`/is_mover/` + board)
        .then(response => response.json())
        .then(data => {
            if (data.mover) {
                const pass = confirm('При пропуске хода - ходивший пират умрет, согласны ?');
                if(pass) {
                    fetch('/pass_turn/' + board, { // pass turn
                        method: 'PUT'
                    }).then(function() {
                        location.reload()
                    });
                } else {
                    console.log('отмена')
                }
            } else {
                fetch('/pass_turn/' + board, { // pass turn
                    method: 'PUT'
                }).then(function() {
                    location.reload()
                });
            }
        });
    });
}


function tile_info(id) {
    let x = document.getElementById(id);
    console.log(x)
    let y = document.getElementById('info_tile');
    if (x.className == 'TILE tile_inv') {
        y.className = 'water'
    } else {
        y.className = x.className;
        if (y.className == 'TILE tile_10') { // if target is jungle-to-go
            y.className = 'tile_10'
            fetch(`/find_to_go_pirats/` + id + '/' + board)// find all pirats on that to-go tile
            .then(response => response.json())
            .then(data => {
                data.persons.forEach( function(person) {
                    let info = document.getElementById('info_tile');
                    temp = info.innerHTML
                    info.innerHTML = temp + '<a class="mini-pirat' + person[0] + person[1] + ' layer_10_' + person[2] + '"></a>'
                });
                data.coins.forEach( function(coin) {
                    let info = document.getElementById('info_tile');
                    temp = info.innerHTML
                    if (coin[1] === 1) {
                        info.innerHTML = temp + '<a class="mini-coin layer_coin_10_' + coin[0] + '"></a>'
                    } else {
                        info.innerHTML = temp + '<a class="mini-coin layer_coin_10_' + coin[0] + '">' + coin[1] + '</a>'
                    }
                });
                if (data.treasure != 200) {
                    let info = document.getElementById('info_tile');
                    temp = info.innerHTML
                    info.innerHTML = temp + '<a class="mini-treasure layer_treasure_10_' + data.treasure + '"></a>'
                }
            });
        } else if (y.className == 'TILE tile_11') { // if target is desert
            y.className = 'tile_11'
            fetch(`/find_to_go_pirats/` + id + '/' + board)// find all pirats on that to-go tile
            .then(response => response.json())
            .then(data => {
                data.persons.forEach( function(person) {
                    let info = document.getElementById('info_tile');
                    temp = info.innerHTML
                    info.innerHTML = temp + '<a class="mini-pirat' + person[0] + person[1] + ' layer_11_' + person[2] + '"></a>'
                });
                data.coins.forEach( function(coin) {
                    let info = document.getElementById('info_tile');
                    temp = info.innerHTML
                    if (coin[1] === 1) {
                        info.innerHTML = temp + '<a class="mini-coin layer_coin_11_' + coin[0] + '"></a>'
                    } else {
                        info.innerHTML = temp + '<a class="mini-coin layer_coin_11_' + coin[0] + '">' + coin[1] + '</a>'
                    }
                });
                if (data.treasure != 200) {
                    let info = document.getElementById('info_tile');
                    temp = info.innerHTML
                    info.innerHTML = temp + '<a class="mini-treasure layer_treasure_11_' + data.treasure + '"></a>'
                }
            });
        } else if (y.className == 'TILE tile_12') { // if target is swamp
            y.className = 'tile_12'
            fetch(`/find_to_go_pirats/` + id + '/' + board)// find all pirats on that to-go tile
            .then(response => response.json())
            .then(data => {
                data.persons.forEach( function(person) {
                    let info = document.getElementById('info_tile');
                    temp = info.innerHTML
                    info.innerHTML = temp + '<a class="mini-pirat' + person[0] + person[1] + ' layer_12_' + person[2] + '"></a>'
                });
                data.coins.forEach( function(coin) {
                    let info = document.getElementById('info_tile');
                    temp = info.innerHTML
                    if (coin[1] === 1) {
                        info.innerHTML = temp + '<a class="mini-coin layer_coin_12_' + coin[0] + '"></a>'
                    } else {
                        info.innerHTML = temp + '<a class="mini-coin layer_coin_12_' + coin[0] + '">' + coin[1] + '</a>'
                    }
                });
                if (data.treasure != 200) {
                    let info = document.getElementById('info_tile');
                    temp = info.innerHTML
                    info.innerHTML = temp + '<a class="mini-treasure layer_treasure_12_' + data.treasure + '"></a>'
                }
            });
        } else if (y.className == 'TILE tile_13') { // if target is waterfall
            y.className = 'tile_13'
            fetch(`/find_to_go_pirats/` + id + '/' + board)// find all pirats on that to-go tile
            .then(response => response.json())
            .then(data => {
                data.persons.forEach( function(person) {
                    let info = document.getElementById('info_tile');
                    temp = info.innerHTML
                    info.innerHTML = temp + '<a class="mini-pirat' + person[0] + person[1] + ' layer_13_' + person[2] + '"></a>'
                });
                data.coins.forEach( function(coin) {
                    let info = document.getElementById('info_tile');
                    temp = info.innerHTML
                    if (coin[1] === 1) {
                        info.innerHTML = temp + '<a class="mini-coin layer_coin_13_' + coin[0] + '"></a>'
                    } else {
                        info.innerHTML = temp + '<a class="mini-coin layer_coin_13_' + coin[0] + '">' + coin[1] + '</a>'
                    }
                });
                if (data.treasure != 200) {
                    let info = document.getElementById('info_tile');
                    temp = info.innerHTML
                    info.innerHTML = temp + '<a class="mini-treasure layer_treasure_13_' + data.treasure + '"></a>'
                }
            });
        }
    }
    tile_op = document.getElementById('info_tile')
    if (tile_op.className.slice(0, 4) == 'TILE') {
        tile_op.className = tile_op.className.slice(5)
    }
}

function tile_info_clear() {
    let x = document.getElementById('info_tile');
    x.className = 'tile_closed'
    x.innerHTML = ''
}

function ressurect() {
    let res = document.getElementById('ressurect');
    res.addEventListener('click', function() {
        fetch('/ressurect/' + board, { // ressurect pirat
            method: 'PUT'
        }).then(function() {
            location.reload()
        });
    });
}

function drink_rum(id) {
    let rum = document.getElementById('drink_rum');
    rum.addEventListener('click', function() {
        fetch('/drink/' + id + '/' + board, { // drink
            method: 'PUT'
        }).then(function() {
            location.reload()
        });
    });
}

function modal() {
    // Get modal
    var statsmodal = document.getElementById("statsModal");
    var movesmodal = document.getElementById("movesModal");

    // Get button for modal open
    var stats = document.getElementById("stats");
    var moves = document.getElementById("moves");

    // Get element to close modal
    var spanS = document.getElementsByClassName("closeStats")[0];
    var spanM = document.getElementsByClassName("closeMove")[0];

    stats.onclick = function() {
        statsmodal.style.display = "block";
    }

    moves.onclick = function() {
        movesmodal.style.display = "block";
    }

    spanS.onclick = function() {
        statsmodal.style.display = "none";
    }

    spanM.onclick = function() {
        movesmodal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == statsmodal) {
            statsmodal.style.display = "none";
        }
        else if (event.target == movesmodal) {
            movesmodal.style.display = "none";
        }
    }
}