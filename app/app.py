from flask import Flask, render_template, session, copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, rooms, leave_room, close_room, disconnect
from threading import Lock

async_mode = None
RC = 'receive_count'

app = Flask(__name__)
socketio = SocketIO(app, async_mode=async_mode)
app.config['SECRET_KEY'] = 'Secret Key'

thread = None
thread_lock = Lock()

def background_thread():
    count = 0
    while True:
        socketio.sleep(10)
        count+=1
        socket.emit('my response', {"data": 'Server Generated Event', "count": count, namespace :"/test"})



def getRC():
    return session.get(RC, 0) + 1;

@app.route("/")
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

@socketio.on('my_event', namespace='/test')
def test_message(message):
    session[RC] = getRC()
    emit('my_response', {"data": message["data"], "count": session[RC]})

@socketio.on('my_broadcast_event', namespace="/test")
def test_broadcast_messsage(message):
    session[RC] = getRC()
    print("my_broadcast_event", message)
    emit('my_response', {"data": message["data"], "count": session[RC]}, broadcast=True)

@socketio.on('join', namespace="/test")
def join(message):
    join_room(message['room'])
    session[RC] = getRC()
    emit('my_response', {'data': 'In rooms: ' + ', '.join(rooms()), "count": session[RC]})

@socketio.on('leave', namespace="/test")
def leave(message):
    leave_room(message['room'])
    session[RC] = getRC()
    emit('my_response', {'data': 'In rooms: ' + ', '.join(rooms()), "count": session[RC]})

@socketio.on("close_room", namespace="/test")
def close(message):
    session[RC] = getRC()
    emit('my_response', {'data': 'Room ' + message["room"] + ' is closing', "count": session[RC]})
    close_room(message["room"])


@socketio.on('my_room_event', namespace="/test")
def send_room_message(message): 
    print("my_room_event", message)
    session[RC] = getRC()
    emit('my_response', {'data': message["data"], "count": session[RC]}, room=message['room'])


@socketio.on('connect', namespace="/test")
def test_connect():
    print("client connected")
    emit('my response', {"data":"connected"})

@socketio.on('disconnect_request', namespace="/test")
def test_disconnect():
    @copy_current_request_context
    def can_disconnect():
        disconnect()

    session[RC] = getRC()
    # for this emit we use a callback function
    # when the callback function is invoked we know that the message has been
    # received and it is safe to disconnect
    emit('my_response',
         {'data': 'Disconnected!', 'count': session[RC]},
         callback=can_disconnect)


if __name__ == '__main__':
    socketio.run(app)