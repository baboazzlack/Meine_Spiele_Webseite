# Ort: games/urls.py
from django.urls import path
from . import views
app_name = 'games'
urlpatterns = [
    path('', views.game_list, name='game_list'),
    path('zahlen-raten/', views.guess_the_number, name='guess_the_number'),
    path('tic-tac-toe/', views.tic_tac_toe, name='tic_tac_toe'),
    # NEU: Die Adresse für die Highscore-Liste
    path('highscores/', views.highscore_list, name='highscores'),
]