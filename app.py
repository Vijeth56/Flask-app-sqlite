from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///user.db"
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100))
    status = db.Column(db.String(20))  # "assigned", "in-progress", "done"
    deadline = db.Column(db.Date, nullable=True)  # New deadline field
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'status': self.status,
            'deadline': self.deadline.strftime('%Y-%m-%d') if self.deadline else None  # Format date
        }

@app.route("/", methods=['GET'])
def index():
    return render_template("index.html")

@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.json
    description = data.get('description')
    deadline_str = data.get('deadline')  # Get the deadline string

    # Convert the string to a date object
    deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date() if deadline_str else None

    new_task = Task(description=description, status="assigned", deadline=deadline)
    db.session.add(new_task)
    db.session.commit()
    return jsonify(success=True, task={
        'id': new_task.id,
        'description': new_task.description,
        'status': new_task.status,
        'deadline': new_task.deadline.strftime('%Y-%m-%d') if new_task.deadline else None
    })



@app.route('/tasks/<status>', methods=['POST'])
def move_task(status):
    data = request.json
    task_id = data.get('id')
    task = Task.query.get(task_id)
    if task and status in ["assigned", "in-progress", "done"]:
        task.status = status
        db.session.commit()
        return jsonify(success=True)
    return jsonify(success=False), 400

def get_tasks():
    tasks = {
        "assigned": [task.to_dict() for task in Task.query.filter_by(status="assigned").all()],
        "in-progress": [task.to_dict() for task in Task.query.filter_by(status="in-progress").all()],
        "done": [task.to_dict() for task in Task.query.filter_by(status="done").all()]
    }
    return tasks

@app.route('/tasks-data')
def tasks_data():
    return jsonify(get_tasks())

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
        return jsonify(success=True)
    return jsonify(success=False), 404

# teams route 

@app.route("/teams", methods=['GET'])
def teams():
    return render_template("teams.html")

@app.route('/users', methods=['POST'])
def add_user():
    data = request.json
    username = data.get('username')
    if username:
        new_user = User(username=username)
        db.session.add(new_user)
        db.session.commit()
        return jsonify(success=True)
    return jsonify(success=False), 400

@app.route('/users-data', methods=['GET'])
def users_data():
    users = User.query.all()
    return jsonify([{'id': user.id, 'username': user.username} for user in users])

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)