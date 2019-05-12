import logging
import json

from flask import Flask, jsonify, request
from flask_json_schema import JsonSchema, JsonValidationError

from classes.affordability import Affordability
from classes.scorecard import Scorecard

# instantiate the application and validation schema
app = Flask(__name__)
schema = JsonSchema(app)

# instantiate and train the scorecard
scorecard = Scorecard()
scorecard.train()

# load schemas
with open('schemas/affordability.json') as json_data:
    affordability_schema = json.load(json_data)
    json_data.close()
with open('schemas/scorecard.json') as json_data:
    scorecard_schema = json.load(json_data)
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
    a = Affordability(request.json)
    affordability = a.getAffordability()
    return jsonify({'affordability': affordability})

@app.route('/creditworthiness/api/v1.0/scorecard/predict', methods=['GET'])
def scorecard_predict():
    response = {'prediction': {
        'class': scorecard.predictFromFile('resources/scorecardtest.json', proba=False).tolist(),
        'probabilities': scorecard.predictFromFile('resources/scorecardtest.json', proba=True).tolist()}}
    return jsonify(response)

@app.route('/creditworthiness/api/v1.0/scorecard/predict', methods=['POST'])
@schema.validate(scorecard_schema)
def scorecard_predict_json():
    if not request.json:
        abort(400)
    json = request.get_json()
    response = {'prediction': {
        'class': scorecard.predictFromJson(json, proba=False).tolist(),
        'probabilities': scorecard.predictFromJson(json, proba=True).tolist()}}
    return jsonify(response)

# run the application
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True)