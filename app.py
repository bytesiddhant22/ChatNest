from flask import Flask , render_template , redirect , url_for , request
from flask_login import LoginManager , login_user , login_required , logout_user , current_user 
from flask_socketio import SocketIO
from werkzeug.security import generate_password_hash , check_password_hash
from models import db , User , Message
from message import handle_message
from dotenv import load_dotenv
import os

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
    messages = Message.query.all()
    return render_template('index.html' , messages=messages)

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

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@socketio.on('message')
def on_message(msg):
    handle_message(msg , current_user.username)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app , debug=True)
