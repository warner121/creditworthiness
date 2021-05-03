import logging
import pandas as pd
import numpy as np

from jsonschema import validate

# define the product range here
durationInMonths = pd.Series([4, 8, 12, 24, 36, 72], name='durationInMonths')
interestRate = pd.Series([0.05, 0.07, 0.10, 0.15], name='interestRate')
creditAmount = pd.Series([250, 500, 1000, 2500, 5000, 10000, 20000], name='creditAmount')

class Pricing():
    """Risk-based Pricing Calculation Class"""

    @staticmethod
    def _calculate_payments(row):
        return (row.interestRate / 12) / (1 - pow(1+(row.interestRate/12), -row.durationInMonths)) * row.creditAmount

    def __init__(self, df): 
        
        # retain index
        df.reset_index(inplace=True)

        # enumerate application/product matrix
        df = df.merge(durationInMonths, how='cross', suffixes=['_supplied', ''])
        df = df.merge(interestRate, how='cross', suffixes=['_supplied', ''])
        df = df.merge(creditAmount, how='cross', suffixes=['_supplied', ''])

        # calculate monthly payments
        df['monthlyPayment'] = df.apply(self._calculate_payments, axis=1)
        df['totalCost'] = df.monthlyPayment * df.durationInMonths
        self._df = df
    
    @staticmethod
    def _calculate_profit(row): 
        return ((row.totalCost - row.creditAmount) * row.pGood) - (row.creditAmount * (1.0-row.pGood))

    def calculate_credit_risk(self, scorecard):
        
        df = self._df
        df['pGood'] = scorecard.predict_proba(df)[:, 1]
        df['profit'] = df.apply(self._calculate_profit, axis=1)
        return df
