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
    # NEU: Die Adresse für Pong
    path('pong/', views.pong, name='pong'),
    path('save-score/', views.save_score, name='save_score'),
]