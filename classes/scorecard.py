import logging
import pandas as pd
import numpy as np
import pickle

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from os import path

SCORECARDFILE = path.join(path.dirname(__file__), '../resources/scorecard.pkl')

class Scorecard():
    
    def __init__(self):

        # train the model on instantiation
        self.train()
    
    def train(self):
        """Method for training the credit risk model."""
        
        # read data from static file
        data = pd.read_csv(path.join(path.dirname(__file__), '../resources/german_credit_data.csv'), index_col=0)
            
        # define integer features
        integer_features = ['Age', 'Job', 'Credit amount', 'Duration']
        integer_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())])

        # define categorical features
        categorical_features = ['Sex', 'Housing', 'Saving accounts', 'Checking account', 'Purpose']
        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
            ('onehot', OneHotEncoder(handle_unknown='ignore'))])
        
        # define the preprocessor
        preprocessor = ColumnTransformer(
            transformers=[
                ('int', integer_transformer, integer_features),
                ('cat', categorical_transformer, categorical_features)])

        # build sklearn pipeline
        self._pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                                         ('classifier', LogisticRegression(solver='lbfgs'))])
    
        # fit the model
        X = data.drop('Risk', axis=1)
        y = data['Risk']
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
    
        logging.info('{"scorecardPredictionInput": %s}', df.to_json(orient='records'))
        if proba: prediction = self._pipeline.predict_proba(df)
        else: prediction = self._pipeline.predict(df)
        return(prediction)
        
    def predict_from_file(self, filename: str, proba: bool):
        
        df = pd.read_json(filename)
        return(self.predict(df, proba))
    
    def predict_from_json(self, json: list, proba: bool):
    
        df = pd.DataFrame.from_records(json)
        return(self.predict(df, proba))