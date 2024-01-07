import uvicorn

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse, Response, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from jinja2 import Environment, FileSystemLoader

import json
import os

from constants import *
from structures import *

# FasrAPI
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
def root(request: Request):
    dir_path = LOGS_DIR
    temp_files = os.listdir(dir_path)

    # 拡張子がlogのんだけ抽出
    files = []
    for f in temp_files:
        if f[-4:] == ".log":
            files.append(f)

    return templates.TemplateResponse("root.html", {
        "request": request,
        "files": files
    })


@app.get("/{dealer_name}")
def game(request: Request, dealer_name):

    dir_path = LOGS_DIR
    file_path = dir_path + f"{dealer_name}.log"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="log_not_found")

    if os.path.exists(f"{dir_path}/{dealer_name}/game_data.json"):
        with open(f"{dir_path}/{dealer_name}/game_data.json") as f:
            game_data = json.load(f)
        turn_data = game_data["turn_data"]
        N = len(turn_data)

    else:
        game = Game(file_path)
        game.save_separated_logs()
        turn_data = [t.turn_data for t in game.turns]
        N = len(game.turns)

    temp_socket_const = SOCKET_CONST[:]
    temp_socket_const.remove("join-room")
    temp_socket_const.remove("receiver-card")
    temp_socket_const.remove("first-player")
    temp_socket_const.remove("finish-game")
    temp_socket_const.append("penalty")

    # 深刻なデバッグの時用…
    # temp_socket_const.remove("finish-turn")
    # temp_socket_const.append("disconnect")

    return templates.TemplateResponse(
        "game.html", {
            "request": request,
            "dealer_name": dealer_name,
            "N": N,
            "turn_data": turn_data,
            "SOCKET_CONST": temp_socket_const
        })


@app.get("/{dealer_name}/{turn_num}")
def turn(request: Request, dealer_name, turn_num):
    dir_path = LOGS_DIR + dealer_name
    file_path = f"{dir_path}/{turn_num}.log"
    if not os.path.exists(file_path) or not os.path.exists(
            f"{dir_path}/game_data.json"):
        raise HTTPException(status_code=404, detail="log_not_found")
    with open(f"{dir_path}/game_data.json") as f:
        game_data = json.load(f)
    base_players = game_data["players"]

    with open(file_path) as f:
        lines = f.readlines()

    for l in lines:
        activity = Activity(json.loads(l))
        if activity.event == "first-player":
            turn = Turn(activity)
            turn.activities.append(activity)
        elif activity.event == "finish-turn":
            turn.activities.append(activity)
        elif activity.event == "disconnect":
            if "turn" in locals():
                turn.activities.append(activity)
        else:
            turn.activities.append(activity)

    res_list, player_code_list = turn.make_activities()
    players = [base_players[p] for p in player_code_list]

    return templates.TemplateResponse(
        "turn.html", {
            "request": request,
            "dealer_name": dealer_name,
            "turn_num": turn_num,
            "players": players,
            "res_list": res_list
        })


@app.get("/{dealer_name}/{turn_num}/transformed")
def transformed_turn(request: Request, dealer_name, turn_num):
    dir_path = LOGS_DIR + dealer_name
    file_path = f"{dir_path}/{turn_num}.log"
    if not os.path.exists(file_path) or not os.path.exists(
            f"{dir_path}/game_data.json"):
        raise HTTPException(status_code=404, detail="log_not_found")
    with open(f"{dir_path}/game_data.json") as f:
        game_data = json.load(f)
    base_players = game_data["players"]

    with open(file_path) as f:
        lines = f.readlines()

    for l in lines:
        activity = Activity(json.loads(l))
        if activity.event == "first-player":
            turn = Turn(activity)
            turn.activities.append(activity)
        elif activity.event == "finish-turn":
            turn.activities.append(activity)
        elif activity.event == "disconnect":
            if "turn" in locals():
                turn.activities.append(activity)
        else:
            turn.activities.append(activity)

    unpersed_turn = UnparsedTurn(turn)
    res_list, player_code_list = unpersed_turn.make_activities()
    players = [base_players[p] for p in player_code_list]

    return templates.TemplateResponse(
        "transformed_turn.html", {
            "request": request,
            "dealer_name": dealer_name,
            "turn_num": turn_num,
            "players": players,
            "res_list": res_list
        })


if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8001)
