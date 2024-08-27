# game_logic.py

from enum import Enum
from typing import List, Tuple, Dict, Optional

class CharacterType(Enum):
    PAWN = "P"
    HERO1 = "H1"
    HERO2 = "H2"

class Direction(Enum):
    LEFT = "L"
    RIGHT = "R"
    FORWARD = "F"
    BACKWARD = "B"
    FORWARD_LEFT = "FL"
    FORWARD_RIGHT = "FR"
    BACKWARD_LEFT = "BL"
    BACKWARD_RIGHT = "BR"

class Character:
    def __init__(self, name: str, char_type: CharacterType, player: str):
        self.name = name
        self.type = char_type
        self.player = player

    def __str__(self):
        return f"{self.player}-{self.name}"

class GameState:
    def __init__(self):
        self.board: List[List[Optional[Character]]] = [[None for _ in range(5)] for _ in range(5)]
        self.players: List[str] = ['A', 'B']
        self.current_player: str = 'A'
        self.characters: Dict[str, Character] = {}

    def initialize_game(self, setup_a: List[str], setup_b: List[str]):
        for i, char in enumerate(setup_a):
            char_type = CharacterType.PAWN if char.startswith('P') else (CharacterType.HERO1 if char.startswith('H1') else CharacterType.HERO2)
            character = Character(char, char_type, 'A')
            self.board[0][i] = character
            self.characters[f'A-{char}'] = character

        for i, char in enumerate(setup_b):
            char_type = CharacterType.PAWN if char.startswith('P') else (CharacterType.HERO1 if char.startswith('H1') else CharacterType.HERO2)
            character = Character(char, char_type, 'B')
            self.board[4][i] = character
            self.characters[f'B-{char}'] = character

    def get_character_position(self, character: Character) -> Tuple[int, int]:
        for i, row in enumerate(self.board):
            for j, cell in enumerate(row):
                if cell == character:
                    return i, j
        return -1, -1

    def is_valid_move(self, character: Character, direction: Direction) -> bool:
        row, col = self.get_character_position(character)
        if row == -1 or col == -1:
            return False

        new_row, new_col = row, col

        if character.type == CharacterType.PAWN:
            if direction == Direction.LEFT:
                new_col -= 1
            elif direction == Direction.RIGHT:
                new_col += 1
            elif direction == Direction.FORWARD:
                new_row += 1 if character.player == 'A' else -1
            elif direction == Direction.BACKWARD:
                new_row -= 1 if character.player == 'A' else 1
        elif character.type == CharacterType.HERO1:
            if direction == Direction.LEFT:
                new_col -= 2
            elif direction == Direction.RIGHT:
                new_col += 2
            elif direction == Direction.FORWARD:
                new_row += 2 if character.player == 'A' else -2
            elif direction == Direction.BACKWARD:
                new_row -= 2 if character.player == 'A' else 2
        elif character.type == CharacterType.HERO2:
            if direction == Direction.FORWARD_LEFT:
                new_row += 2 if character.player == 'A' else -2
                new_col -= 2
            elif direction == Direction.FORWARD_RIGHT:
                new_row += 2 if character.player == 'A' else -2
                new_col += 2
            elif direction == Direction.BACKWARD_LEFT:
                new_row -= 2 if character.player == 'A' else 2
                new_col -= 2
            elif direction == Direction.BACKWARD_RIGHT:
                new_row -= 2 if character.player == 'A' else 2
                new_col += 2

        # Check if the new position is within the board
        if not (0 <= new_row < 5 and 0 <= new_col < 5):
            return False

        # Check if the new position is occupied by a friendly character
        if self.board[new_row][new_col] and self.board[new_row][new_col].player == character.player:
            return False

        return True

    def make_move(self, character: Character, direction: Direction) -> bool:
        if not self.is_valid_move(character, direction):
            return False

        old_row, old_col = self.get_character_position(character)
        new_row, new_col = old_row, old_col

        # Calculate new position based on character type and direction
        if character.type == CharacterType.PAWN:
            if direction == Direction.LEFT:
                new_col -= 1
            elif direction == Direction.RIGHT:
                new_col += 1
            elif direction == Direction.FORWARD:
                new_row += 1 if character.player == 'A' else -1
            elif direction == Direction.BACKWARD:
                new_row -= 1 if character.player == 'A' else 1
        elif character.type == CharacterType.HERO1:
            if direction == Direction.LEFT:
                new_col -= 2
            elif direction == Direction.RIGHT:
                new_col += 2
            elif direction == Direction.FORWARD:
                new_row += 2 if character.player == 'A' else -2
            elif direction == Direction.BACKWARD:
                new_row -= 2 if character.player == 'A' else 2
        elif character.type == CharacterType.HERO2:
            if direction == Direction.FORWARD_LEFT:
                new_row += 2 if character.player == 'A' else -2
                new_col -= 2
            elif direction == Direction.FORWARD_RIGHT:
                new_row += 2 if character.player == 'A' else -2
                new_col += 2
            elif direction == Direction.BACKWARD_LEFT:
                new_row -= 2 if character.player == 'A' else 2
                new_col -= 2
            elif direction == Direction.BACKWARD_RIGHT:
                new_row -= 2 if character.player == 'A' else 2
                new_col += 2

        # Remove any opponent's character at the new position
        if self.board[new_row][new_col]:
            del self.characters[f"{self.board[new_row][new_col].player}-{self.board[new_row][new_col].name}"]

        # Update the board
        self.board[old_row][old_col] = None
        self.board[new_row][new_col] = character

        return True

    def switch_turn(self):
        self.current_player = 'B' if self.current_player == 'A' else 'A'

    def is_game_over(self) -> Optional[str]:
        players_characters = {'A': 0, 'B': 0}
        for row in self.board:
            for cell in row:
                if cell:
                    players_characters[cell.player] += 1
        
        if players_characters['A'] == 0:
            return 'B'
        elif players_characters['B'] == 0:
            return 'A'
        else:
            return None

    def get_board_state(self) -> List[List[str]]:
        return [[str(char) if char else '' for char in row] for row in self.board]

def create_game() -> GameState:
    return GameState()

def process_move(game: GameState, player: str, move: str) -> Tuple[bool, str]:
    if game.current_player != player:
        return False, "Not your turn"

    char_name, direction = move.split(':')
    character = game.characters.get(f"{player}-{char_name}")
    if not character:
        return False, "Invalid character"

    try:
        direction_enum = Direction(direction)
    except ValueError:
        return False, "Invalid direction"

    if game.make_move(character, direction_enum):
        game.switch_turn()
        winner = game.is_game_over()
        if winner:
            return True, f"Game over. Player {winner} wins!"
        return True, "Move successful"
    else:
        return False, "Invalid move"