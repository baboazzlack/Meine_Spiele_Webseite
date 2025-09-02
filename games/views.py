from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
import json
import asyncio # Modul für die Ausführung von Async-Funktionen

# KORREKTUR: Wir importieren die Highscore-Logik direkt aus der api.py
# anstatt sie über das Netzwerk aufzurufen.
from RetroArcadeHub.api import read_highscores, clear_all_highscores, create_highscore, HighscoreIn

# HINWEIS: Das Passwort verbleibt als Umgebungsvariable
import os
HIGHSCORE_DELETE_PASSWORD = os.environ.get('HIGHSCORE_DELETE_PASSWORD', 'fallback_is_invalid')


def game_list(request):
    return render(request, 'games/game_list.html')

def highscore_list(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        if password == HIGHSCORE_DELETE_PASSWORD:
            try:
                # DIREKTER AUFRUF: Führt die clear_all_highscores Funktion aus.
                asyncio.run(clear_all_highscores())
                messages.success(request, 'Highscore-Liste wurde erfolgreich zurückgesetzt!')
            except Exception as e:
                messages.error(request, f'Fehler beim Löschen der Highscores: {e}')
        else:
            messages.error(request, 'Falsches Passwort!')
        return redirect('games:highscores')

    scores = []
    try:
        # DIREKTER AUFRUF: Führt die read_highscores Funktion aus.
        scores = asyncio.run(read_highscores())
    except Exception as e:
         messages.warning(request, f'Der Highscore-Service meldet einen Fehler: {e}')
    
    return render(request, 'games/highscore_list.html', {'highscores': scores})

def save_score(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Wir erstellen ein Datenobjekt, das die API-Funktion erwartet
            score_data = HighscoreIn(
                player_name=data.get('player_name', 'ANONYM'),
                game=data.get('game', 'Unbekannt'),
                score=int(data.get('score', 0))
            )
            # DIREKTER AUFRUF: Führt die create_highscore Funktion aus.
            asyncio.run(create_highscore(score=score_data))
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'invalid_method'}, status=405)

# --- Ansichten für alle Spiele ---
def guess_the_number(request): return render(request, 'games/guess_the_number.html')
def rock_paper_scissors(request): return render(request, 'games/rock_paper_scissors.html')
def tic_tac_toe(request): return render(request, 'games/tic_tac_toe.html')
def hangman(request): return render(request, 'games/hangman.html')
def snake(request): return render(request, 'games/snake.html')
def pong(request): return render(request, 'games/pong.html')
def tetris(request): return render(request, 'games/tetris.html')
def super_breakout(request): return render(request, 'games/super_breakout.html')
def pacman(request): return render(request, 'games-pacman') # There seems to be a typo here, it should probably be pacman.html
def space_invaders(request): return render(request, 'games/space_invaders.html')