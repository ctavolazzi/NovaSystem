import Character from './Character.js';

class GameState {
    constructor(sessionId, playerName, characterClass) {
        this.sessionId = sessionId;
        this.character = new Character(playerName, characterClass);
        this.currentScene = 'start';
        this.history = [];
    }

    updateScene(newScene) {
        this.currentScene = newScene;
        this.addToHistory(`Moved to ${newScene}`);
    }

    addToHistory(event) {
        this.history.push({
            timestamp: new Date().toISOString(),
            event: event
        });
    }

    toJSON() {
        return {
            sessionId: this.sessionId,
            character: this.character.toJSON(),
            currentScene: this.currentScene,
            history: this.history
        };
    }

    static fromJSON(json) {
        const gameState = new GameState(json.sessionId, json.character.name, json.character.className);
        gameState.currentScene = json.currentScene;
        gameState.history = json.history || [];
        gameState.character = Character.fromJSON(json.character);
        return gameState;
    }
}

export default GameState;