# Chess-like Game with WebSocket Communication

This project was developed as a task for the Software Development Profile at [Hitwicket](https://hitwicket.com/). 

Hitwicket is a cricket strategy game that combines elements of management and tactics. This chess-like game project demonstrates skills in real-time multiplayer game development, which are relevant to the kind of work done at Hitwicket.

## Project Overview
This project implements a turn-based, chess-like game played on a 5x5 grid. It features real-time multiplayer functionality using WebSockets, with a Python backend and a JavaScript frontend.

## Technology Stack
- Backend: Python with FastAPI
- Frontend: HTML, CSS, JavaScript
- Real-time Communication: WebSockets

## Project Structure
```
WS-Game/
├── server/
│   ├── main.py
│   ├── game_logic.py
│   └── ws_handler.py
└── client/
    ├── index.html
    ├── styles.css
    └── script.js
```

## Setup and Installation
1. Ensure Python 3.7+ is installed.
2. Install required Python packages:
   ```
   pip install fastapi uvicorn websockets
   ```
3. Navigate to the server directory and run:
   ```
   uvicorn main:app --reload
   ```
4. Open `index.html` in a web browser.

## Game Rules
- The game is played on a 5x5 grid.
- Each player controls 5 characters: 3 Pawns, 1 Hero1, and 1 Hero2.
- Characters have unique movement patterns:
  - Pawn: Moves one space in any direction.
  - Hero1: Moves two spaces straight in any direction.
  - Hero2: Moves two spaces diagonally in any direction.
- Players take turns moving one character per turn.
- A character is eliminated if an opponent's character moves to its space.

## Code Structure and Workflow

### Backend (`server/`)

#### `main.py`
- Sets up the FastAPI application.
- Defines the WebSocket endpoint for game communication.

#### `game_logic.py`
- Implements the `GameState` class, managing the game's core logic.
- Defines character types, movement rules, and board state.
- Handles move validation and execution.

#### `ws_handler.py`
- Manages WebSocket connections and game instances.
- Processes incoming messages and broadcasts game state updates.

### Frontend (`client/`)

#### `index.html`
- Provides the basic structure for the game interface.
- Includes controls for creating/joining games and the game board.

#### `styles.css`
- Defines the visual styling for the game interface.
- Styles the game board, cells, and character pieces.

#### `script.js`
- Handles client-side game logic and user interactions.
- Manages WebSocket communication with the server.
- Renders the game board and updates the UI based on game state.

## Workflow

1. Game Initialization:
   - A player creates a game, generating a unique game ID.
   - Another player joins using this game ID.
   - The server assigns roles (Player A and Player B) to the connected clients.

2. Game Setup:
   - Players arrange their characters on their respective starting rows.
   - The initial board state is sent to both players.

3. Gameplay:
   - Players take turns selecting a character and making a move.
   - The client sends the move to the server for validation.
   - If valid, the server updates the game state and broadcasts it to both players.
   - The UI updates to reflect the new board state.

4. Game Conclusion:
   - The game ends when all characters of one player are eliminated.
   - The server announces the winner and offers an option to start a new game.

## Future Enhancements
- Implement a more sophisticated UI with animations for moves.
- Add a chat feature for player communication.
- Introduce additional character types with unique abilities.
- Implement a ranking system for competitive play.
