from django.shortcuts import render, redirect
from django.contrib import messages
import requests
import json

# Die URL deines FastAPI-Services
HIGHSCORE_API_URL = "http://highscore_api:8001/highscores/"

# --- Ansichten für die Spiele (unverändert) ---
def game_list(request):
    return render(request, 'games/game_list.html')

def guess_the_number(request):
    return render(request, 'games/standard_game_page.html', {'game_title': 'Zahlen Raten'})

def tic_tac_toe(request):
    return render(request, 'games/standard_game_page.html', {'game_title': 'Tic-Tac-Toe'})

def rock_paper_scissors(request):
    return render(request, 'games/standard_game_page.html', {'game_title': 'Schere-Stein-Papier'})

def hangman(request):
    return render(request, 'games/standard_game_page.html', {'game_title': 'Galgenmännchen'})

def snake(request):
    return render(request, 'games/standard_game_page.html', {'game_title': 'Snake'})

def super_breakout(request):
    return render(request, 'games/super_breakout.html')

def pong(request):
    return render(request, 'games/standard_game_page.html', {'game_title': 'Pong'})

def tetris(request):
    return render(request, 'games/standard_game_page.html', {'game_title': 'Tetris'})

def pacman(request):
    return render(request, 'games/standard_game_page.html', {'game_title': 'Pac-Man'})

def space_invaders(request):
    return render(request, 'games/standard_game_page.html', {'game_title': 'Space Invaders'})

# --- Logik zum Speichern von Scores (unverändert) ---
def save_score(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            player_name = data.get('player_name', 'ANONYM')
            game = data.get('game', 'Unbekannt')
            score = data.get('score', 0)

            api_data = {
                "player_name": player_name,
                "game": game,
                "score": int(score)
            }
            
            response = requests.post(HIGHSCORE_API_URL, json=api_data)
            
            if response.status_code == 200:
                return redirect('games:highscores')
            else:
                # Optional: Fehlerbehandlung, falls die API nicht erreichbar ist
                pass
        except Exception as e:
            # Optional: Fehler loggen
            pass
    return redirect('games:highscores')


# --- NEUE, ERWEITERTE HIGHSCORE-ANSICHT ---
def highscore_list(request):
    # Logik für das Löschen der Highscores per Passwort
    if request.method == 'POST':
        password = request.POST.get('password')
        if password == 'Offenbach069':
            try:
                # Sende DELETE-Request an die FastAPI
                response = requests.delete(f"{HIGHSCORE_API_URL}clear/")
                if response.status_code == 200:
                    messages.success(request, 'Highscore-Liste wurde erfolgreich zurückgesetzt!')
                else:
                    messages.error(request, f'Fehler beim Löschen. API antwortete mit Status {response.status_code}.')
            except requests.exceptions.RequestException as e:
                messages.error(request, f'Verbindungsfehler zur API: {e}')
        else:
            messages.error(request, 'Falsches Passwort!')
        return redirect('games:highscores')

    # Logik für das Anzeigen der Highscores
    scores = []
    try:
        response = requests.get(HIGHSCORE_API_URL)
        if response.status_code == 200:
            scores = response.json()
        else:
             messages.warning(request, 'Die Highscore-Liste konnte nicht geladen werden. Der Service ist möglicherweise nicht erreichbar.')
    except requests.exceptions.RequestException:
        messages.warning(request, 'Die Highscore-Liste konnte nicht geladen werden. Der Service ist möglicherweise nicht erreichbar.')

    context = {
        'highscores': scores
    }
    return render(request, 'games/highscore_list.html', context)