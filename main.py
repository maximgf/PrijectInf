from flask import Flask
from flask import render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
db = SQLAlchemy(app)

id = 1

username = 'masya'

user = 'user'

admin = 'admin'


@app.route('/book',methods = ['GET'])
def show_form_book():
    return render_template('AddBook.html')


@app.route('/author',methods = ['GET'])
def show_form_author():
    return render_template('AddAuthor.html')


class Add_book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10), unique=False, nullable=False)
    username = db.Column(db.String(20), unique=False, nullable=False)
    book = db.Column(db.String(20), unique=False, nullable=False)
    surname = db.Column(db.String(20), unique=False, nullable=False)


@app.route('/submitbook', methods=['POST'])
def Add_book_func():
  book = request.form['book']
  author = request.form['surnameauthor']
  return f'add book: {book} {author}'



#//////////////////////////////////////////



class Add_author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10), unique=False, nullable=False)
    username = db.Column(db.String(20), unique=False, nullable=False)
    name = db.Column(db.String(20), unique=False, nullable=False)
    surname = db.Column(db.String(20), unique=False, nullable=False)


@app.route('/submitauthor', methods=['POST'])
def Add_author_func():
  name = request.form['nameauthor']
  surname = request.form['surnameauthor']
  return f'add author: {name} {surname}'



if __name__ == '__main__':
  app.run(debug=True)