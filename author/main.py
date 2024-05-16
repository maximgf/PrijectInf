from flask import Flask
from flask import jsonify
from flask import request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Boolean, DateTime
import datetime
import uuid
import re



app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///author.db'
db = SQLAlchemy(app)


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
def Add_author_func():

    data = request.get_json()
    id = str(uuid.uuid4())
    first_name = data.get("first_name")
    last_name = data.get("last_name")

    if (re.search(r'\d', first_name) or re.search(r'\d', last_name)) or (len(first_name) > 20 or len(last_name) > 20):
        return jsonify({"error": "First name or last name is not valid"}), 400
    
    new_task = Add_author(id = id,
                        username = data.get("username"), 
                        requested_by = data.get("requested_by"),
                        first_name = data.get("first_name"),
                        last_name = data.get("last_name"),
                        completed = False,
                        created_at = datetime.datetime.utcnow().replace(microsecond=0)
                        )
    
    db.session.add(new_task)
    db.session.commit()
    
    return {"id":id} 



@app.route('/all_user_request', methods=['POST'])
def all_user_request():

    username = request.args.get("username")
    authors = Add_author.query.filter_by(username=username).all()
    
    if authors:
    
        authors = [author.to_dict() for author in authors]
        return jsonify(authors),200
    
    else:
        return jsonify({"error": "Requests not found"}), 404

@app.route('/nlastrequests', methods=['POST'])
def n_last_requests():
    
    #/nlastrequests?complete=1
    complete = request.args.get("complete")
    n = request.args.get("count")
    if n is None:
        n = 1

    if complete != None:
        requests = Add_author.query.filter(Add_author.completed == complete).order_by(Add_author.created_at.desc()).limit(n).all()
    else:
        requests = Add_author.query.order_by(Add_author.created_at.desc()).limit(n).all()

    if requests:
        
        requests = [reques.to_dict() for reques in requests]
        return jsonify(requests), 200
    
    else:
        return jsonify({"error": "No requests found"}), 404
    

@app.route('/mark', methods=['POST'])
def mark():
    id = request.args.get("id")
    
    user_id = request.args.get("user_id")   

    reques = Add_author.query.filter_by(id=id).first()

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
    


if __name__ == '__main__':
  app.run(debug=True)