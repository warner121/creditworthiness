from flask import Flask, jsonify, request
from flask_json_schema import JsonSchema, JsonValidationError
from resources.affordability import Affordability
from resources.scorecard import Scorecard

import json

# instantiate the application and validation schema
app = Flask(__name__)
schema = JsonSchema(app)

# instantiate and train the scorecard
scorecard = Scorecard()
scorecard.train()

# define schema for affordability
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

# validator error handling
@app.errorhandler(JsonValidationError)
def validation_error(e):
    return jsonify({ 'error': e.message, 'errors': [validation_error.message for validation_error in e.errors]})
    
# define routes
@app.route('/creditworthiness/api/v1.0/net_disposable_income', methods=['GET'])
def net_disposable_income():
    a = Affordability()
    net_disposable_income = a.getNetDisposableIncome()
    return jsonify({'net_disposable_income': net_disposable_income})

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
    return jsonify({'affordability': affordability})

@app.route('/creditworthiness/api/v1.0/scorecard/predict-file/<string:calculation>', methods=['GET'])
def scorecard_predict(calculation):
    if calculation == 'class':
        prediction = scorecard.predictFromFile('resources/scorecardtest.json', proba=False)
    elif calculation == 'probability':
        prediction = scorecard.predictFromFile('resources/scorecardtest.json', proba=True)
    else:
        make_response(jsonify({'error': 'Not found'}), 404)
    return jsonify({'prediction': prediction.tolist()})

@app.route('/creditworthiness/api/v1.0/scorecard/predict-json/<string:calculation>', methods=['POST'])
def scorecard_predict_json(calculation):
    json = [request.get_json()]
    if calculation == 'class':
        prediction = scorecard.predictFromJson(json, proba=False)
    elif calculation == 'probability':
        prediction = scorecard.predictFromJson(json, proba=True)
    else:
        make_response(jsonify({'error': 'Not found'}), 404)
    return jsonify({'prediction': prediction.tolist()})

# run the application
if __name__ == '__main__':
    app.run(debug=True)