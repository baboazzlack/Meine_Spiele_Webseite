# Ort: games/models.py
from django.db import models

class Highscore(models.Model):
    player_name = models.CharField(max_length=100)
    game = models.CharField(max_length=50, default="Tic-Tac-Toe") # NEU
    difficulty = models.CharField(max_length=10)
    score = models.IntegerField(default=1) # NEU: Für Siegesserien
    date_achieved = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.player_name} - {self.game} ({self.score})'