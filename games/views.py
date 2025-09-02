from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
import requests
import json

# Die URL deines FastAPI-Services
HIGHSCORE_API_URL = "http://highscore_api:8001/highscores/"

# --- Haupt-Ansichten ---

def game_list(request):
    """Rendert die Liste aller Spiele."""
    return render(request, 'games/game_list.html')

def highscore_list(request):
    """
    Behandelt die Anzeige der Highscore-Liste und die passwortgeschützte Reset-Funktion.
    JETZT MIT VERBESSERTER FEHLERMELDUNG.
    """
    if request.method == 'POST':
        password = request.POST.get('password')
        if password == 'Offenbach069':
            try:
                response = requests.delete(f"{HIGHSCORE_API_URL}clear/", timeout=5)
                if response.status_code == 200:
                    messages.success(request, 'Highscore-Liste wurde erfolgreich zurückgesetzt!')
                else:
                    messages.error(request, f'Fehler beim Löschen. API antwortete mit Status {response.status_code}.')
            except requests.exceptions.RequestException as e:
                messages.error(request, f'Verbindungsfehler zur API: {e}')
        else:
            messages.error(request, 'Falsches Passwort!')
        return redirect('games:highscores')

    scores = []
    try:
        # Wir fügen einen Timeout hinzu und fangen die Fehler genauer ab
        response = requests.get(HIGHSCORE_API_URL, timeout=5)
        if response.status_code == 200:
            scores = response.json()
        else:
             # Spezifische Nachricht, wenn der Server einen Fehler meldet (z.B. 500)
             messages.warning(request, f'Der Highscore-Service meldet einen Fehler (Statuscode: {response.status_code}).')
    except requests.exceptions.RequestException:
        # Spezifische Nachricht bei einem Verbindungsproblem
        messages.warning(request, 'Der Highscore-Service ist nicht erreichbar. Bitte stelle sicher, dass alle Container laufen.')

    context = {
        'highscores': scores
    }
    return render(request, 'games/highscore_list.html', context)

# --- Ansichten für ALLE fertigen Spiele ---

def guess_the_number(request):
    return render(request, 'games/guess_the_number.html')

def rock_paper_scissors(request):
    return render(request, 'games/rock_paper_scissors.html')

def tic_tac_toe(request):
    return render(request, 'games/tic_tac_toe.html')

def super_breakout(request):
    return render(request, 'games/super_breakout.html')

def hangman(request):
    return render(request, 'games/hangman.html')

def snake(request):
    return render(request, 'games/snake.html')

def pong(request):
    return render(request, 'games/pong.html')

def tetris(request):
    return render(request, 'games/tetris.html')

def pacman(request):
     return render(request, 'games/pacman.html')

def space_invaders(request):
    return render(request, 'games-invaders.html')

# --- Logik zum Speichern von Scores ---
def save_score(request):
    """Empfängt einen Score per POST-Request und sendet ihn an den FastAPI-Service."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            api_data = {
                "player_name": data.get('player_name', 'ANONYM'),
                "game": data.get('game', 'Unbekannt'),
                "score": int(data.get('score', 0))
            }
            requests.post(HIGHSCORE_API_URL, json=api_data, timeout=5)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'invalid_method'}, status=405)