from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
import requests
import json

BASE_API_URL = "http://127.0.0.1:8000/api/highscores/"

def game_list(request):
    return render(request, 'games/game_list.html')

def highscore_list(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        if password == 'Offenbach069':
            try:
                response = requests.delete(f"{BASE_API_URL}clear/", timeout=5)
                if response.status_code == 200:
                    messages.success(request, 'Highscore-Liste wurde erfolgreich zurückgesetzt!')
                else:
                    messages.error(request, f'API-Fehler: Status {response.status_code}.')
            except requests.exceptions.RequestException as e:
                messages.error(request, f'Verbindungsfehler zur API: {e}')
        else:
            messages.error(request, 'Falsches Passwort!')
        return redirect('games:highscores')

    scores = []
    try:
        response = requests.get(BASE_API_URL, timeout=5)
        if response.status_code == 200:
            scores = response.json()
        else:
             messages.warning(request, f'Der Highscore-Service meldet einen Fehler (Statuscode: {response.status_code}).')
    except requests.exceptions.RequestException:
        messages.warning(request, 'Der Highscore-Service ist nicht erreichbar. Läuft die Anwendung?')
    
    return render(request, 'games/highscore_list.html', {'highscores': scores})

def save_score(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            api_data = {
                "player_name": data.get('player_name', 'ANONYM'),
                "game": data.get('game', 'Unbekannt'),
                "score": int(data.get('score', 0))
            }
            requests.post(BASE_API_URL, json=api_data, timeout=5)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'invalid_method'}, status=405)

def guess_the_number(request): return render(request, 'games/guess_the_number.html')
def rock_paper_scissors(request): return render(request, 'games/rock_paper_scissors.html')
def tic_tac_toe(request): return render(request, 'games/tic_tac_toe.html')
def hangman(request): return render(request, 'games/hangman.html')
def snake(request): return render(request, 'games/snake.html')
def pong(request): return render(request, 'games/pong.html')
def tetris(request): return render(request, 'games/tetris.html')
def super_breakout(request): return render(request, 'games/super_breakout.html')
def pacman(request): return render(request, 'games/pacman.html')
def space_invaders(request): return render(request, 'games/space_invaders.html')
def whack_a_mole(request): return render(request, 'games/whack_a_mole.html')