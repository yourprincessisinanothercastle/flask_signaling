"""
simple signaling server
"""

import uuid
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, send
import logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config['SECRET_KEY'] = uuid.uuid4()
io = SocketIO(app)

clients = []

socket_game = {
    #"<socket_id>": "game_name"
}

game_details = {
    #"game_name": {
    #    "server": "<socketId>"
    #}
    'test': {
        'server': "123"
    }
}


def _remove_game(socket_id):
    if socket_game.get(socket_id, False):
        game_name = socket_game[socket_id]
        del game_details[game_name]
        del socket_game[socket_id]
        return True

    return False


def _add_game(name, socket_id):
    socket_game[socket_id] = name
    game_details[name] = {
        "server": socket_id,
    }


@io.on('connect')
def connected():
    clients.append(request.sid)
    logging.info('%s connected (%s clients)' % (request.sid, len(clients)))
    get_games()


@io.on('disconnect')
def disconnect():
    session_id = request.sid
    clients.remove(session_id)
    if _remove_game(session_id):
        logging.info('server closed')
    else:
        logging.info("client disconnected")


@io.on('open_game')
def open_game(data):
    name = data['game_name']
    _add_game(name, request.sid)
    get_games()


@io.on('get_games')
def get_games():
    emit('games', game_details, broadcast=True)


@io.on('message')
def message(data, target):
    """
    relays to data['target']
    """
    target = target
    source = request.sid
    
    emit('message', {'from': source, 'data': data}, room=target)


if __name__ == '__main__':
    io.run(app, debug=True)
