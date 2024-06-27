let currentSessionId;
let currentGameState;
const storyElement = document.getElementById('story');
const choicesElement = document.getElementById('choices');
const characterInfoElement = document.getElementById('character-info');
const inventoryElement = document.getElementById('inventory');
const currentSceneElement = document.getElementById('current-scene');

document.addEventListener('DOMContentLoaded', fetchSavedGames);

async function fetchSavedGames() {
    try {
        const response = await fetch('/saved-games');
        const savedGames = await response.json();
        const sessionSelect = document.getElementById('session-select');
        savedGames.forEach(game => {
            const option = document.createElement('option');
            option.value = game.id;
            option.textContent = `${game.player_name} - ${new Date(game.created_at).toLocaleString()}`;
            sessionSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error fetching saved games:', error);
    }
}

async function startNewGame() {
    const playerName = document.getElementById('player-name').value;
    const characterClass = document.getElementById('character-class').value;
    if (!playerName) {
        alert('Please enter your name');
        return;
    }
    
    try {
        const response = await fetch('/start-game', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ playerName, characterClass })
        });
        const data = await response.json();
        currentSessionId = data.sessionId;
        currentGameState = data.gameState;
        document.getElementById('current-session-id').textContent = currentSessionId;
        
        switchToGameScreen();
        updateGameDisplay();
        await takeAction('start the game');
    } catch (error) {
        console.error('Error starting new game:', error);
        alert('Failed to start new game. Please try again.');
    }
}

async function loadGame() {
    const sessionId = document.getElementById('session-select').value;
    if (!sessionId) {
        alert('Please select a saved game');
        return;
    }
    
    try {
        const response = await fetch(`/load-game/${sessionId}`);
        if (response.ok) {
            currentSessionId = sessionId;
            currentGameState = await response.json();
            document.getElementById('current-session-id').textContent = currentSessionId;
            
            switchToGameScreen();
            updateGameDisplay();
            await takeAction('continue the game');
        } else {
            alert('Failed to load game. Please try again.');
        }
    } catch (error) {
        console.error('Error loading game:', error);
        alert('Failed to load game. Please try again.');
    }
}

function switchToGameScreen() {
    document.getElementById('start-screen').classList.remove('active');
    document.getElementById('game-screen').classList.add('active');
}

function updateGameDisplay() {
    updateCharacterInfo();
    updateInventory();
    currentSceneElement.textContent = currentGameState.currentScene;
}

function updateCharacterInfo() {
    if (currentGameState && currentGameState.character) {
        const character = currentGameState.character;
        characterInfoElement.innerHTML = `
            <h2>${character.name} the ${character.className}</h2>
            <p>Level: ${character.level}</p>
            <p>Health: ${character.health}/${character.maxHealth}</p>
            <p>Strength: ${character.strength}</p>
            <p>Dexterity: ${character.dexterity}</p>
            <p>Intelligence: ${character.intelligence}</p>
        `;
    }
}

function updateInventory() {
    const inventoryElement = document.getElementById('inventory');
    inventoryElement.innerHTML = '<h3>Inventory:</h3>';
    const inventoryList = document.createElement('ul');
    for (const [item, quantity] of Object.entries(currentGameState.character.inventory)) {
        const listItem = document.createElement('li');
        listItem.textContent = `${item}: ${quantity}`;
        inventoryList.appendChild(listItem);
    }
    inventoryElement.appendChild(inventoryList);
}

async function useItem(item) {
    try {
        const response = await fetch('/use-item', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sessionId: currentSessionId, item: item })
        });
        const data = await response.json();
        if (data.success) {
            alert(`You used the ${item}. ${data.effect}`);
            currentGameState = data.gameState;
            updateGameDisplay();
        } else {
            alert(`Failed to use ${item}. ${data.message}`);
        }
    } catch (error) {
        console.error('Error using item:', error);
        alert('Failed to use item. Please try again.');
    }
}

function displayChoices(choices) {
    choicesElement.innerHTML = '';
    choices.forEach(choice => {
        const choiceDiv = document.createElement('div');
        choiceDiv.className = 'choice';

        const choiceButton = document.createElement('button');
        choiceButton.textContent = choice.text;
        choiceButton.onclick = () => takeAction(choice.text);

        const effectsDiv = document.createElement('div');
        effectsDiv.className = 'effects';
        effectsDiv.innerHTML = `
            <p>Difficulty: ${choice.difficulty}</p>
            ${choice.effects.health ? `<p>Health: ${choice.effects.health > 0 ? '+' : ''}${choice.effects.health}</p>` : ''}
            ${Object.entries(choice.effects.stats || {}).map(([stat, value]) => `<p>${stat.charAt(0).toUpperCase() + stat.slice(1)}: ${value > 0 ? '+' : ''}${value}</p>`).join('')}
            ${choice.effects.inventory && choice.effects.inventory.add ? `<p>Gain: ${choice.effects.inventory.add.join(', ')}</p>` : ''}
            ${choice.effects.inventory && choice.effects.inventory.remove ? `<p>Lose: ${choice.effects.inventory.remove.join(', ')}</p>` : ''}
        `;

        choiceDiv.appendChild(choiceButton);
        choiceDiv.appendChild(effectsDiv);
        choicesElement.appendChild(choiceDiv);
    });
}

async function takeAction(action) {
    try {
        // Show loading message
        storyElement.textContent = 'Loading response...';
        choicesElement.innerHTML = '';

        const response = await fetch('/game', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sessionId: currentSessionId, action }),
        });

        const gameUpdate = await response.json();
        
        currentGameState = gameUpdate.gameState;
        
        updateGameDisplay();
        displayChoices(gameUpdate.choices);
        
        storyElement.textContent = gameUpdate.description;
    } catch (error) {
        console.error('Error:', error);
        storyElement.textContent = 'An error occurred. Please try again.';
    }
}