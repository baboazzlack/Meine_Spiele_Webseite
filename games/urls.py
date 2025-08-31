# Ort: games/urls.py
from django.urls import path
from . import views
app_name = 'games'
urlpatterns = [
    path('', views.game_list, name='game_list'),
    path('zahlen-raten/', views.guess_the_number, name='guess_the_number'),
    path('tic-tac-toe/', views.tic_tac_toe, name='tic_tac_toe'),
    path('highscores/', views.highscore_list, name='highscores'),
    path('schere-stein-papier/', views.rock_paper_scissors, name='rock_paper_scissors'),
    path('galgenmaennchen/', views.hangman, name='hangman'),
    path('snake/', views.snake, name='snake'),
    path('pong/', views.pong, name='pong'),
    path('tetris/', views.tetris, name='tetris'),
    # NEU: Die Adresse für Pac-Man
    path('pacman/', views.pacman, name='pacman'),
    path('save-score/', views.save_score, name='save_score'),
]