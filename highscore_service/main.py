import sqlalchemy, json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List
import databases
from fastapi.middleware.cors import CORSMiddleware

DATABASE_URL = "sqlite:///./highscores.db"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()
highscores = sqlalchemy.Table(
    "highscores", metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("player_name", sqlalchemy.String),
    sqlalchemy.Column("game", sqlalchemy.String),
    sqlalchemy.Column("score", sqlalchemy.Integer),
)
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
app = FastAPI()

# HIER IST DIE WICHTIGE ÄNDERUNG:
origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://gfn-retro-hub.onrender.com"  # Deine Live-Webseiten-URL
]
app.add_middleware(
    CORSMiddleware, allow_origins=origins, allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/highscores/", response_model=List[Highscore])
async def read_highscores():
    query = highscores.select().order_by(sqlalchemy.desc(highscores.c.score))
    return await database.fetch_all(query)

@app.post("/highscores/", response_model=Highscore)
async def create_highscore(score: HighscoreIn):
    query = highscores.insert().values(player_name=score.player_name, game=score.game, score=score.score)
    last_record_id = await database.execute(query)
    new_highscore_data = {**score.dict(), "id": last_record_id}
    highscore_message = json.dumps({"type": "highscore", "data": new_highscore_data})
    await manager.broadcast(highscore_message)
    return new_highscore_data

@app.delete("/highscores/clear/")
async def clear_all_highscores():
    query = highscores.delete()
    await database.execute(query)
    return {"message": "Alle Highscores wurden erfolgreich gelöscht."}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket)

@app.get("/")
async def read_root():
    return {"message": "Highscore-Service ist online und mit der Datenbank verbunden!"}