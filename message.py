from flask_socketio import send
from flask_login import current_user
from models import db , Message

def handle_message(msg , username):
    new_msg = Message(user_id=current_user.id , content=msg)
    db.session.add(new_msg)
    db.session.commit()
    send({'message': msg, 'username': username}, broadcast=True)
