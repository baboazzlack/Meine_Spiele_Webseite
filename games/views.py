# Vollständiger Inhalt für: games/views.py

import random, json, requests
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from collections import Counter
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def dashboard(request):
    """Zeigt die Hauptseite des Admin-Dashboards."""
    # NEU: Hole alle Benutzer aus der Datenbank, außer dem aktuell eingeloggten Admin
    all_users = User.objects.exclude(username=request.user.username)
    
    context = {
        'users': all_users,
    }
    return render(request, 'dashboard.html', context)

# ==============================================================================
# ZENTRALE HILFSFUNKTION zum Speichern von Highscores
# ==============================================================================
def _save_score_to_api(payload):
    """
    Eine interne Hilfsfunktion, die einen Highscore-Payload
    an den FastAPI-Microservice sendet.
    """
    api_url = "http://highscore_api:8001/highscores/"
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status() # Löst einen Fehler aus, wenn die API einen Fehler zurückgibt
        print(f"Highscore erfolgreich an API gesendet: {payload}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Fehler bei der Kommunikation mit Highscore-Service: {e}")
        return False

# ==============================================================================
# Die View für die JS-Spiele (Snake, Pong etc.)
# ==============================================================================
def save_score(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            player_name = data.get('player_name') or data.get('name') or data.get('player') or 'Anonym'
            payload = {
                "player_name": player_name,
                "game": data.get('game', 'Unknown'),
                "score": data.get('score', 0)
            }
            
            if _save_score_to_api(payload):
                return JsonResponse({'status': 'success', 'message': 'Highscore an Service gesendet.'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Kommunikationsfehler mit Highscore-Service'}, status=503)

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

# Schere, Stein, Papier - JETZT AKTUALISIERT
def rock_paper_scissors(request):
    # Logik zum Speichern des Highscores
    if request.method == 'POST' and 'player_name' in request.POST:
        if request.session.get('rps_streak', 0) > 0:
            payload = {
                'player_name': request.POST.get('player_name', 'Anonym'),
                'game': "Schere, Stein, Papier",
                'score': request.session.get('rps_streak', 0)
            }
            _save_score_to_api(payload) # BENUTZT NEUES SYSTEM
            
        for k in ['rps_difficulty','rps_streak','rps_history','rps_message','rps_choices']: request.session.pop(k, None)
        return redirect(reverse('games:highscores'))

    # Die restliche Spiellogik (unverändert)
    if request.GET.get('reset') == 'true':
        for k in ['rps_difficulty','rps_streak','rps_history','rps_message','rps_choices']: request.session.pop(k, None)
        return redirect(reverse('games:rock_paper_scissors'))
    if request.method == 'POST' and 'difficulty' in request.POST:
        difficulty = request.POST.get('difficulty')
        request.session.update({'rps_difficulty':difficulty, 'rps_streak':0, 'rps_history':[], 'rps_message':f"Schwierigkeit: {difficulty}. Wähle dein Zeichen!"})
        return redirect(reverse('games:rock_paper_scissors'))
    if 'rps_difficulty' not in request.session: return render(request, 'games/rock_paper_scissors.html')
    message, streak, choices, show_highscore_form = request.session.get('rps_message',''), request.session.get('rps_streak',0), request.session.get('rps_choices',{}), False
    if request.method == 'POST' and 'move' in request.POST:
        player_move = request.POST.get('move')
        history = request.session.get('rps_history', [])
        history.append(player_move)
        options = ['Schere', 'Stein', 'Papier']
        if request.session.get('rps_difficulty') == 'easy': computer_move = request.session.get('rps_last_win', random.choice(options))
        elif request.session.get('rps_difficulty') == 'hard' and len(history) > 2:
            most_common = Counter(history).most_common(1)[0][0]
            if most_common == 'Schere': computer_move = 'Stein'
            elif most_common == 'Stein': computer_move = 'Papier'
            else: computer_move = 'Schere'
        else: computer_move = random.choice(options)
        if player_move == computer_move: result, streak, show_highscore_form = 'Unentschieden!', 0, True
        elif (player_move, computer_move) in [('Stein','Schere'),('Schere','Papier'),('Papier','Stein')]:
            result, streak = 'Du gewinnst!', streak + 1
            request.session['rps_last_win'] = player_move
        else: result, streak, show_highscore_form = 'Computer gewinnt!', 0, True
        message, choices = f"Du: {player_move}, PC: {computer_move}. {result}", {'player': player_move, 'computer': computer_move}
        request.session['rps_history'] = history[-10:]
    request.session.update({'rps_message':message, 'rps_streak':streak, 'rps_choices':choices})
    return render(request, 'games/rock_paper_scissors.html', {'message': message, 'streak': streak, 'choices': choices, 'show_highscore_form': show_highscore_form})

# Galgenmännchen - JETZT AKTUALISIERT
def hangman(request):
    # Logik zum Speichern des Highscores
    if request.method == 'POST' and 'player_name' in request.POST:
        score = request.session.get('guesses_left', 0)
        if score > 0:
            payload = {
                'player_name': request.POST.get('player_name','Anonym'),
                'game': "Galgenmännchen",
                'score': score
            }
            _save_score_to_api(payload) # BENUTZT NEUES SYSTEM

        for k in ['secret_word','guessed_letters','guesses_left','hangman_difficulty']: request.session.pop(k, None)
        return redirect(reverse('games:highscores'))
        
    # Die restliche Spiellogik (unverändert)
    word_lists = {'easy':["HAUS","AUTO","BALL"],"medium":["PYTHON","DJANGO"],"hard":["BIBLIOTHEK","ALGORITHMUS"]}
    guesses_map = {'easy': 8, 'medium': 6, 'hard': 5}
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÜ"
    if request.method == 'POST' and 'difficulty' in request.POST:
        difficulty = request.POST.get('difficulty')
        request.session.update({'hangman_difficulty':difficulty, 'secret_word':random.choice(word_lists[difficulty]), 'guessed_letters':[], 'guesses_left':guesses_map[difficulty]})
        return redirect(reverse('games:hangman'))
    if request.GET.get('reset') == 'true' or 'hangman_difficulty' not in request.session:
        for k in ['secret_word','guessed_letters','guesses_left','hangman_difficulty']: request.session.pop(k, None)
        return render(request, 'games/hangman.html')
    secret_word, guessed_letters, guesses_left = request.session.get('secret_word'), request.session.get('guessed_letters',[]), request.session.get('guesses_left',6)
    message, winner = '', None
    if request.method == 'POST' and 'guess' in request.POST:
        guess = request.POST.get('guess').upper()
        if guess in alphabet and len(guess) == 1 and guess not in guessed_letters:
            guessed_letters.append(guess)
            if guess not in secret_word: guesses_left -= 1
    display_word = "".join([letter if letter in guessed_letters else "_" for letter in secret_word])
    if display_word == secret_word: winner, message = 'player', "🎉 Du hast gewonnen! 🎉 Das Wort war " + secret_word
    elif guesses_left <= 0: winner, message = 'computer', "Du hast verloren! Das Wort war " + secret_word
    request.session.update({'guessed_letters':guessed_letters, 'guesses_left':guesses_left})
    context = {'display_word':" ".join(display_word), 'guesses_left':guesses_left, 'guessed_letters':guessed_letters, 'alphabet':alphabet, 'winner':winner, 'message':message}
    return render(request, 'games/hangman.html', context)


# ==============================================================================
# Unveränderte Views
# ==============================================================================

def tic_tac_toe(request):
    def check_winner(board):
        for i in range(3):
            if board[i][0] == board[i][1] == board[i][2] != '': return board[i][0]
            if board[0][i] == board[1][i] == board[2][i] != '': return board[0][i]
        if board[0][0] == board[1][1] == board[2][2] != '': return board[0][0]
        if board[0][2] == board[1][1] == board[2][0] != '': return board[0][2]
        if all(all(cell != '' for cell in row) for row in board): return 'draw'
        return None

    def computer_move(board, difficulty):
        empty_cells = [(r, c) for r in range(3) for c in range(3) if board[r][c] == '']
        if not empty_cells: return
        if difficulty == 'easy': r, c = random.choice(empty_cells); board[r][c] = 'O'; return
        for r_try, c_try in empty_cells:
            board[r_try][c_try] = 'O';
            if check_winner(board) == 'O': return
            board[r_try][c_try] = ''
        for r_try, c_try in empty_cells:
            board[r_try][c_try] = 'X'
            if check_winner(board) == 'X': board[r_try][c_try] = 'O'; return
            board[r_try][c_try] = ''
        if difficulty == 'medium': r, c = random.choice(empty_cells); board[r][c] = 'O'; return
        if difficulty == 'hard':
            if board[1][1] == '': board[1][1] = 'O'; return
            corners = [(0,0),(0,2),(2,0),(2,2)]; random.shuffle(corners)
            for r,c in corners:
                if board[r][c] == '': board[r][c] = 'O'; return
            r, c = random.choice(empty_cells); board[r][c] = 'O'

    if request.method == 'POST' and 'player_name' in request.POST:
        payload = {
            'player_name': request.POST.get('player_name', 'Anonym'),
            'game': "Tic-Tac-Toe",
            'score': 1,
        }
        _save_score_to_api(payload)
        for key in ['ttt_board','ttt_difficulty','ttt_message','ttt_wins','ttt_losses']: request.session.pop(key, None)
        return redirect(reverse('games:highscores'))
    if request.GET.get('reset') == 'true':
        for key in ['ttt_board','ttt_difficulty','ttt_message','ttt_wins','ttt_losses']: request.session.pop(key, None)
        return redirect(reverse('games:tic_tac_toe'))
    if request.method == 'POST' and 'difficulty' in request.POST:
        difficulty = request.POST.get('difficulty')
        request.session.update({'ttt_difficulty':difficulty, 'ttt_board':[['','',''],['','',''],['','','']], 'ttt_message':f"Du bist Spieler X. Schwierigkeit: {difficulty}. Mach deinen Zug!", 'ttt_wins':0, 'ttt_losses':0})
        return redirect(reverse('games:tic_tac_toe'))
    if 'ttt_difficulty' not in request.session: return render(request, 'games/tic_tac_toe.html')
    board, message = request.session['ttt_board'], request.session['ttt_message']
    if request.method == 'POST' and 'move' in request.POST and not check_winner(board):
        try:
            row, col = map(int, request.POST.get('move').split(','))
            if board[row][col] == '':
                board[row][col] = 'X'
                if not check_winner(board): computer_move(board, request.session.get('ttt_difficulty'))
                winner = check_winner(board)
                if winner:
                    if winner == 'X': message, request.session['ttt_wins'] = "🎉 Du hast gewonnen! 🎉 Gib deinen Namen ein!", request.session.get('ttt_wins',0) + 1
                    elif winner == 'O': message, request.session['ttt_losses'] = "Der Computer hat gewonnen!", request.session.get('ttt_losses',0) + 1
                    else: message = "Unentschieden!"
                else: message = "Du bist wieder am Zug."
        except (ValueError, IndexError): message = "Ungültiger Zug!"
    request.session.update({'ttt_board':board, 'ttt_message':message})
    context = {'board':board, 'message':message, 'winner':check_winner(board), 'wins':request.session.get('ttt_wins',0), 'losses':request.session.get('ttt_losses',0)}
    return render(request, 'games/tic_tac_toe.html', context)

def game_list(request):
    games = [
        {'name': 'Space Invaders', 'description': 'Verteidige die Erde vor den Aliens!', 'category': 'Neue Retro Games', 'url_name': 'games:space_invaders'},
        {'name': 'Zahlen Raten', 'description': 'Ein klassisches Ratespiel.', 'category': 'Alte Retro Games', 'url_name': 'games:guess_the_number'},
        {'name': 'Tic-Tac-Toe', 'description': 'Der unsterbliche Klassiker.', 'category': 'Alte Retro Games', 'url_name': 'games:tic_tac_toe'},
        {'name': 'Schere, Stein, Papier', 'description': 'Glück, Taktik oder beides?', 'category': 'Alte Retro Games', 'url_name': 'games:rock_paper_scissors'},
        {'name': 'Galgenmännchen', 'description': 'Errate das geheime Wort.', 'category': 'Alte Retro Games', 'url_name': 'games:hangman'},
        {'name': 'Snake', 'description': 'Der unzerstörbare Nokia-Klassiker.', 'category': 'Neue Retro Games', 'url_name': 'games:snake'},
        {'name': 'Pong', 'description': 'Der Urvater aller Videospiele.', 'category': 'Neue Retro Games', 'url_name': 'games:pong'},
        {'name': 'Tetris', 'description': 'Der König der Puzzle-Spiele.', 'category': 'Neue Retro Games', 'url_name': 'games:tetris'},
        {'name': 'Pac-Man', 'description': 'Jage die Geister durch das Labyrinth!', 'category': 'Neue Retro Games', 'url_name': 'games:pacman'},
    ]
    alte_spiele = [g for g in games if g['category'] == 'Alte Retro Games']
    neue_spiele = [g for g in games if g['category'] == 'Neue Retro Games']
    return render(request, 'games/game_list.html', {'alte_spiele': alte_spiele, 'neue_spiele': neue_spiele})

def highscore_list(request):
    api_url = "http://highscore_api:8001/highscores/"
    scores = []
    message = None
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        scores = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Fehler bei der API-Anfrage: {e}")
        message = "Der Highscore-Service ist momentan nicht erreichbar. Bitte versuche es später erneut."
    return render(request, 'games/highscores.html', {'scores': scores, 'message': message})

def guess_the_number(request):
    if 'secret_number' not in request.session or request.GET.get('reset') == 'true': request.session.update({'secret_number': random.randint(1, 100), 'attempts': 0, 'message': "Ich habe mir eine Zahl zwischen 1 und 100 ausgedacht. Rate mal!"})
    if request.method == 'POST':
        try:
            guess = int(request.POST.get('guess', 0))
            request.session['attempts'] += 1
            if guess < request.session['secret_number']: request.session['message'] = f"Deine Zahl {guess} ist zu niedrig! Versuch's nochmal."
            elif guess > request.session['secret_number']: request.session['message'] = f"Deine Zahl {guess} ist zu hoch! Versuch's nochmal."
            else:
                request.session['message'] = f"🎉 Richtig! Die Zahl war {request.session['secret_number']}! Du hast {request.session['attempts']} Versuche gebraucht. 🎉"; del request.session['secret_number']
        except (ValueError, TypeError): request.session['message'] = "Das war keine gültige Zahl!"
    return render(request, 'games/guess_the_number.html', {'message': request.session.get('message', '')})

def snake(request): return render(request, 'games/snake.html')
def pong(request): return render(request, 'games/pong.html')
def tetris(request): return render(request, 'games/tetris.html')
def pacman(request): return render(request, 'games/pacman.html')
def space_invaders(request):
    """Rendert die Space Invaders Spielseite."""
    return render(request, 'games/space_invaders.html')
# games/views.py --- GANZ AM ENDE HINZUFÜGEN
@staff_member_required
def clear_highscores(request):
    """Sendet eine Anfrage an den FastAPI-Service, um alle Highscores zu löschen."""
    api_url = "http://highscore_api:8001/highscores/clear/"
    try:
        response = requests.delete(api_url)
        response.raise_for_status()
        # Leite den Admin nach der Aktion zur (jetzt leeren) Highscore-Liste weiter
        return redirect('games:highscores')
    except requests.exceptions.RequestException as e:
        # Hier könntest du eine richtige Fehlerseite anzeigen
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)