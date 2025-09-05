document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elemente ---
    const boardElement = document.getElementById('board-tic-tac-toe');
    const cells = document.querySelectorAll('.cell-tic-tac-toe');
    const difficultySelect = document.getElementById('difficulty');
    const startGameBtn = document.getElementById('startGameBtn');
    const modal = document.getElementById('gameOverModal');
    const modalTitle = document.getElementById('modalTitle');
    const finalScoreEl = document.getElementById('finalScore');
    const playerNameInput = document.getElementById('playerNameInput');
    const saveScoreBtn = document.getElementById('saveScoreBtn');
    const restartGameBtn = document.getElementById('restartGameBtn');
    const closeModalBtn = document.getElementById('closeModalBtn');

    // --- Spiel-Variablen ---
    let board;
    const player = 'X';
    const ai = 'O';
    let gameActive;
    let score;

    const winningCombos = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ];
    
    // Initialisiert das Board, startet das Spiel aber nicht.
    function init() {
        board = Array.from(Array(9).keys());
        gameActive = false;
        score = 0;
        modal.style.display = 'none';
        cells.forEach(cell => {
            cell.classList.remove(player, ai);
            cell.removeEventListener('click', handleCellClick);
        });
        startGameBtn.disabled = false;
        difficultySelect.disabled = false;
    }

    function startGame() {
        init(); // Setzt das Spiel zurück
        gameActive = true;
        cells.forEach(cell => {
            cell.addEventListener('click', handleCellClick, { once: true });
        });
        startGameBtn.disabled = true;
        difficultySelect.disabled = true;
    }

    function handleCellClick(e) {
        if (!gameActive) return;
        const cellId = e.target.id;
        // Nur Züge in leeren Feldern erlauben
        if (typeof board[cellId] == 'number') {
            turn(cellId, player);
            if (!checkWin(board, player) && !checkTie()) {
                setTimeout(() => makeAIMove(), 500);
            }
        }
    }

    function turn(cellId, currentPlayer) {
        board[cellId] = currentPlayer;
        document.getElementById(cellId).classList.add(currentPlayer);
        document.getElementById(cellId).removeEventListener('click', handleCellClick);
        let gameWon = checkWin(board, currentPlayer);
        if (gameWon) gameOver(gameWon);
        checkTie();
    }

    function checkWin(currentBoard, currentPlayer) {
        let plays = currentBoard.reduce((a, e, i) => (e === currentPlayer) ? a.concat(i) : a, []);
        for (let [index, win] of winningCombos.entries()) {
            if (win.every(elem => plays.indexOf(elem) > -1)) {
                return { index: index, player: currentPlayer };
            }
        }
        return null;
    }

    function checkTie() {
        if (getEmptyCells(board).length === 0 && !checkWin(board, player) && !checkWin(board, ai)) {
            gameOver({ player: 'Tie' });
            return true;
        }
        return false;
    }

    function getEmptyCells(currentBoard) {
        return currentBoard.filter(c => typeof c == 'number');
    }

    function gameOver(gameWon) {
        gameActive = false;
        startGameBtn.disabled = false;
        difficultySelect.disabled = false;

        const difficulty = difficultySelect.value;
        if (gameWon.player === player) {
            modalTitle.textContent = 'Gewonnen!';
            if (difficulty === 'easy') score = 50;
            if (difficulty === 'medium') score = 100;
        } else if (gameWon.player === ai) {
            modalTitle.textContent = 'Verloren!';
            score = 0;
        } else {
            modalTitle.textContent = 'Unentschieden!';
            if (difficulty === 'hard') score = 250;
        }

        finalScoreEl.textContent = score;
        modal.style.display = 'flex';
    }

    // --- KI Logik ---
    function makeAIMove() {
        if (!gameActive) return;
        const difficulty = difficultySelect.value;
        let move;

        if (difficulty === 'easy') {
            const emptyCells = getEmptyCells(board);
            move = emptyCells[Math.floor(Math.random() * emptyCells.length)];
        } else if (difficulty === 'medium') {
            move = mediumAI();
        } else { // hard
            move = minimax(board, ai).index;
        }
        turn(move, ai);
    }

    function mediumAI() {
        for (let i of getEmptyCells(board)) {
            let boardCopy = [...board]; boardCopy[i] = ai;
            if (checkWin(boardCopy, ai)) return i;
        }
        for (let i of getEmptyCells(board)) {
            let boardCopy = [...board]; boardCopy[i] = player;
            if (checkWin(boardCopy, player)) return i;
        }
        const emptyCells = getEmptyCells(board);
        return emptyCells[Math.floor(Math.random() * emptyCells.length)];
    }

    function minimax(newBoard, currentPlayer) {
        const availSpots = getEmptyCells(newBoard);

        if (checkWin(newBoard, player)) return { score: -10 };
        if (checkWin(newBoard, ai)) return { score: 10 };
        if (availSpots.length === 0) return { score: 0 };

        let moves = [];
        for (let i = 0; i < availSpots.length; i++) {
            let move = {};
            move.index = newBoard[availSpots[i]];
            newBoard[availSpots[i]] = currentPlayer;

            if (currentPlayer == ai) {
                move.score = minimax(newBoard, player).score;
            } else {
                move.score = minimax(newBoard, ai).score;
            }
            newBoard[availSpots[i]] = move.index;
            moves.push(move);
        }

        let bestMove;
        if (currentPlayer === ai) {
            let bestScore = -10000;
            for (let i = 0; i < moves.length; i++) {
                if (moves[i].score > bestScore) {
                    bestScore = moves[i].score;
                    bestMove = i;
                }
            }
        } else {
            let bestScore = 10000;
            for (let i = 0; i < moves.length; i++) {
                if (moves[i].score < bestScore) {
                    bestScore = moves[i].score;
                    bestMove = i;
                }
            }
        }
        return moves[bestMove];
    }
    
    // --- Event Listeners ---
    startGameBtn.addEventListener('click', startGame);
    restartGameBtn.addEventListener('click', startGame);
    closeModalBtn.addEventListener('click', () => {
        modal.style.display = 'none';
        init(); // Spiel zurücksetzen, wenn Modal geschlossen wird
    });
    
    saveScoreBtn.addEventListener('click', () => {
        const playerName = playerNameInput.value.trim() || 'ANONYM';
        if (score > 0) {
             fetch("{% url 'games:save_score' %}", {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': '{{ csrf_token }}' },
                body: JSON.stringify({ player_name: playerName, game: 'Tic-Tac-Toe', score: score })
            })
            .then(res => res.json())
            .then(data => { if(data.status === 'success') window.location.href = "{% url 'games:highscores' %}"; });
        }
    });

    init(); // Board initial zeichnen, aber Spiel nicht starten
});