import logging
import pandas as pd
import numpy as np
import pickle

from sklearn.pipeline import make_pipeline
from sklearn.compose import make_column_transformer

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression

from os import path
from classes.pipelines import GermanCreditColumnTransformer

SCORECARDFILE = path.join(path.dirname(__file__), '../resources/scorecard.pkl')

class Scorecard():
    
    def __init__(self):

        # read data from static file
        df = pd.read_csv(path.join(path.dirname(__file__), '../resources/german.data'), sep=' ', header=None,
                         names=['statusOfExistingCheckingAccount', 'durationInMonths', 'creditHistory', 'purpose', 'creditAmount',
                                 'savingsAccountOrBonds', 'presentEmploymentSince', 'installmentRateInPercentageOfDisposableIncome',
                                 'personalStatusAndSex', 'otherDebtorsOrGuarantors', 'presentResidenceSince', 'property', 'ageInYears',
                                 'otherInstallmentPlans', 'housing', 'numberOfExistingCreditsAtThisBank', 'job',
                                 'numberOfPeopleBeingLiableToProvideMaintenanceFor', 'telephone', 'foreignWorker', 'good'])
        
        # set boolean for good
        df.good = df.good==1
        self._df = df
               
    def fit(self):
        """Method for training the credit risk model."""
        
        df = self._df
            
        # list features by type
        categorical_feature_mask = df.dtypes==object
        categorical_features = df.columns[categorical_feature_mask].tolist()
        integer_feature_mask = df.dtypes==int
        integer_features = df.columns[integer_feature_mask].tolist()
        
        # define column transformers by type
        preprocessor = make_column_transformer(
            (StandardScaler(), integer_features), 
            (OneHotEncoder(), categorical_features))

        # build sklearn pipeline
        self._pipeline = make_pipeline(
            preprocessor, 
            LogisticRegression(solver='lbfgs'))
    
        # isolate X and y
        X = df.drop('good', axis=1)
        y = df['good']
        
        # fir the model
        self._xcolumns = X.columns
        self._pipeline.fit(X, y)
        
    def save(self):
        """Saves the model to a file."""
        
        picklefile = open(SCORECARDFILE, 'wb')
        pickle.dump(self._pipeline, picklefile)
        picklefile.close()
        
    def load(self):
        """Loads the model from a file."""
        
        picklefile = open(SCORECARDFILE, 'rb')
        self._pipeline = pickle.load(picklefile)
        picklefile.close()
        
    def transform(self, df: pd.DataFrame):
        """Labels the input from the request suitable for scorecard prediction"""
        
        # apply transformer to label input before applying model
        logging.info('{"scorecardTansformerInput', df.to_json(orient='records'))
        df.fillna(value=np.nan, inplace=True)
        df = pd.DataFrame(
            GermanCreditColumnTransformer.fit_transform(df), 
            columns=self._xcolumns)
        return df
        
    def predict(self, df: pd.DataFrame):
        """Performs model predictions from the pre-defined pipeline"""
        
        # apply transformer
        df = self.transform(df)

        # apply model and return class/probability as requested 
        logging.info('{"scorecardPredictionInput": %s}', df.to_json(orient='records'))
        prediction = self._pipeline.predict(df)
        return prediction
        
    def predict_proba(self, df: pd.DataFrame):
        """Performs model predictions from the pre-defined pipeline"""
        
        # apply transformer
        df = self.transform(df)

        # apply model and return class/probability as requested 
        logging.info('{"scorecardPredictionInput": %s}', df.to_json(orient='records'))
        prediction = self._pipeline.predict_proba(df)
        return prediction
        
