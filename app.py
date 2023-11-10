from flask import Flask,url_for
app = Flask(__name__)

@app.route('/')
def hello(name):
    return 'Hello'

@app.route('/user/<name>')
def user_page(name):
    return '%s' % name

@app.route('/test')
def test_url_for():
    print(url_for('hello'))
    print(url_for('user_page',name='lpa'))
    print(url_for('test_url_for'))
    print(url_for('test_url_for',num=2))
    return 'Test page'