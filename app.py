import logging
import json
import pandas as pd

from flask import Flask, jsonify, request
from flask_json_schema import JsonSchema, JsonValidationError

from classes.scorecard import Scorecard
from classes.onsexpenditure import ONSExpenditure
from classes.pricing import Pricing

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
    
    # ensure json and read to data frame
    if not request.json: abort(400)
    df = pd.DataFrame(request.get_json())
    
    # switch depending on url options
    if option=='full': response = onsexpenditure.predict(df, False).to_dict(orient='records')
    else: response = onsexpenditure.predict(df).tolist()
        
    # format response and return
    response = {'ons_expenditure': response}
    return jsonify(response)

@app.route('/creditworthiness/api/v1.0/scorecard', methods=['POST'])
@app.route('/creditworthiness/api/v1.0/scorecard/<option>', methods=['POST'])
@schema.validate(scorecard_schema)
def scorecard_predict(option=''):
    
    # ensure json and read to data frame
    if not request.json: abort(400)
    df = pd.DataFrame(request.get_json(), columns=scorecard._xcolumns)
    
    # switch depending on url options
    if option=='proba': response = scorecard.predict_proba(df).tolist()
    else: response = scorecard.predict(df).tolist()
        
    # format response and return
    response = {'credit_risk': response}
    return jsonify(response)

@app.route('/creditworthiness/api/v1.0/pricing', methods=['POST'])
@schema.validate(pricing_schema)
def pricing():
    
    # ensure json and read to data frame
    if not request.json: abort(400)
    df = pd.DataFrame(request.get_json())
    
    # segregate input to ensure scorecard variables are not counted as expenditure
    expenditure_columns = expenditure_schema['items']['properties']
    df_expenditure = df[df.columns[df.columns.isin(expenditure_columns)]]
    df['monthlyExpenditure'] = onsexpenditure.predict(df_expenditure).tolist()
    
    # enumerate pricing matrix
    pricing = Pricing()
    pricing.fit(df)
    df = pricing.get_product_matrix()
    
    # calculate risk/profit
    df['pGood'] = scorecard.predict_proba(df)[:, 1]
    df['profit'] = df.apply(pricing.calculate_profit, axis=1)

    # filter profitable and affordable
    df = df[df.profit > 0]
    df = df[df.disposableIncome > df.monthlyPayment]
    
    # ensure credit limit increases with term
    df.sort_values(['index', 'durationInMonths', 'creditAmount', 'totalCost'], 
                   ascending=[True, True, False, True], inplace=True)
    df = df.merge(df.groupby('index')['creditAmount'].cummax(), 
                  left_index=True, right_index=True, suffixes=['', 'Cummax'])
    df = df[df.creditAmount >= df.creditAmountCummax]
    
    # take cheapest option for each term
    df.drop_duplicates(['index', 'durationInMonths'], inplace=True)
    df = df[['index', 'durationInMonths', 'interestRate', 'creditAmount', 'disposableIncome', 
             'monthlyPayment', 'pGood', 'totalCost', 'profit']].round(2)
    response = df.groupby('index').apply(lambda x: x.to_dict(orient='records')).tolist()

    # return
    response = {'suggested_products': response}
    return jsonify(response)

# run the application
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True)