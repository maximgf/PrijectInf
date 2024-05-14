from flask import Flask
from flask import render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Boolean, DateTime
import datetime
import uuid
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///author.db'
db = SQLAlchemy(app)

id = 1

username = 'masya'

uid = '5185b78c-814c-4e3b-b65a-9e0f48f3a1a7'

user = 'admin'

admin = 'admin'

class Add_author(db.Model):
    id = Column(String, primary_key=True)
    username = Column(String(20))
    requested_by = Column(String)
    first_name = Column(String(20))
    last_name = Column(String(20))
    completed = Column(Boolean)
    added_author_id = Column(String)
    created_at = Column(DateTime)
    completed_at = Column(DateTime)
    completed_by = Column(String)
with app.app_context():
    db.create_all()
@app.route('/author',methods = ['GET'])
def show_form_author():
    return render_template('AddAuthor.html')


@app.route('/submitauthor', methods=['POST'])
def Add_author_func():
    new_task = Add_author(id = str(uuid.uuid4()),
                          username = username, 
                          requested_by = uid,
                          first_name = request.form['nameauthor'],
                          last_name = request.form['surnameauthor'],
                          completed = False,
                          created_at = datetime.date.today()
                         )
    db.session.add(new_task)
    db.session.commit()
    return render_template('AddAuthor.html')


@app.route('/authors_table', methods=['GET', 'POST'])
def show_table():
    if request.method == 'POST':
        username = request.form['username']
        # Получаем все строки из таблицы, где requested_by совпадает с username
        authors = Add_author.query.filter_by(username=username).all()
        return render_template('authors_table.html', username=username, authors=authors)
    else:
        return render_template('authors_table.html')


if __name__ == '__main__':
  app.run(debug=True)