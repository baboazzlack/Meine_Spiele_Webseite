# Ort: games/views.py
import random
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Highscore
from collections import Counter

# --- game_list wurde aktualisiert ---
def game_list(request):
    games = [
        {'name': 'Zahlen Raten', 'description': 'Ein klassisches Ratespiel.', 'url_name': 'games:guess_the_number'},
        {'name': 'Tic-Tac-Toe', 'description': 'Der unsterbliche Klassiker.', 'url_name': 'games:tic_tac_toe'},
        {'name': 'Schere, Stein, Papier', 'description': 'Glück, Taktik oder beides?', 'url_name': 'games:rock_paper_scissors'},
    ]
    return render(request, 'games/game_list.html', {'games': games})

# --- guess_the_number bleibt unverändert ---
def guess_the_number(request):
    # ... alter Code ...
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

# --- tic_tac_toe wurde für Highscore angepasst ---
def tic_tac_toe(request):
    # ... fast der gesamte alte Code, nur eine kleine Änderung beim Speichern ...
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
    if request.method == 'POST' and 'player_name' in request.POST:
        name = request.POST.get('player_name', 'Anonym')
        difficulty = request.session.get('ttt_difficulty', 'unknown')
        # Highscore mit Score 1 speichern
        Highscore.objects.create(player_name=name, game="Tic-Tac-Toe", difficulty=difficulty, score=1)
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
    context = {'board': board, 'message': message, 'winner': check_winner(board)}
    return render(request, 'games/tic_tac_toe.html', context)

# --- highscore_list wurde aktualisiert ---
def highscore_list(request):
    scores = Highscore.objects.order_by('-score', '-date_achieved') # Sortiere nach Score, dann Datum
    context = {'scores': scores}
    return render(request, 'games/highscores.html', context)

# --- NEU: Die komplette Logik für Schere, Stein, Papier ---
def rock_paper_scissors(request):
    # Spiel zurücksetzen
    if request.GET.get('reset') == 'true':
        for key in ['rps_difficulty', 'rps_streak', 'rps_history', 'rps_message', 'rps_choices']:
            if key in request.session: del request.session[key]
        return redirect(reverse('games:rock_paper_scissors'))

    # Neues Spiel / Auswahl der Schwierigkeit
    if request.method == 'POST' and 'difficulty' in request.POST:
        difficulty = request.POST.get('difficulty')
        request.session['rps_difficulty'] = difficulty
        request.session['rps_streak'] = 0
        request.session['rps_history'] = []
        request.session['rps_message'] = f"Schwierigkeit: {difficulty}. Wähle dein Zeichen!"
        return redirect(reverse('games:rock_paper_scissors'))

    # Highscore speichern
    if request.method == 'POST' and 'player_name' in request.POST:
        name = request.POST.get('player_name', 'Anonym')
        difficulty = request.session.get('rps_difficulty', 'unknown')
        streak = request.session.get('rps_streak', 0)
        if streak > 0:
            Highscore.objects.create(player_name=name, game="Schere, Stein, Papier", difficulty=difficulty, score=streak)
        for key in ['rps_difficulty', 'rps_streak', 'rps_history', 'rps_message', 'rps_choices']:
            if key in request.session: del request.session[key]
        return redirect(reverse('games:highscores'))
        
    # Wenn kein Spiel läuft, zeige die Auswahl
    if 'rps_difficulty' not in request.session:
        return render(request, 'games/rock_paper_scissors.html')

    # Spiel läuft
    message = request.session.get('rps_message', '')
    streak = request.session.get('rps_streak', 0)
    choices = request.session.get('rps_choices', {})
    difficulty = request.session.get('rps_difficulty')
    history = request.session.get('rps_history', [])
    options = ['Schere', 'Stein', 'Papier']
    show_highscore_form = False

    # Wenn der Spieler einen Zug macht
    if request.method == 'POST' and 'move' in request.POST:
        player_move = request.POST.get('move')
        history.append(player_move)
        
        # KI-Logik
        computer_move = ''
        if difficulty == 'easy': # Nachahmer
            last_win = request.session.get('rps_last_win', random.choice(options))
            computer_move = last_win
        elif difficulty == 'hard': # Analytiker
            if len(history) > 2:
                most_common = Counter(history).most_common(1)[0][0]
                # Wähle den Konter
                if most_common == 'Schere': computer_move = 'Stein'
                elif most_common == 'Stein': computer_move = 'Papier'
                else: computer_move = 'Schere'
            else:
                computer_move = random.choice(options)
        else: # Mittel (Zufall)
            computer_move = random.choice(options)
        
        # Gewinner ermitteln
        if player_move == computer_move:
            result = 'Unentschieden!'
            streak = 0
            show_highscore_form = True # Nach unentschieden Serie speichern
        elif (player_move == 'Stein' and computer_move == 'Schere') or \
             (player_move == 'Schere' and computer_move == 'Papier') or \
             (player_move == 'Papier' and computer_move == 'Stein'):
            result = 'Du gewinnst!'
            streak += 1
            request.session['rps_last_win'] = player_move
        else:
            result = 'Computer gewinnt!'
            show_highscore_form = True # Nach Niederlage Serie speichern
            streak = 0
            
        message = f"Du hast {player_move} gewählt, der Computer hat {computer_move} gewählt. {result}"
        choices = {'player': player_move, 'computer': computer_move}

    # Session aktualisieren
    request.session['rps_message'] = message
    request.session['rps_streak'] = streak
    request.session['rps_history'] = history[-10:] # Nur die letzten 10 Züge merken
    request.session['rps_choices'] = choices
    
    context = {
        'message': message,
        'streak': streak,
        'choices': choices,
        'show_highscore_form': show_highscore_form,
    }
    return render(request, 'games/rock_paper_scissors.html', context)