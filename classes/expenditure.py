import logging
import pandas as pd
import numpy as np

from os import path
from classes.pipelines import ONSExpenditureTransformer

ONSDATAFILE = path.join(path.dirname(__file__), '../resources/a23final201718.csv')
INDEXCOLUMNS = ['retirementStatus', 'numberOfAdults', 'numberOfChildren']

class ONSExpenditure():
    """Expenditure Determination Class"""

    def __init__(self): 
        
        # load ONS data file and transpose
        df = pd.read_csv(ONSDATAFILE, header=None, index_col=0)
        self._df = df
        
    def fit(self):
        """Define lookup for indiscretionary spending based on household composition"""
                
        df = self._df
        
        # transpose, index and cast floats
        df = df.transpose()
        df.set_index(INDEXCOLUMNS, inplace=True)
        df = df.astype(float)
        logging.info('{"onsData": %s}', df.to_json(orient='records'))
        
        # scale per household member
        persons_per_household = df.weightedAverageNumberOfPersonsPerHousehold
        df.drop('weightedAverageNumberOfPersonsPerHousehold', inplace=True, axis=1)
        df = df.apply(lambda x: x / persons_per_household)
        
        # scale weekly to monthly
        df = (df / 7) * 30.25
        df.reset_index(inplace=True)
        
        # reset self._df
        self._df = df
        
    def transform(self, df: pd.DataFrame):
        """Labels the input from the request suitable for scorecard prediction"""
        
        # apply override retirement status where not required by ons
        df.loc[(df.numberOfAdults > 2) | (df.numberOfChildren > 0), 'retirementStatus'] = 'retired_and_non_retired'
        
        # apply transformer to label input before applying model
        logging.info('{"expenditureTansformerInput', df.to_json(orient='records'))
        df.fillna(value=np.nan, inplace=True)
        df = pd.DataFrame(
            ONSExpenditureTransformer.fit_transform(df), 
            columns=df.columns)
        return df

    def predict(self, df: pd.DataFrame):
        """Performs ons lookup of expenditure"""
        
        # determine total number of residents for ons extrapolation
        persons_per_household = df.numberOfAdults + df.numberOfChildren
        
        # apply transformer
        df = self.transform(df)
        
        # apply lookup to estimate expenditure
        logging.info('{"expenditurePredictionInput": %s}', df.to_json(orient='records'))
        df = df.merge(self._df, how='left', sort=False, on=INDEXCOLUMNS)
        
        # scale to number of residents
        df = df.apply(lambda x: x * persons_per_household if x.name not in INDEXCOLUMNS else x)
        prediction = df.drop(INDEXCOLUMNS, axis=1).round(2)
        
        # return esimated expenditure
        return prediction
        