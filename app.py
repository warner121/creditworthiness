import logging
import json

from flask import Flask, jsonify, request
from flask_json_schema import JsonSchema, JsonValidationError

from classes.scorecard import Scorecard
from classes.affordability import Affordability
from classes.pricing import Pricing

# instantiate the application and validation schema
app = Flask(__name__)
schema = JsonSchema(app)

# instantiate the scorecard and affordability calculator
scorecard = Scorecard()

# load schemas
with open('schemas/affordability.json') as json_data:
    affordability_schema = json.load(json_data)
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
@app.route('/creditworthiness/api/v1.0/affordability', methods=['POST'])
@schema.validate(affordability_schema)
def affordability():
    if not request.json:
        abort(400)
    json = request.get_json()
    affordability = Affordability()
    response = {'affordability': affordability.calculate_from_json([json]).tolist()}
    return jsonify(response)

@app.route('/creditworthiness/api/v1.0/scorecard', methods=['GET'])
def scorecard_predict():
    response = {'prediction': {
        'class': scorecard.predict_from_file('resources/scorecardtest.json', proba=False).tolist(),
        'probabilities': scorecard.predict_from_file('resources/scorecardtest.json', proba=True).tolist()}}
    return jsonify(response)

@app.route('/creditworthiness/api/v1.0/scorecard', methods=['POST'])
@schema.validate(scorecard_schema)
def scorecard_predict_json():
    if not request.json:
        abort(400)
    json = request.get_json()
    response = {'prediction': {
        'class': scorecard.predict_from_json([json], proba=False).tolist(),
        'probabilities': scorecard.predict_from_json([json], proba=True).tolist()}}
    return jsonify(response)

@app.route('/creditworthiness/api/v1.0/pricing', methods=['POST'])
@schema.validate(pricing_schema)
def pricing():
    if not request.json:
        abort(400)
    json = request.get_json()
    affordability = Affordability()
    pricing = Pricing([json])
    pricing.calculate_credit_risk(scorecard)
    pricing.calculate_affordability(affordability)
    response = {'pricing': pricing.get_suitable_products(-25).to_json()}
    return jsonify(response)

# run the application
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True)