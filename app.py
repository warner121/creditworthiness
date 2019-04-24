from flask import Flask, jsonify
from flask import make_response
from resources.affordability import Affordability

app = Flask(__name__)

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol', 
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web', 
        'done': False
    }
]

@app.route('/todo/api/v1.0/tasks', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': tasks})

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        return make_response(jsonify({'error': 'Not found'}), 404)
    return jsonify({'task': task[0]})

@app.route('/creditworthiness/api/v1.0/net_disposable_income', methods=['GET'])
def net_disposable_income():
    a = Affordability()
    net_disposable_income = a.getNetDisposableIncome()
    return jsonify({'net_disposable_income': net_disposable_income})

if __name__ == '__main__':
    app.run(debug=True)