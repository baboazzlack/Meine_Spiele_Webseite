# Vollständiger Inhalt für: highscore_service/main.py

import sqlalchemy
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import databases

# --- Datenbank-Setup ---
# Definiert die URL für unsere SQLite-Datenbank.
# Die Datei 'highscores.db' wird im highscore_service-Ordner erstellt.
DATABASE_URL = "sqlite:///./highscores.db"

# Erstellt ein Datenbank-Objekt, das FastAPI für die Verbindung nutzt.
database = databases.Database(DATABASE_URL)

# Definiert die Metadaten für die Datenbank-Tabellen.
metadata = sqlalchemy.MetaData()

# Definiert die Struktur unserer 'highscores'-Tabelle.
highscores = sqlalchemy.Table(
    "highscores",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("player_name", sqlalchemy.String),
    sqlalchemy.Column("game", sqlalchemy.String),
    sqlalchemy.Column("score", sqlalchemy.Integer),
)

# Erstellt die Datenbank-Engine.
engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
# Erstellt die Tabelle in der Datenbank, falls sie noch nicht existiert.
metadata.create_all(engine)

# --- Pydantic Datenmodelle (für Typsicherheit und Validierung) ---
# Dieses Modell definiert, wie ein Highscore aussehen muss, wenn er
# an unsere API gesendet wird (z.B. von Django).
class HighscoreIn(BaseModel):
    player_name: str
    game: str
    score: int

# Dieses Modell definiert, wie ein Highscore aussieht, wenn er
# von unserer API zurückgegeben wird (inkl. der ID aus der Datenbank).
class Highscore(BaseModel):
    id: int
    player_name: str
    game: str
    score: int

# --- FastAPI Anwendung ---
app = FastAPI()

# Events, die beim Starten und Stoppen der App ausgeführt werden
@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# --- API Endpunkte ---
@app.get("/highscores/", response_model=List[Highscore])
async def read_highscores():
    """Gibt eine Liste aller Highscores aus der Datenbank zurück."""
    query = highscores.select().order_by(sqlalchemy.desc(highscores.c.score))
    return await database.fetch_all(query)

@app.post("/highscores/", response_model=Highscore)
async def create_highscore(score: HighscoreIn):
    """Nimmt einen neuen Highscore entgegen und speichert ihn in der Datenbank."""
    query = highscores.insert().values(
        player_name=score.player_name,
        game=score.game,
        score=score.score
    )
    last_record_id = await database.execute(query)
    return {**score.dict(), "id": last_record_id}

@app.get("/")
async def read_root():
    return {"message": "Highscore-Service ist online und mit der Datenbank verbunden!"}