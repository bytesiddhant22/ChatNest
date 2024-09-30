from flask_socketio import emit , join_room
from models import db, Message, User
from flask_login import current_user
from datetime import datetime
import pytz

def handle_message(data):
    msg = data['message']
    room_id = data['room_id']
    user = User.query.get(current_user.id)

    new_message = Message(content=msg, user_id=current_user.id, chat_room_id=room_id)
    db.session.add(new_message)
    db.session.commit()

    utc_timestamp = new_message.timestamp.isoformat()

    emit('message', {
        'message': msg, 
        'username': user.username, 
        'timestamp': utc_timestamp
    }, room=room_id)

def handle_join(data):
    room_id = data['room_id']
    user = User.query.get(current_user.id)
    
    join_room(room_id)

    ist = pytz.timezone('Asia/Kolkata')
    timestamp = datetime.now(ist).strftime('%H:%M')

    emit('message', {'message': f'{user.username} has joined the room.', 'timestamp': timestamp , 'username':"System"}, room=room_id)
