from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
import json
import asyncio
import os

from RetroArcadeHub.api import read_highscores, clear_all_highscores, create_highscore, HighscoreIn

HIGHSCORE_DELETE_PASSWORD = os.environ.get('HIGHSCORE_DELETE_PASSWORD', 'fallback_is_invalid')


def game_list(request):
    return render(request, 'games/game_list.html')

def highscore_list(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        if password == HIGHSCORE_DELETE_PASSWORD:
            try:
                asyncio.run(clear_all_highscores())
                messages.success(request, 'Highscore-Liste wurde erfolgreich zurückgesetzt!')
            except Exception as e:
                messages.error(request, f'Fehler beim Löschen der Highscores: {e}')
        else:
            messages.error(request, 'Falsches Passwort!')
        return redirect('games:highscores')

    scores = []
    try:
        scores = asyncio.run(read_highscores())
    except Exception as e:
         messages.warning(request, f'Der Highscore-Service meldet einen Fehler: {e}')
    
    return render(request, 'games/highscore_list.html', {'highscores': scores})

def save_score(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            score_data = HighscoreIn(
                player_name=data.get('player_name', 'ANONYM'),
                game=data.get('game', 'Unbekannt'),
                score=int(data.get('score', 0))
            )
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
# KORREKTUR: Tippfehler im Template-Pfad behoben
def pacman(request): return render(request, 'games/pacman.html')
def space_invaders(request): return render(request, 'games/space_invaders.html')
def asteroids(request): return render(request, 'games/asteroids.html')
def galaga(request): return render(request, 'games/galaga.html')