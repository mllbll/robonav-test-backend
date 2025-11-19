from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import json
import websocket
import os
import sys

app = FastAPI()

os.makedirs("templates", exist_ok=True)
templates = Jinja2Templates(directory="templates")

# Замените на IP-адрес робота в вашей сети
ROBOT_IP = '192.168.0.137'
ROSBRIDGE_PORT = 9090

def get_robot_topics():
    """
    Подключается к rosbridge на роботе через WebSocket,
    вызывает сервис /rosapi/topics и получает список топиков.
    Возвращает список топиков и ошибку (если есть)
    """
    topics = []
    error = None
    
    try:
        ws_url = f"ws://{ROBOT_IP}:{ROSBRIDGE_PORT}"
        print(f"[DEBUG] Подключаемся к {ws_url}", file=sys.stderr)
        
        ws = websocket.create_connection(ws_url, timeout=10)
        print("[DEBUG] Соединение установлено", file=sys.stderr)
        
        request_msg = {
            "op": "call_service",
            "service": "/rosapi/topics",
            "args": {}
        }
        ws.send(json.dumps(request_msg))
        print(f"[DEBUG] Запрос отправлен: {request_msg}", file=sys.stderr)
        
        response_data = ws.recv()
        print(f"[DEBUG] Ответ получен: {response_data[:500]}", file=sys.stderr)
        
        response = json.loads(response_data)
        
        if 'values' in response and 'topics' in response['values'] and isinstance(response['values']['topics'], list):
            topics = response['values']['topics']
            print(f"[DEBUG] Найдено топиков: {len(topics)}", file=sys.stderr)
        else:
            error = f"Неверный формат ответа rosbridge: {response}"
            print(f"[ERROR] {error}", file=sys.stderr)
        
        ws.close()
        print("[DEBUG] Соединение закрыто", file=sys.stderr)
        
    except Exception as e:
        error = f"Ошибка подключения к rosbridge: {str(e)}"
        print(f"[ERROR] {error}", file=sys.stderr)
    
    return topics, error

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    topics_list, error = get_robot_topics()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "topics": topics_list, "error": error}
    )

@app.get("/api/topics")
async def get_topics_json():
    topics_list, error = get_robot_topics()
    if error:
        return {"error": error, "topics": [], "count": 0}
    return {"topics": topics_list, "count": len(topics_list)}

@app.get("/api/robot_config")
async def get_robot_config():
    """Возвращает конфигурацию робота для подключения"""
    return {
        "robot_ip": ROBOT_IP,
        "rosbridge_port": ROSBRIDGE_PORT,
        "rosbridge_url": f"ws://{ROBOT_IP}:{ROSBRIDGE_PORT}"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

