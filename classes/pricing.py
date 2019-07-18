import logging
import pandas as pd
import numpy as np

from jsonschema import validate
from classes.scorecard import Scorecard
from classes.affordability import Affordability

# define the product range here
INTEREST = {'Interest rate' : [0.05, 0.07, 0.10, 0.15]}
DURATION = {'Duration' : [4, 8, 12, 24, 36, 72]}
CREDIT = {'Credit amount' : [250, 500, 1000, 2500, 5000, 10000, 20000]}

class Pricing():
    """Risk-based Pricing Calculation Class"""

    @staticmethod
    def cartesian_product(left, right): return (
        left.assign(key=1).merge(right.assign(key=1), on='key').drop('key', 1))
    
    @staticmethod
    def calculate_payments(row): return(
        (row['Interest rate'] / 12) / (1 - pow(1+(row['Interest rate']/12), -row['Duration'])) * row['Credit amount'])
    
    def __init__(self, request): 

        # log request
        logging.info('{"pricingInput": %s}', request)

        # define pricing matrix
        self._df = pd.DataFrame.from_records(request)
        
        # add range of potential interest rates
        self._df = self.cartesian_product(
            self._df, pd.DataFrame(INTEREST))
                
        # set properties from non-mandatory fields
        if 'Duration' not in self._df:
            self._df = self.cartesian_product(
                self._df, pd.DataFrame(DURATION))
        if 'Credit amount' not in self._df:
            self._df = self.cartesian_product(
                self._df, pd.DataFrame(CREDIT))
            
        # calculate monthly payments
        self._df['Monthly payment'] = self._df.apply(self.calculate_payments, axis=1)
    
    @staticmethod
    def calculate_profit(row): return(
        (row['Total cost'] - row['Credit amount']) * row['pGood'] - row['Credit amount'] * row['pBad'])
    
    def calculate_credit_risk(self, scorecard: Scorecard):
        
        # calculate pBad and pGood
        self._df = pd.merge(
            self._df, 
            pd.DataFrame(scorecard.predict(self._df, proba=True), columns=['pBad', 'pGood']),
            left_index=True, 
            right_index=True)
        
        # calculate profit
        self._df['Total cost'] = self._df['Monthly payment'] * self._df['Duration']
        self._df['Profit'] = self._df.apply(self.calculate_profit, axis=1)
        
    def calculate_affordability(self, affordability: Affordability):
        
        # calculate affordability
        self._df = pd.merge(
            self._df, 
            pd.DataFrame(affordability.calculate(self._df), columns=['expenditure', 'affordability']),
            left_index=True, 
            right_index=True)
    
    def get_suitable_products(self, minprofit: float):
            
        # filter on profit and affordability
        profitable = self._df['Profit'] >= minprofit
        affordable = self._df['Monthly payment'] <= self._df['affordability']
        df = self._df[profitable & affordable]
        
        # aggregate
        df = df.groupby(['Duration', 'Credit amount']).agg({'Interest rate' : np.min, 'Monthly payment': np.min})
        return(df)