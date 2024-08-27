# main.py

from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from ws_handler import handle_websocket

app = FastAPI()

# Serve static files (client-side code)
app.mount("/static", StaticFiles(directory="../client"), name="static")
@app.get("/")
async def read_root():
    return FileResponse("../client/index.html")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    await handle_websocket(websocket, game_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)