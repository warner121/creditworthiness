from flask import Flask, jsonify, make_response, request
from flask_json_schema import JsonSchema, JsonValidationError
from resources.affordability import Affordability

app = Flask(__name__)
schema = JsonSchema(app)

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

task_schema = {
    'required': ['title'],
    'properties': {
        'id': { 'type': 'integer' },
        'title': { 'type': 'string' },
        'description': { 'type': 'string' },
        'done': { 'type': 'boolean' },
    }
}

affordability_schema = {
    'required': ['monthly_income'],
    'properties': {
        'monthly_income': { 'type': 'integer' },
        'morgage_or_rent': { 'type': 'integer' },
        'monthly_credit_commitments': { 'type': 'integer' },
        'employment_status': { 'type': 'string' },
        'no_of_dependants': { 'type': 'integer' },
        'no_of_adults': { 'type': 'integer' },
    }
}

@app.errorhandler(JsonValidationError)
def validation_error(e):
    return jsonify({ 'error': e.message, 'errors': [validation_error.message for validation_error in e.errors]})
    
@app.route('/todo/api/v1.0/tasks', methods=['POST'])
@schema.validate(task_schema)
def create_task():
    if not request.json:
        abort(400)
    task = {
        'id': tasks[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'done': False
    }
    tasks.append(task)
    return jsonify({'task': task}), 201

@app.route('/creditworthiness/api/v1.0/affordability', methods=['POST'])
@schema.validate(affordability_schema)
def affordability():
    if not request.json:
        abort(400)
    a = Affordability()
    a.setMonthlyIncome(request.json['monthly_income'])
    a.setMortgageOrRent(request.json['mortgage_or_rent'])
    a.setMonthlyCreditCommitments(request.json['monthly_credit_commitments'])
    a.setEmploymentStatus(request.json['employment_status'])
    a.setNoOfDependants(request.json['no_of_dependants'])
    a.setNoOfAdults(request.json['no_of_adults'])
    affordability = a.getAffordability()
    return jsonify({'affordability': affordability}), 201

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