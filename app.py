# for all
from flask import Flask,url_for,render_template, request, flash, redirect
# for all
from flask_sqlalchemy import SQLAlchemy
# login 
from flask_login import LoginManager, UserMixin, login_user
#logout
from flask_login import logout_user
# view protect
from flask_login import login_required, current_user
# password for user
from werkzeug.security import generate_password_hash, check_password_hash
# args in terminal
import click
#test connection
from sqlalchemy import text

app = Flask(__name__)

HOSTNAME = "localhost"
PORT = 3306
USERNAME = "root"
PASSWD = "Lpa112211"
DATABASE = "Test"
app.config['SQLALCHEMY_DATABASE_URI']=f"mysql+pymysql://{USERNAME}:{PASSWD}@{HOSTNAME}/{DATABASE}?charset=utf8mb4"
app.config['SECRET_KEY'] = '123456'
# app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

db = SQLAlchemy(app)
# if connection is extablished, (1,) is expected to see in the terminal
# with app.app_context():
#     with db.engine.connect() as conn:
#         rs = conn.execute(text("select 1"))
#         print(rs.fetchone())

#--------------------table setting--------------------
class User(db.Model, UserMixin):
    # __tablename__ = 'users' #指定表名
    #表的列（属性）
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(256))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

class Movie(db.Model): # 表名将会是 movie
    id = db.Column(db.Integer, primary_key=True) # 主键
    title = db.Column(db.String(60)) # 电影标题
    year = db.Column(db.String(4)) # 电影年份
#--------------------table setting--------------------

#------------------initialize database-----------------------
@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')
#可以直接flask initdb 来运行initdb，可以加上选项--drop
#------------------initialize database-----------------------

# --------example of static settings(Home page)------------
@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash('You have to login.')
            return redirect(url_for('index'))
        title = request.form.get('title')
        year = request.form.get('year')
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('index'))

        movie = Movie(title=title, year=year)
        db.session.add(movie)
        db.session.commit()
        flash('Item created.')
        return redirect(url_for('index'))    
    # user = User.query.first()
    movies = Movie.query.all()
    return render_template('index.html', movies=movies, current_user=current_user)
    # return render_template('index.html', user=user, movies=movies)
    # use if context processor disabled
# --------example of static settings(Home page)------------

# --------example of dynamic settings------------
# @app.route('/user/<name>')
# def user_page(name):
#     return '%s' % name

# @app.route('/test')
# def test_url_for():
#     print(url_for('hello'))
#     print(url_for('user_page',name='lpa'))
#     print(url_for('test_url_for'))
#     print(url_for('test_url_for',num=2))
#     return 'Test page'
# --------example of dynamic settings------------

#--------------------edit info--------------------
@app.route('/movie/edit/<int:movie_id>', methods=['GET','POST'])
@login_required
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    
    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']
        
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=movie_id))
        
        movie.title = title
        movie.year = year
        db.session.commit()
        flash('Item updated.')
        return redirect(url_for('index'))
    
    return render_template('edit.html',movie=movie)
#--------------------edit info--------------------

#--------------------del info--------------------
@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
@login_required
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted.')
    return redirect(url_for('index'))
#--------------------del info--------------------

#--------------------generate fake info--------------------
@app.cli.command()
def forge():
    """Generate fake data"""
    db.create_all()
    
    name = 'Peiao Luo'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]
    
    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'],year=m['year'])
        db.session.add(movie)
    
    db.session.commit()
    click.echo('Done.')
#--------------------generate fake info--------------------

#-----------------error dealing------------------- 
@app.errorhandler(404)
def page_not_found(e):
    # user = User.query.first()
    return render_template('404.html'), 404
    # return render_template('404.html', user=user), 404 
    # use if context_processor disabled
#-----------------error dealing-------------------    

#-----------------context processor----------------
# this will pass the varible returned by the function into other place where
# render_template is used
# if base template use variable A, then A should be conclude in context_processor
@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)
#-----------------context processor----------------

#-----------------adim user create-----------------
@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    db.create_all()
    
    user = User.query.first()
    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password)
    else:
        click.echo('Creating user...')
        user = User(username=username, name='Admin')
        user.set_password(password)
        db.session.add(user)
    
    db.session.commit()
    click.echo('Done.')
#-----------------adim user create-----------------

login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    user = db.session.query(User).get(int(user_id))
    return user
login_manager.login_view = 'login'

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))
        
        user = User.query.first()
        if username == user.username and user.validate_password(password):
            login_user(user)
            flash('Login success.')
            return redirect(url_for('index'))
        
        flash('Invalid username or password.')
        return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Bye.')
    return redirect(url_for('index'))

@app.route('/settings',methods=['POST','GET'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))
        
        current_user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))
    
    return render_template('settings.html', current_user=current_user) # 不需要传入current？
