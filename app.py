import logging
import json
import pandas as pd

from flask import Flask, jsonify, request
from flask_json_schema import JsonSchema, JsonValidationError

from classes.scorecard import Scorecard
from classes.onsexpenditure import ONSExpenditure
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
@app.route('/creditworthiness/api/v1.0/ons_expenditure', methods=['POST'])
@app.route('/creditworthiness/api/v1.0/ons_expenditure/<option>', methods=['POST'])
@schema.validate(expenditure_schema)
def ons_expenditure(option=''):
    if not request.json: abort(400)
    df = pd.DataFrame(request.get_json())
    if option=='full': response = onsexpenditure.predict(df, False).to_dict(orient='records')
    else: response = onsexpenditure.predict(df).tolist()
    response = {'ons_expenditure': response}
    return jsonify(response)

@app.route('/creditworthiness/api/v1.0/scorecard', methods=['POST'])
@app.route('/creditworthiness/api/v1.0/scorecard/<option>', methods=['POST'])
@schema.validate(scorecard_schema)
def scorecard_predict_proba(option=''):
    if not request.json: abort(400)
    df = pd.DataFrame(request.get_json(), columns=scorecard._xcolumns)
    if option=='proba': response = scorecard.predict_proba(df).tolist()
    else: response = scorecard.predict(df).tolist()
    response = {'credit_risk': response}
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