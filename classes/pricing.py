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

    def __init__(self):
        pass
    
    @staticmethod
    def _calculate_payments(x: pd.Series):
        return (x.interestRate / 12) / (1 - pow(1+(x.interestRate/12), -x.durationInMonths)) * x.creditAmount
    
    def fit(self, df: pd.DataFrame):
        
        # retain index
        df.reset_index(inplace=True)
        df['disposableIncome'] = df.monthlyIncomeAfterTax - df.monthlyExpenditure

        # enumerate application/product matrix
        df = df.merge(interestRate, how='cross')
        if 'durationInMonths' not in df: df = df.merge(durationInMonths, how='cross')
        if 'creditAmount' not in df: df = df.merge(creditAmount, how='cross')

        # calculate monthly payments
        df['monthlyPayment'] = df.apply(self._calculate_payments, axis=1)
        df['totalCost'] = df.monthlyPayment * df.durationInMonths
        
        # generate final mandatory field for scorecard (10X reduced from original)
        df['installmentRateInPercentageOfDisposableIncome'] = np.ceil(10 * df.monthlyPayment / df.disposableIncome)
        self._df = df
    
    def get_product_matrix(self):
        return self._df
    
    @staticmethod
    def calculate_profit(x: pd.Series): 
        return ((x.totalCost - x.creditAmount) * x.pGood) - (x.creditAmount * (1.0-x.pGood))
