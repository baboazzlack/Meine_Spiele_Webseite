# RetroArcadeHub/api.py

import sqlalchemy, json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List
import databases

# Die Datenbank wird jetzt im Hauptverzeichnis des Projekts liegen
DATABASE_URL = "sqlite:///../highscores.db"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

highscores = sqlalchemy.Table(
    "highscores", metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("player_name", sqlalchemy.String),
    sqlalchemy.Column("game", sqlalchemy.String),
    sqlalchemy.Column("score", sqlalchemy.Integer),
)

# Wichtig: Die Engine muss hier sein, damit die Tabelle erstellt wird
engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
metadata.create_all(engine)

class HighscoreIn(BaseModel):
    player_name: str
    game: str
    score: int

class Highscore(BaseModel):
    id: int
    player_name: str
    game: str
    score: int

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        await self.broadcast_user_count()
    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        await self.broadcast_user_count()
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
    async def broadcast_user_count(self):
        message = json.dumps({"type": "user_count", "count": len(self.active_connections)})
        await self.broadcast(message)

manager = ConnectionManager()
api = FastAPI() # Wichtig: die Variable heißt jetzt 'api'

@api.on_event("startup")
async def startup():
    await database.connect()

@api.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@api.get("/highscores/", response_model=List[Highscore])
async def read_highscores():
    query = highscores.select().order_by(sqlalchemy.desc(highscores.c.score))
    return await database.fetch_all(query)

@api.post("/highscores/", response_model=Highscore)
async def create_highscore(score: HighscoreIn):
    query = highscores.insert().values(player_name=score.player_name, game=score.game, score=score.score)
    last_record_id = await database.execute(query)
    new_highscore_data = {**score.dict(), "id": last_record_id}
    highscore_message = json.dumps({"type": "highscore", "data": new_highscore_data})
    await manager.broadcast(highscore_message)
    return new_highscore_data

@api.delete("/highscores/clear/")
async def clear_all_highscores():
    query = highscores.delete()
    await database.execute(query)
    return {"message": "Alle Highscores wurden erfolgreich gelöscht."}

@api.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket)