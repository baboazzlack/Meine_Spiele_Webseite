# Vollständiger Inhalt für: highscore_service/main.py

import sqlalchemy
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List
import databases
import json

# --- NEU: Import für die CORS-Middleware ---
from fastapi.middleware.cors import CORSMiddleware

# --- Datenbank-Setup (unverändert) ---
DATABASE_URL = "sqlite:///./highscores.db"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()
highscores = sqlalchemy.Table(
    "highscores",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("player_name", sqlalchemy.String),
    sqlalchemy.Column("game", sqlalchemy.String),
    sqlalchemy.Column("score", sqlalchemy.Integer),
)
engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
metadata.create_all(engine)

# --- Pydantic Datenmodelle (unverändert) ---
class HighscoreIn(BaseModel):
    player_name: str
    game: str
    score: int

class Highscore(BaseModel):
    id: int
    player_name: str
    game: str
    score: int

# --- WebSocket Connection Manager (unverändert) ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
manager = ConnectionManager()

# --- FastAPI Anwendung ---
app = FastAPI()

# --- NEU: Die "Gästeliste" für unseren Türsteher (CORS-Middleware) ---
# Definiert, welche Adressen (origins) mit unserem Service reden dürfen.
origins = [
    "http://localhost:8000",  # Erlaubt Anfragen von unserer Django-Entwicklungs-Seite
    "http://127.0.0.1:8000", # Eine weitere gängige Adresse für localhost
    # Später können wir hier auch deine Live-URL eintragen, z.B. "https://gfn-retro-hub.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Erlaubt alle Methoden (GET, POST, etc.)
    allow_headers=["*"], # Erlaubt alle Header
)
# --- ENDE ---

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# --- API Endpunkte (unverändert) ---
@app.get("/highscores/", response_model=List[Highscore])
async def read_highscores():
    query = highscores.select().order_by(sqlalchemy.desc(highscores.c.score))
    return await database.fetch_all(query)

@app.post("/highscores/", response_model=Highscore)
async def create_highscore(score: HighscoreIn):
    query = highscores.insert().values(player_name=score.player_name, game=score.game, score=score.score)
    last_record_id = await database.execute(query)
    new_highscore_data = {**score.dict(), "id": last_record_id}
    await manager.broadcast(json.dumps(new_highscore_data))
    return new_highscore_data

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/")
async def read_root():
    return {"message": "Highscore-Service ist online und mit der Datenbank verbunden!"}