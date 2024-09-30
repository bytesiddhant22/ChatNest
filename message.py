from flask_socketio import emit , join_room
from models import db, Message, User
from flask_login import current_user
from datetime import datetime
import pytz
from datetime import datetime , timedelta , timezone

def convertime(dbtime):
    if dbtime.tzinfo is None:
        dbtime = dbtime.replace(tzinfo=timezone.utc)  
    ist = pytz.timezone('Asia/Kolkata')
    return dbtime.astimezone(ist)


def format_time_for_chat(timestamp):
    now = datetime.now(pytz.timezone('Asia/Kolkata'))  
    diff = now - timestamp

    if diff < timedelta(minutes=1):
        return "Just now"
    elif diff < timedelta(hours=1):
        minutes = diff.seconds // 60
        return f"{minutes} minutes ago"
    elif diff < timedelta(hours=24) and timestamp.date() == now.date():
        return timestamp.strftime('%H:%M') 
    else:
        return timestamp.strftime('%b %d, %Y, %I:%M %p')  


def handle_message(data):
    msg = data['message']
    room_id = data['room_id']
    user = User.query.get(current_user.id)

    new_message = Message(content=msg, user_id=current_user.id, chat_room_id=room_id)
    db.session.add(new_message)
    db.session.commit()

    ist_timestamp = convertime(new_message.timestamp)

    formatted_timestamp = format_time_for_chat(ist_timestamp)

    emit('message', {
        'message': msg,
        'username': user.username,
        'timestamp': formatted_timestamp  
    }, room=room_id)

def handle_join(data):
    room_id = data['room_id']
    user = User.query.get(current_user.id)
    
    join_room(room_id)

    ist = pytz.timezone('Asia/Kolkata')
    timestamp = datetime.now(ist).strftime('%H:%M')

    emit('message', {'message': f'{user.username} has joined the room.', 'timestamp': timestamp , 'username':"System"}, room=room_id)