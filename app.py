from flask import Flask
from flask import render_template, request, redirect ,url_for
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import os
import settings

#データベース情報
DB_USER = settings.DB_USER
DB_PASSWORD=  settings.DB_PASSWORD,
DB_HOST =  settings.DB_HOST,
DB_NAME =  settings.DB_NAME

 
 
db_uri = 'postgresql+psycopg2://{user}:{password}@{host}/{name}'.format(**{
    'user': settings.DB_USER,
    'password': settings.DB_PASSWORD,
    'host': settings.DB_HOST,
    'name': settings.DB_NAME
})

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin , db.Model):
    __tablename__ = 'todouser'
    id = db.Column(db.Integer, primary_key=True , autoincrement=True)
    name = db.Column(db.Text())
    password = db.Column(db.Text())
    
class Todo(db.Model):
    __tablename__ = 'todolist'
    userid = db.Column(db.Integer)
    id = db.Column(db.Integer , primary_key = True , autoincrement = True)
    todo = db.Column(db.Text())
    date = db.Column(db.DateTime)
   

@app.route('/')
def index():
    return redirect ('/login')
         
@app.route('/todoList/<int:id>', methods=['GET','POST'])
@login_required
def userpage(id):
    if request.method == 'GET':
        user = db.session.query(User).get(id)
        todos = db.session.query(Todo).filter(Todo.userid == id)
        return render_template('home.html' , todos = todos , name = user.name , userid=id )

@login_manager.unauthorized_handler
def unauthorized():
    return redirect('/login')
 
    
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    logout_user()
    
    if request.method == "POST":
        name = request.form.get('name')
        password = request.form.get('password')
        retype = request.form.get('passwordRetype')
        
        if retype != password:
            message = "パスワードが一致してません"
            return render_template('signup.html' , message = message)
        
        else:
            # Userのインスタンスを作成
            try:
                user = User(name=name, password=generate_password_hash(password, method='sha256'))
                db.session.add(user)
                db.session.commit()
                return redirect( url_for('login' , name = name ))
            
            except Exception as e :
                return render_template('signup.html' , message="このユーザ名は既に使用されています")
    else:
        return render_template('signup.html')
    
    
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == "POST":
        name = request.form.get('name')
        password = request.form.get('password')
        # Userテーブルからusernameに一致するユーザを取得
        user = User.query.filter_by(name=name).first()
        
        try:
            if check_password_hash(user.password, password):
                login_user(user)
                
                id = user.id
                name = user.name
                return redirect(url_for('userpage' , id = id , message='null'))
            
            else:
                message = "ユーザ名またはパスワードが間違っています"
                return render_template('login.html' , message = message)
        except :
            message = "ユーザ名またはパスワードが間違っています"
            return render_template('login.html' , message = message)
        
    else:
        return render_template('login.html' ,  message = '')
    
 
@app.route('/logout')
@login_required
def logout():
    logout_user()
    
    return redirect(url_for('login'))

@login_manager.unauthorized_handler
def unauthorized():
    return redirect('/login')

@app.route('/remove' ,  methods=['POST'])
def destory():
    todoId = request.form.get('id').split('.')
    userid = int(todoId[0]) 
    id = int(todoId[1])
    todo = Todo.query.get(id)
    db.session.delete(todo)
    db.session.commit()
    
    message='タスクを削除しました'
    return redirect(url_for('userpage' , id = userid , message = message))

@app.route('/add' ,  methods=['POST'])
def create():
    
    userid = request.form['id']
    todoname = request.form['todoname']
    date = request.form['date']
    
    
    if todoname == '':
        message = 'スク名を入力してください'
        return redirect(url_for('userpage' , id = userid , message = message))
    
    
    if date =='':
        date = '未設定'
        
    todo = Todo()
    todo.userid = userid
    todo.todo = todoname
    todo.date = date
    
    db.session.add(todo)
    db.session.commit()

    message ="タスクを追加しました"
    return redirect(url_for('userpage' , id = userid , message = message))
    

if __name__ == '__main__':
    app.run()