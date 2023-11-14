from flask import Flask,url_for,render_template
from flask_sqlalchemy import SQLAlchemy
import click

#if test connection needed
from sqlalchemy import text

app = Flask(__name__)

HOSTNAME = "localhost"
PORT = 3306
USERNAME = "root"
PASSWD = "Lpa112211"
DATABASE = "Test"
app.config['SQLALCHEMY_DATABASE_URI']=f"mysql+pymysql://{USERNAME}:{PASSWD}@{HOSTNAME}/{DATABASE}?charset=utf8mb4"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

db = SQLAlchemy(app)

# if connection is extablished, (1,) is expected to see in the terminal
# with app.app_context():
#     with db.engine.connect() as conn:
#         rs = conn.execute(text("select 1"))
#         print(rs.fetchone())

class User(db.Model):
    # __tablename__ = 'users' #指定表名
    #表的列（属性）
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))

class Movie(db.Model): # 表名将会是 movie
    id = db.Column(db.Integer, primary_key=True) # 主键
    title = db.Column(db.String(60)) # 电影标题
    year = db.Column(db.String(4)) # 电影年份

@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')

def initdb(drop):
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')

#可以直接flask initdb 来运行initdb，可以加上选项--drop

'''
如何向数据库添加记录
>>> from app import User, Movie # 导入模型类
>>> user = User(name='Grey Li') # 创建一个 User 记录
>>> m1 = Movie(title='Leon', year='1994') # 创建一个 Movie 记录
>>> m2 = Movie(title='Mahjong', year='1996') # 再创建一个 Movie
记录
>>> db.session.add(user) # 把新创建的记录添加到数据库会话
>>> db.session.add(m1)
>>> db.session.add(m2)
>>> db.session.commit() # 提交数据库会话，只需要在最后调用一次即可
'''

# --------example of static settings------------
@app.route('/')
def index():
    # user = User.query.first()
    movies = Movie.query.all()
    return render_template('index.html', movies=movies)
    # return render_template('index.html', user=user, movies=movies)
    # use if context processor disabled
    
# --------example of static settings------------

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
@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)
#-----------------context processor----------------