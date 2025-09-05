from django.urls import path
from . import views

app_name = 'games'

urlpatterns = [
    path('', views.game_list, name='game_list'),
    path('highscores/', views.highscore_list, name='highscores'),
    path('save-score/', views.save_score, name='save_score'),

    path('zahlen-raten/', views.guess_the_number, name='guess_the_number'),
    path('schere-stein-papier/', views.rock_paper_scissors, name='rock_paper_scissors'),
    path('tic-tac-toe/', views.tic_tac_toe, name='tic_tac_toe'),
    path('galgenmaennchen/', views.hangman, name='hangman'),
    path('snake/', views.snake, name='snake'),
    path('pong/', views.pong, name='pong'),
    path('tetris/', views.tetris, name='tetris'),
    path('super-breakout/', views.super_breakout, name='super_breakout'),
    path('pacman/', views.pacman, name='pacman'),
    path('space-invaders/', views.space_invaders, name='space_invaders'),
    path('whack-a-mole/', views.whack_a_mole, name='whack_a_mole'),
    path('asteroids/', views.asteroids, name='asteroids'), # NEU
]