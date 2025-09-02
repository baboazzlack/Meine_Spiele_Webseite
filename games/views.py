# games/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
import requests
import json

HIGHSCORE_API_URL = "http://highscore_api:8001/highscores/"

# ... (game_list and highscore_list views remain unchanged) ...
def game_list(request):
    return render(request, 'games/game_list.html')
# ...

# --- Ansichten für ALLE fertigen Spiele ---
def guess_the_number(request):
    return render(request, 'games/guess_the_number.html')

def rock_paper_scissors(request):
    return render(request, 'games/rock_paper_scissors.html')

def tic_tac_toe(request):
    return render(request, 'games/tic_tac_toe.html') # KORRIGIERT

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

# --- Logik zum Speichern von Scores (unverändert) ---
def save_score(request):
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