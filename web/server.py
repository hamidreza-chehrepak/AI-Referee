from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from game.game_engine import create_game, apply_legal_move
from game.referee import AIReferee
from game.events import PlayCardEvent


app = FastAPI(title="AI Referee")


app.mount(
    "/static",
    StaticFiles(directory="web/static"),
    name="static",
)


game = create_game()
game.trump = "♠"

referee = AIReferee(game)

players = {}


@app.get("/")
async def home():
    return FileResponse("web/index.html")


async def send_to_player(player, message):
    connection = players.get(player)

    if connection:
        await connection.send_json(message)


async def broadcast(message):
    for connection in list(players.values()):
        await connection.send_json(message)


async def send_player_hand(player):

    if player == game.player1:
        hand = game.player1_cards

    elif player == game.player2:
        hand = game.player2_cards

    else:
        return

    await send_to_player(
        player,
        {
            "type": "HAND",
            "cards": hand,
        },
    )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await websocket.accept()

    player = None

    if "Player 1" not in players:
        player = "Player 1"

    elif "Player 2" not in players:
        player = "Player 2"

    else:
        await websocket.send_json(
            {
                "type": "ERROR",
                "message": "The game is full.",
            }
        )

        await websocket.close()
        return

    players[player] = websocket

    await websocket.send_json(
        {
            "type": "CONNECTED",
            "player": player,
            "message": f"You are {player}.",
        }
    )

    await send_player_hand(player)

    await broadcast(
        {
            "type": "PLAYER_STATUS",
            "player": player,
            "status": "Connected",
        }
    )

    if len(players) == 2:

        await broadcast(
            {
                "type": "GAME_READY",
                "message": "Both players are connected. The game can begin.",
            }
        )

    try:

        while True:

            data = await websocket.receive_json()

            action = data.get("action")

            if action != "PLAY_CARD":

                await websocket.send_json(
                    {
                        "type": "ERROR",
                        "message": "Unknown action.",
                    }
                )

                continue

            card = data.get("card")

            if not card:

                await websocket.send_json(
                    {
                        "type": "ERROR",
                        "message": "No card was provided.",
                    }
                )

                continue

            event = PlayCardEvent(
                player=player,
                card=card,
            )

            result = referee.process_event(event)

            await websocket.send_json(
                {
                    "type": "REFEREE_DECISION",
                    **result,
                }
            )

            if result["decision"] != "LEGAL":
                continue

            success = apply_legal_move(
                game,
                player,
                card,
            )

            if not success:

                await websocket.send_json(
                    {
                        "type": "ERROR",
                        "message": "The legal move could not be applied.",
                    }
                )

                continue

            opponent = (
                game.player2
                if player == game.player1
                else game.player1
            )

            await send_to_player(
                opponent,
                {
                    "type": "OPPONENT_MOVE",
                    "player": player,
                    "card": card,
                    "decision": "LEGAL",
                },
            )

            await send_player_hand(player)

    except WebSocketDisconnect:

        if player in players:
            del players[player]

        await broadcast(
            {
                "type": "PLAYER_STATUS",
                "player": player,
                "status": "Disconnected",
            }
        )