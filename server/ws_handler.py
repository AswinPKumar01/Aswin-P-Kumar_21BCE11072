from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict
import json
import logging
from game_logic import GameState, create_game, process_move

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, game_id: str):
        await websocket.accept()
        if game_id not in self.active_connections:
            self.active_connections[game_id] = []
        self.active_connections[game_id].append(websocket)
        logger.info(f"New connection added to game {game_id}. Total connections: {len(self.active_connections[game_id])}")

    def disconnect(self, websocket: WebSocket, game_id: str):
        self.active_connections[game_id].remove(websocket)
        if not self.active_connections[game_id]:
            del self.active_connections[game_id]
        logger.info(f"Connection removed from game {game_id}. Remaining connections: {len(self.active_connections.get(game_id, []))}")

    async def broadcast(self, message: str, game_id: str):
        if game_id in self.active_connections:
            for connection in self.active_connections[game_id]:
                await connection.send_text(message)

class GameManager:
    def __init__(self):
        self.games: Dict[str, GameState] = {}
        self.player_assignments: Dict[str, Dict[WebSocket, str]] = {}

    def create_game(self, game_id: str) -> bool:
        if game_id not in self.games:
            self.games[game_id] = create_game()
            self.player_assignments[game_id] = {}
            logger.info(f"Game created: {game_id}. Total games: {len(self.games)}")
            return True
        return False

    def get_game(self, game_id: str) -> GameState:
        return self.games.get(game_id)

    def remove_game(self, game_id: str):
        if game_id in self.games:
            del self.games[game_id]
            del self.player_assignments[game_id]
            logger.info(f"Game removed: {game_id}. Remaining games: {len(self.games)}")

    def assign_player(self, game_id: str, websocket: WebSocket) -> str:
        if game_id not in self.player_assignments:
            self.player_assignments[game_id] = {}

        if len(self.player_assignments[game_id]) == 0:
            player = 'A'
        elif len(self.player_assignments[game_id]) == 1:
            player = 'B'
        else:
            player = 'spectator'

        self.player_assignments[game_id][websocket] = player
        return player

    def get_player(self, game_id: str, websocket: WebSocket) -> str:
        return self.player_assignments.get(game_id, {}).get(websocket, 'unknown')

connection_manager = ConnectionManager()
game_manager = GameManager()

async def handle_websocket(websocket: WebSocket, game_id: str):
    await connection_manager.connect(websocket, game_id)
    try:
        while True:
            data = await websocket.receive_text()
            await process_message(websocket, game_id, data)
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, game_id)
        player = game_manager.get_player(game_id, websocket)
        await connection_manager.broadcast(
            json.dumps({"type": "player_disconnected", "game_id": game_id, "player": player}),
            game_id
        )
    except Exception as e:
        logger.error(f"Unexpected error in game {game_id}: {str(e)}")
        await websocket.send_json({"type": "error", "message": "An unexpected error occurred"})

async def process_message(websocket: WebSocket, game_id: str, data: str):
    try:
        message = json.loads(data)
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON received: {data}")
        await websocket.send_json({"type": "error", "message": "Invalid JSON"})
        return

    if message['type'] == 'create_game':
        if game_manager.create_game(game_id):
            player = game_manager.assign_player(game_id, websocket)
            await websocket.send_json({"type": "game_created", "game_id": game_id})
            await websocket.send_json({"type": "player_assigned", "player": player})
        else:
            await websocket.send_json({"type": "error", "message": "Game already exists"})

    elif message['type'] == 'join_game':
        if game_id in game_manager.games:
            player = game_manager.assign_player(game_id, websocket)
            await websocket.send_json({"type": "player_assigned", "player": player})
        else:
            await websocket.send_json({"type": "error", "message": "Game not found"})

    elif message['type'] == 'initialize_game':
        game = game_manager.get_game(game_id)
        if game:
            try:
                game.initialize_game(message['setupA'], message['setupB'])
                await connection_manager.broadcast(
                    json.dumps({
                        "type": "game_initialized",
                        "game_id": game_id,
                        "board": game.get_board_state(),
                        "current_player": game.current_player
                    }),
                    game_id
                )
            except Exception as e:
                await websocket.send_json({"type": "error", "message": f"Error initializing game: {str(e)}"})
        else:
            await websocket.send_json({"type": "error", "message": "Game not found"})

    elif message['type'] == 'make_move':
        game = game_manager.get_game(game_id)
        if game:
            player = game_manager.get_player(game_id, websocket)
            if player == game.current_player:
                success, result = process_move(game, player, message['move'])
                if success:
                    await connection_manager.broadcast(
                        json.dumps({
                            "type": "move_made",
                            "game_id": game_id,
                            "board": game.get_board_state(),
                            "current_player": game.current_player,
                            "move": message['move']
                        }),
                        game_id
                    )
                else:
                    await websocket.send_json({"type": "error", "message": result})
            else:
                await websocket.send_json({"type": "error", "message": "It's not your turn"})
        else:
            await websocket.send_json({"type": "error", "message": "Game not found"})