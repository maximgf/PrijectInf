from flask import Flask
from flask import jsonify
from flask import request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Boolean, DateTime
import datetime
import uuid
import re
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity,get_jwt_header,get_jwt
from sqlalchemy import event
from sqlalchemy.engine import Engine
import time

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())
    print(f"\nStarting query at {datetime.datetime.now()}")

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    start_time = sum(conn.info.pop('query_start_time', []))
    execution_time = time.time() - start_time
    print(f"\nQuery executed at {datetime.datetime.now()}.")
    print(f"\nTime taken: {execution_time} seconds")
    print(f"\nSQL Query: {statement}")
    if parameters:
        print(f"\nParameters: {parameters}")

secret = 'pidorasipidorasipidorasipidorasi'

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///author.db'
app.config['JWT_SECRET_KEY'] = secret  # Используйте ваш секретный ключ
#app.config['JWT_IDENTITY_CLAIM'] = "0"

jwt = JWTManager(app)
db = SQLAlchemy(app)
status_key = 'http://schemas.microsoft.com/ws/2008/06/identity/claims/role'
username_key = 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name'

class Add_author(db.Model):

    id = Column(String, primary_key=True)
    username = Column(String)
    requested_by = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    completed = Column(Boolean)
    added_author_id = Column(String)
    created_at = Column(DateTime)
    completed_at = Column(DateTime)
    completed_by = Column(String)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'requested_by': self.requested_by,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'completed': self.completed,
            'added_author_id': self.added_author_id,
            'created_at': self.created_at,#.isoformat() if self.created_at else None,
            'completed_at': self.completed_at,#.isoformat() if self.completed_at else None,
            'completed_by': self.completed_by,
        }

with app.app_context():
    if not db.engine.dialect.has_table(db.engine.connect(), "add_author"):
        db.create_all()



@app.route('/add_author', methods=['POST'])
@jwt_required()
def Add_author_func():
    current_user = get_jwt()
    id = str(uuid.uuid4())
    first_name = current_user.get("first_name")
    last_name = current_user.get("last_name")

    if (first_name is None or last_name is None) or (re.search(r'\d', first_name) or re.search(r'\d', last_name)) or (len(first_name) > 20 or len(last_name) > 20):
        return jsonify({"error": "First name or last name is not valid"}), 400
    
    new_task = Add_author(id = id,
                        username = current_user.get(username_key), 
                        requested_by = current_user.get("sub"),
                        first_name = current_user.get("first_name"),
                        last_name = current_user.get("last_name"),
                        completed = False,
                        created_at = datetime.datetime.utcnow().replace(microsecond=0)
                        )
    
    db.session.add(new_task)
    db.session.commit()
    
    return {"id":id} 



@app.route('/', methods=['GET'])
@jwt_required()
def request_output():
    current_user = get_jwt()
    username = request.args.get(username_key)
    complete = request.args.get("complete")
    n = request.args.get("count")

    if n is None:
        n = 1
    if current_user.get(status_key) != 'admin':

        authors = Add_author.query.filter_by(username=username).order_by(Add_author.created_at.desc()).limit(n).all()
        if authors:
        
            authors = [author.to_dict() for author in authors]
            return jsonify(authors),200
        
        else:
            return jsonify({"error": "No requests found"}), 404
    else:


        if complete is not None and complete in ['True', 'False']:
            complete = complete == 'True'  # Преобразуем строку в булево значение
            requests = Add_author.query.filter(Add_author.completed == complete).order_by(Add_author.created_at.desc()).limit(n).all()
        else:
            requests = Add_author.query.order_by(Add_author.created_at.desc()).limit(n).all()

        if requests:
            requests = [reques.to_dict() for reques in requests]
            return jsonify(requests), 200
        else:
            return jsonify({"error": "No requests found"}), 404
    

@app.route('/', methods=['PATCH'])
@jwt_required()
def mark():
    current_user = get_jwt()
    if current_user.get(status_key) == 'admin':
        id = request.args.get("id")
        user_id = current_user.get("sub")  

        reques = Add_author.query.filter_by(id=id).first()

        if reques is None:
            return jsonify({"error": "Request not found"}), 404

        if reques.completed:
            return jsonify({"error": "Request is completed"}), 404 
        
        if reques:
    
            reques.completed = True
            reques.completed_at = datetime.datetime.utcnow().replace(microsecond=0)
            reques.completed_by = user_id
            
            existing_author = Add_author.query.filter_by(first_name=reques.first_name, last_name=reques.last_name).first()
            
            if existing_author:
                reques.added_author_id = existing_author.id
            else:
                reques.added_author_id = str(uuid.uuid4())

            db.session.commit()

            return jsonify({"message": "Request marked successfully"}), 200
        
        else:
            return jsonify({"error": "Request not found"}), 404
    else:
        return jsonify({"error": "Not prav"}), 404 
    


if __name__ == '__main__':
  app.run(debug=True)