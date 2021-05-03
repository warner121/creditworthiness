import logging
import json
import pandas as pd

from flask import Flask, jsonify, request
from flask_json_schema import JsonSchema, JsonValidationError

from classes.scorecard import Scorecard
from classes.expenditure import ONSExpenditure
#from classes.pricing import Pricing

# instantiate the application and validation schema
app = Flask(__name__)
schema = JsonSchema(app)

# instantiate the scorecard and expenditure calculators
scorecard = Scorecard()
scorecard.fit()
onsexpenditure = ONSExpenditure()
onsexpenditure.fit()

# load schemas
with open('schemas/expenditure.json') as json_data:
    expenditure_schema = json.load(json_data)
    json_data.close()
with open('schemas/scorecard.json') as json_data:
    scorecard_schema = json.load(json_data)
    json_data.close()
with open('schemas/pricing.json') as json_data:
    pricing_schema = json.load(json_data)
    json_data.close()

# validator error handling
@app.errorhandler(JsonValidationError)
def validation_error(e):
    return jsonify({ 'error': e.message, 'errors': [validation_error.message for validation_error in e.errors]})

# define routes
@app.route('/creditworthiness/api/v1.0/expenditure', methods=['POST'])
@schema.validate(expenditure_schema)
def expenditure():
    if not request.json: abort(400)
    df = pd.DataFrame(request.get_json())
    response = {'expenditure': onsexpenditure.predict(df).to_dict(orient='records')}
    return jsonify(response)

@app.route('/creditworthiness/api/v1.0/scorecard', methods=['POST'])
def scorecard_predict():
    if not request.json: abort(400)
    df = pd.DataFrame(request.get_json(), columns=scorecard._xcolumns)
    response = {'predictions_good': scorecard.predict(df).tolist()}
    return jsonify(response)

@app.route('/creditworthiness/api/v1.0/scorecard_proba', methods=['POST'])
@schema.validate(scorecard_schema)
def scorecard_predict_proba():
    if not request.json: abort(400)
    df = pd.DataFrame(request.get_json(), columns=scorecard._xcolumns)
    response = {'prediction_probabilities': scorecard.predict_proba(df).tolist()}
    return jsonify(response)

@app.route('/creditworthiness/api/v1.0/pricing', methods=['POST'])
@schema.validate(pricing_schema)
def pricing():
    if not request.json: abort(400)
    json = request.get_json()
    expenditure = expenditure()
    pricing = Pricing(json)
    pricing.calculate_credit_risk(scorecard)
    pricing.calculate_expenditure(expenditure)
    response = pricing.get_suitable_products(-12500).reset_index()
    response = response.groupby(
        ['Application identifier', 'Credit amount', 'Duration'])['Interest rate','Monthly payment'].first().reset_index()
    print(response.columns)
    response = response.groupby(
        ['Application identifier', 'Credit amount'])['Duration'].first().reset_index()
    print(response.columns)
    response = response.groupby(
        ['Application identifier'])['Credit amount'].first()
    response = response.tolist()
    return jsonify(response)

# run the application
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True)