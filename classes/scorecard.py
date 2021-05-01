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

        # train the model on instantiation
        self.train()
    
    def train(self):
        """Method for training the credit risk model."""
        
        # read data from static file
        df = pd.read_csv(path.join(path.dirname(__file__), '../resources/german.data'), sep=' ', header=None,
                         names=['statusOfExistingCheckingAccount', 'durationInMonths', 'creditHistory', 'purpose', 'creditAmount',
                                 'savingsAccountOrBonds', 'presentEmploymentSince', 'installmentRateInPercentageOfDisposableIncome',
                                 'personalStatusAndSex', 'otherDebtorsOrGuarantors', 'presentResidenceSince', 'property', 'ageInYears',
                                 'otherInstallmentPlans', 'housing', 'numberOfExistingCreditsAtThisBank', 'job',
                                 'numberOfPeopleBeingLiableToProvideMaintenanceFor', 'telephone', 'foreignWorker', 'paid'])
        
        # set boolean for paid
        df.paid = df.paid==2
                         
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
        self._pipeline = make_pipeline(preprocessor, LogisticRegression(solver='lbfgs'))
    
        # fit the model
        X = df.drop('paid', axis=1)
        y = df['paid']
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
        
    def predict(self, df: pd.DataFrame, proba: bool):
        """Performs model predictions from the pre-defined pipeline"""
        
        # apply transformer to label input before applying model
        logging.info('{"scorecardPredictionRawInput": %s}', df.to_json(orient='records'))
        df.fillna(value=np.nan, inplace=True)
        df = pd.DataFrame(GermanCreditColumnTransformer.fit_transform(df), columns=self._xcolumns)
        
        # apply model and return class/probability as requested 
        logging.info('{"scorecardPredictionTransformedInput": %s}', df.to_json(orient='records'))
        if proba: prediction = self._pipeline.predict_proba(df)
        else: prediction = self._pipeline.predict(df)
        return(prediction)
        
    def predict_from_file(self, filename: str, proba: bool):
        
        # read request from file and pad out missing columns if required
        df = pd.read_json(filename).to_dict(orient='records')
        df = pd.DataFrame(df, columns=self._xcolumns)
        return(self.predict(df, proba))
    
    def predict_from_json(self, json: list, proba: bool):
    
        # read request from arg and pad out missing columns if required
        df = pd.DataFrame(json, columns=self._xcolumns)
        return(self.predict(df, proba))
