# Ort: games/views.py

import random
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Highscore # NEU: Wir importieren unser Highscore-Modell

# --- game_list und guess_the_number bleiben unverändert ---
def game_list(request):
    games = [
        {'name': 'Zahlen Raten', 'description': 'Ein klassisches Ratespiel.', 'url_name': 'games:guess_the_number'},
        {'name': 'Tic-Tac-Toe', 'description': 'Der unsterbliche Klassiker.', 'url_name': 'games:tic_tac_toe'},
    ]
    return render(request, 'games/game_list.html', {'games': games})

def guess_the_number(request):
    # ... (Code von vorher bleibt hier unverändert) ...
    if 'secret_number' not in request.session or request.GET.get('reset') == 'true':
        request.session['secret_number'] = random.randint(1, 100)
        request.session['attempts'] = 0
        request.session['message'] = "Ich habe mir eine Zahl zwischen 1 und 100 ausgedacht. Rate mal!"
    message = request.session.get('message', '')
    if request.method == 'POST':
        try:
            guess = int(request.POST.get('guess', 0))
            request.session['attempts'] += 1
            attempts = request.session['attempts']
            secret_number = request.session['secret_number']
            if guess < secret_number:
                message = f"Deine Zahl {guess} ist zu niedrig! Versuch's nochmal."
            elif guess > secret_number:
                message = f"Deine Zahl {guess} ist zu hoch! Versuch's nochmal."
            else:
                message = f"🎉 Richtig! Die Zahl war {secret_number}! Du hast {attempts} Versuche gebraucht. 🎉"
                del request.session['secret_number']
        except (ValueError, TypeError):
            message = "Das war keine gültige Zahl! Bitte gib eine Zahl zwischen 1 und 100 ein."
    request.session['message'] = message
    context = {'message': message}
    return render(request, 'games/guess_the_number.html', context)


# --- TIC-TAC-TOE LOGIK MIT HIGHSCORE-FUNKTION ---
def tic_tac_toe(request):

    def check_winner(board):
        for i in range(3):
            if board[i][0] == board[i][1] == board[i][2] != '': return board[i][0]
            if board[0][i] == board[1][i] == board[2][i] != '': return board[0][i]
        if board[0][0] == board[1][1] == board[2][2] != '': return board[0][0]
        if board[0][2] == board[1][1] == board[2][0] != '': return board[0][2]
        if all(all(cell != '' for cell in row) for row in board): return 'draw'
        return None

    def get_empty_cells(board):
        return [(r, c) for r in range(3) for c in range(3) if board[r][c] == '']

    def computer_move(board, difficulty):
        # ... (KI-Logik bleibt unverändert) ...
        if difficulty == 'easy':
            empty_cells = get_empty_cells(board)
            if empty_cells:
                r, c = random.choice(empty_cells)
                board[r][c] = 'O'
            return
        for r, c in get_empty_cells(board):
            board[r][c] = 'O'
            if check_winner(board) == 'O': return
            board[r][c] = ''
        for r, c in get_empty_cells(board):
            board[r][c] = 'X'
            if check_winner(board) == 'X':
                board[r][c] = 'O'
                return
            board[r][c] = ''
        if difficulty == 'medium':
            empty_cells = get_empty_cells(board)
            if empty_cells:
                r, c = random.choice(empty_cells)
                board[r][c] = 'O'
            return
        if difficulty == 'hard':
            if board[1][1] == '':
                board[1][1] = 'O'
                return
            corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
            random.shuffle(corners)
            for r, c in corners:
                if board[r][c] == '':
                    board[r][c] = 'O'
                    return
            empty_cells = get_empty_cells(board)
            if empty_cells:
                r, c = random.choice(empty_cells)
                board[r][c] = 'O'

    # NEU: Highscore speichern, wenn der Name gesendet wird
    if request.method == 'POST' and 'player_name' in request.POST:
        name = request.POST.get('player_name', 'Anonym')
        difficulty = request.session.get('ttt_difficulty', 'unknown')
        Highscore.objects.create(player_name=name, difficulty=difficulty)
        # Spiel nach dem Speichern zurücksetzen
        for key in ['ttt_board', 'ttt_difficulty', 'ttt_message']:
            if key in request.session: del request.session[key]
        return redirect(reverse('games:highscores'))

    if request.method == 'POST' and 'difficulty' in request.POST:
        difficulty = request.POST.get('difficulty')
        request.session['ttt_difficulty'] = difficulty
        request.session['ttt_board'] = [['', '', ''], ['', '', ''], ['', '', '']]
        request.session['ttt_message'] = f"Du bist Spieler X. Schwierigkeit: {difficulty}. Mach deinen Zug!"
        return redirect(reverse('games:tic_tac_toe'))

    if request.GET.get('reset') == 'true':
        for key in ['ttt_board', 'ttt_difficulty', 'ttt_message']:
            if key in request.session: del request.session[key]
        return redirect(reverse('games:tic_tac_toe'))
        
    if 'ttt_difficulty' not in request.session:
        return render(request, 'games/tic_tac_toe.html')

    board = request.session['ttt_board']
    message = request.session['ttt_message']
    difficulty = request.session['ttt_difficulty']

    if request.method == 'POST' and 'move' in request.POST:
        if not check_winner(board):
            try:
                row, col = map(int, request.POST.get('move').split(','))
                if board[row][col] == '':
                    board[row][col] = 'X'
                    if not check_winner(board):
                        computer_move(board, difficulty)
                    winner = check_winner(board)
                    if winner:
                        if winner == 'draw': message = "Unentschieden!"
                        elif winner == 'X': message = "🎉 Du hast gewonnen! 🎉 Gib deinen Namen für die Highscore-Liste ein!"
                        else: message = "Der Computer hat gewonnen!"
                    else:
                        message = "Du bist wieder am Zug."
            except (ValueError, IndexError):
                message = "Ungültiger Zug!"
    
    request.session['ttt_board'] = board
    request.session['ttt_message'] = message

    context = {
        'board': board,
        'message': message,
        'winner': check_winner(board)
    }
    return render(request, 'games/tic_tac_toe.html', context)


# NEU: Eine komplett neue Funktion für die Highscore-Seite
def highscore_list(request):
    # Hole alle Einträge aus der Datenbank, sortiert nach Datum (neueste zuerst)
    scores = Highscore.objects.order_by('-date_achieved')
    context = {
        'scores': scores
    }
    return render(request, 'games/highscores.html', context)