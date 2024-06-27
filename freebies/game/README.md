# Ollama Adventure

Ollama Adventure is an interactive, text-based role-playing game powered by the Ollama AI model. This game combines the classic choose-your-own-adventure format with dynamic character progression and AI-generated storytelling.

## Features

- AI-powered storytelling using Ollama
- Character creation with different classes
- Dynamic stat and inventory management
- Persistent game state using SQLite
- Interactive web-based user interface

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Node.js (v14 or higher)
- npm (usually comes with Node.js)
- Ollama installed and running on your system

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ollama-adventure.git
   cd ollama-adventure
   ```

2. Install the dependencies:
   ```
   npm install
   ```

3. Set up the database:
   ```
   node src/database.js
   ```

## Usage

1. Start the server:
   ```
   npm start
   ```

2. Open a web browser and navigate to `http://localhost:3000`

3. Create a new character or load an existing game using a session ID

4. Follow the prompts and make choices to progress through the adventure

## Game Mechanics

- **Character Creation**: Choose a name and class for your character
- **Stats**: Your character has health, strength, dexterity, and intelligence stats that can change during the game
- **Inventory**: Items can be added to or removed from your inventory as you play
- **Choices**: Each turn, you'll be presented with choices that affect the story and your character's development

## Project Structure

```
game/
├── public/
│   ├── index.html
│   └── styles/
│       └── main.css
├── src/
│   ├── server.js
│   ├── database.js
│   └── game/
│       ├── Character.js
│       └── gameState.js
└── package.json
```

## Customization

- Modify `src/game/Character.js` to add or change character attributes and methods
- Adjust the Ollama prompt in `src/server.js` to alter the AI's storytelling style or game mechanics
- Update `public/index.html` and `public/styles/main.css` to change the user interface

## Contributing

Contributions to Ollama Adventure are welcome! Here's how you can contribute:

1. Fork the repository
2. Create a new branch: `git checkout -b feature-branch-name`
3. Make your changes and commit them: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-branch-name`
5. Create a pull request

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgements

- [Ollama](https://ollama.ai/) for providing the AI model
- [Express.js](https://expressjs.com/) for the web server framework
- [SQLite](https://www.sqlite.org/) for the database

## Contact

If you have any questions or feedback, please open an issue on the GitHub repository.

Enjoy your adventure!