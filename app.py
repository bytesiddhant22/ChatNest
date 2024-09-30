from flask import Flask , render_template , redirect , url_for , request
from flask_login import LoginManager , login_user , login_required , logout_user , current_user 
from flask_socketio import SocketIO , join_room , emit
from werkzeug.security import generate_password_hash , check_password_hash
from models import db , User , Message , ChatRoom
from message import handle_message , handle_join
from dotenv import load_dotenv
import os
import pytz
from datetime import timezone , datetime , timedelta

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
socketio = SocketIO(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    chat_rooms = ChatRoom.query.all()
    return render_template('index.html', chat_rooms=chat_rooms)

def convertime(dbtime):
    if dbtime.tzinfo is None:
        dbtime = dbtime.replace(tzinfo=timezone.utc) 
    ist = pytz.timezone('Asia/Kolkata')
    return dbtime.astimezone(ist)

def formatTimeForChat(timestamp):
    now = datetime.now(pytz.timezone('Asia/Kolkata'))
    diff = now - timestamp

    if diff < timedelta(minutes=1):
        return "Just Now"
    elif diff < timedelta(hours=1):
        minutes = diff.seconds // 60
        return f"{minutes} minutes ago"
    elif diff < timedelta(hours=24) and timestamp.date() == now.date():
        return timestamp.strftime('%H:%M')  
    else:
        return timestamp.strftime('%b %d, %Y, %I:%M %p')  

@app.route('/chat/<string:roomname>')
@login_required
def chat(roomname):
    room = ChatRoom.query.filter_by(name=roomname).first_or_404()
    messages = Message.query.filter_by(chat_room_id=room.id).all()
    for m in messages:
        istTime = convertime(m.timestamp)
        m.ist_timestamp = formatTimeForChat(istTime)
    return render_template('chat.html', room=room, messages=messages)


@app.route('/login' , methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password , password):
            login_user(user)
            return redirect(url_for('index'))
    
    return render_template('login.html')

def create_default_chat_rooms():
    default_rooms = ['General', 'Technology', 'Anime', 'Movies' , 'Gaming']
    for room_name in default_rooms:
        if not ChatRoom.query.filter_by(name=room_name).first():
            new_room = ChatRoom(name=room_name)
            db.session.add(new_room)
    db.session.commit()

@socketio.on('join')
def on_join(data):
    handle_join(data)


@app.route('/register' , methods =['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        regpassword = generate_password_hash( request.form['password'])
        new_user = User(username=username , password=regpassword)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    
    return render_template('register.html')


@socketio.on('message')
def handle_message_wrapper(data):
    handle_message(data)



@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_default_chat_rooms()
    
    socketio.run(app , debug=True)
