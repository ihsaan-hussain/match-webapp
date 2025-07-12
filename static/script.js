let homePlayers = [];
let awayPlayers = [];

function addPlayer(team) {
    const name = prompt("Name:");
    const goals = prompt("Goals:");
    const assists = prompt("Assists:");
    const player = { name, goals, assists };

    if (team === 'home') {
        homePlayers.push(player);
        updatePlayerList('home', homePlayers);
    } else {
        awayPlayers.push(player);
        updatePlayerList('away', awayPlayers);
    }
    updateHiddenInputs();
}

function updatePlayerList(team, players) {
    const section = document.getElementById(`${team}-players-section`);
    section.innerHTML = '';
    players.forEach(p => {
        const el = document.createElement('p');
        el.innerText = `${p.name} - Goals: ${p.goals}, Assists: ${p.assists}`;
        section.appendChild(el);
    });
}

function updateHiddenInputs() {
    document.querySelector('input[name=home_players_json]').value = JSON.stringify(homePlayers);
    document.querySelector('input[name=away_players_json]').value = JSON.stringify(awayPlayers);
}