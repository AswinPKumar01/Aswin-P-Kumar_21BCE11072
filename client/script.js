let socket;
let gameId;
let player;
let currentTurn;

const gameBoard = document.getElementById('game-board');
const messageDisplay = document.getElementById('message');
const createGameBtn = document.getElementById('create-game');
const joinGameBtn = document.getElementById('join-game');
const startGameBtn = document.getElementById('submit-setup');
const gameIdInput = document.getElementById('game-id');
const setupForm = document.getElementById('setup-form');

createGameBtn.addEventListener('click', createGame);
joinGameBtn.addEventListener('click', joinGame);
startGameBtn.addEventListener('click', startGame);

function createGame() {
    gameId = Math.random().toString(36).substr(2, 6);
    gameIdInput.value = gameId;
    connectToGame('create');
}

function joinGame() {
    gameId = gameIdInput.value;
    if (gameId) {
        connectToGame('join');
    } else {
        setMessage('Please enter a game ID');
    }
}

const characterOptions = ['P1', 'P2', 'P3', 'P4', 'P5', 'H1', 'H2'];

function populateSetupForm() {
    const selects = document.querySelectorAll('#setup-form select');
    selects.forEach(select => {
        characterOptions.forEach(option => {
            const opt = document.createElement('option');
            opt.value = option;
            opt.textContent = option;
            select.appendChild(opt);
        });
    });
}

function showSetupForm() {
    setupForm.style.display = 'block';
    populateSetupForm();
}

startGameBtn.addEventListener('click', startGame);

function startGame() {
    const setupA = Array.from(document.querySelectorAll('#player-a-setup select')).map(select => select.value);
    const setupB = Array.from(document.querySelectorAll('#player-b-setup select')).map(select => select.value);
    
    if (isValidSetup(setupA) && isValidSetup(setupB)) {
        socket.send(JSON.stringify({
            type: 'initialize_game',
            game_id: gameId,
            setupA: setupA,
            setupB: setupB
        }));
        setupForm.style.display = 'none';
    } else {
        setMessage('Invalid setup. Please ensure you have selected 5 unique characters.', 'error');
    }
}

function isValidSetup(setup) {
    return setup.length === 5 && new Set(setup).size === 5;
}

function onConnectionEstablished() {
    showSetupForm();
}

function connectToGame(action) {
    socket = new WebSocket(`ws://${window.location.host}/ws/${gameId}`);
    socket.onopen = () => {
        setMessage(`Connected to game ${gameId}`);
        if (action === 'create') {
            socket.send(JSON.stringify({ type: 'create_game', game_id: gameId }));
        } else if (action === 'join') {
            socket.send(JSON.stringify({ type: 'join_game', game_id: gameId }));
        }
        onConnectionEstablished();
    };
}

function handleMessage(event) {
    try {
        const data = JSON.parse(event.data);
        switch (data.type) {
            case 'game_created':
                setMessage(`Game created: ${data.game_id}`);
                break;
            case 'player_assigned':
                player = data.player;
                setMessage(`You are Player ${player}`);
                setupForm.style.display = 'block';
                break;
            case 'game_initialized':
                renderBoard(data.board);
                currentTurn = data.current_player;
                updateTurnDisplay();
                break;
            case 'move_made':
                renderBoard(data.board);
                currentTurn = data.current_player;
                updateTurnDisplay();
                break;
            case 'error':
                setMessage(`Error: ${data.message}`);
                break;
            default:
                console.warn('Unhandled message type:', data.type);
        }
    } catch (error) {
        console.error('Error parsing message:', error);
    }
}
function renderBoard(board) {
    gameBoard.innerHTML = '';
    for (let row = 0; row < 5; row++) {
        for (let col = 0; col < 5; col++) {
            const cell = document.createElement('div');
            cell.className = 'cell';
            cell.dataset.row = row;
            cell.dataset.col = col;
            if (board[row][col]) {
                const [piecePlayer, pieceName] = board[row][col].split('-');
                cell.textContent = pieceName;
                cell.classList.add(`player-${piecePlayer}`);
            }
            cell.addEventListener('click', () => selectCell(row, col));
            gameBoard.appendChild(cell);
        }
    }
}

function selectCell(row, col) {
    if (currentTurn !== player) {
        setMessage("It's not your turn");
        return;
    }

    const selectedPiece = document.querySelector('.selected');
    const clickedCell = gameBoard.children[row * 5 + col];

    if (selectedPiece) {
        if (clickedCell.classList.contains('valid-move')) {
            makeMove(selectedPiece, row, col);
        } else {
            clearHighlights();
        }
    } else if (clickedCell.classList.contains(`player-${player}`)) {
        clickedCell.classList.add('selected');
        highlightValidMoves(row, col);
    }
}

function highlightValidMoves(row, col) {
    clearHighlights();
    const piece = gameBoard.children[row * 5 + col].textContent;
    const validMoves = getValidMoves(piece, row, col);
    validMoves.forEach(move => {
        const cell = gameBoard.children[move.row * 5 + move.col];
        cell.classList.add('valid-move');
    });
}

function getValidMoves(piece, row, col) {
    const moves = [];
    const direction = player === 'A' ? 1 : -1;

    switch (piece[0]) {
        case 'P':
            addMoveIfValid(moves, row + direction, col);
            addMoveIfValid(moves, row, col - 1);
            addMoveIfValid(moves, row, col + 1);
            addMoveIfValid(moves, row - direction, col);
            break;
        case 'H':
            if (piece[1] === '1') { 
                addMoveIfValid(moves, row + 2 * direction, col);
                addMoveIfValid(moves, row - 2 * direction, col);
                addMoveIfValid(moves, row, col - 2);
                addMoveIfValid(moves, row, col + 2);
            } else if (piece[1] === '2') {
                addMoveIfValid(moves, row + 2 * direction, col + 2);
                addMoveIfValid(moves, row + 2 * direction, col - 2);
                addMoveIfValid(moves, row - 2 * direction, col + 2);
                addMoveIfValid(moves, row - 2 * direction, col - 2);
            }
            break;
    }
    return moves;
}

function addMoveIfValid(moves, row, col) {
    if (row >= 0 && row < 5 && col >= 0 && col < 5) {
        const cell = gameBoard.children[row * 5 + col];
        if (!cell.classList.contains(`player-${player}`)) {
            moves.push({ row, col });
        }
    }
}

function makeMove(fromCell, toRow, toCol) {
    const fromRow = parseInt(fromCell.dataset.row);
    const fromCol = parseInt(fromCell.dataset.col);
    const piece = fromCell.textContent;
    const move = `${piece}:${getMoveDirection(fromRow, fromCol, toRow, toCol)}`;

    socket.send(JSON.stringify({
        type: 'make_move',
        game_id: gameId,
        player: player,
        move: move
    }));

    clearHighlights();
}

function getMoveDirection(fromRow, fromCol, toRow, toCol) {
    const rowDiff = toRow - fromRow;
    const colDiff = toCol - fromCol;

    if (rowDiff === 0) {
        return colDiff > 0 ? 'R' : 'L';
    } else if (colDiff === 0) {
        return rowDiff > 0 ? 'F' : 'B';
    } else {

        const vertical = rowDiff > 0 ? 'F' : 'B';
        const horizontal = colDiff > 0 ? 'R' : 'L';
        return vertical + horizontal;
    }
}

function clearHighlights() {
    document.querySelectorAll('.selected, .valid-move').forEach(cell => {
        cell.classList.remove('selected', 'valid-move');
    });
}

function updateTurnDisplay() {
    setMessage(`Current turn: Player ${currentTurn}`);
}

function setMessage(message) {
    messageDisplay.textContent = message;
}

// Initialize the game
document.addEventListener('DOMContentLoaded', () => {
    setupForm.style.display = 'none';
});