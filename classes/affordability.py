import json
import logging
import pandas as pd
import numpy as np

from os import path

ONSDATAFILE = path.join(path.dirname(__file__), '../resources/a23final201718.json')

class Affordability():
    """Affordability Calculation Class"""

    def __init__(self): 
        
        # load ONS data file
        with open(ONSDATAFILE) as ons_json:
            self._expenditure = json.load(ons_json)
        ons_json.close()

    @staticmethod
    def is_retired(employment_status):
        """Check if appplicant is retired"""
        
        return(employment_status in ('pension', 'retired'))
        
    def get_expenditure(self, household: dict):
        """Lookup indiscretionary spending based on household composition"""
        
        no_of_adults = household['no_of_adults']
        employment_status = household['employment_status']
        no_of_dependants = household['no_of_dependants']

        # determine expediture
        if no_of_adults == 1: 
            expenditure = self._expenditure['non_retired']['one_adult']
            if self.is_retired(employment_status): expenditure = self._expenditure['retired']['other_retired']['one_adult']
            if no_of_dependants == 1: expenditure += self._expenditure['retired_and_non_retired']['one_adult']['one_child']
            if no_of_dependants >= 2: expenditure += self._expenditure['retired_and_non_retired']['one_adult']['two_or_more_children'] * no_of_dependants
        if no_of_adults == 2:
            expenditure = self._expenditure['non_retired']['two_adults']
            if self.is_retired(employment_status): expenditure = self._expenditure['retired']['other_retired']['two_adults']
            if no_of_dependants == 1: expenditure += self._expenditure['retired_and_non_retired']['two_adults']['one_child']
            if no_of_dependants == 2: expenditure += self._expenditure['retired_and_non_retired']['two_adults']['two_children'] * no_of_dependants
            if no_of_dependants >= 3: expenditure += self._expenditure['retired_and_non_retired']['two_adults']['three_or_more_children'] * no_of_dependants
        if no_of_adults >= 3:
            expenditure = self._expenditure['retired_and_non_retired']['three_adults']['without_children']
            if no_of_dependants >= 1: expenditure += self._expenditure['retired_and_non_retired']['three_adults']['with_children'] * no_of_dependants
                
        # scale up weekly to monthly
        expenditure = (expenditure / 7) * 30.25
        return(expenditure)
    
    def calculate(self, df: pd.DataFrame):
        """Calculate the monthly affordability.
        
        Returns: 
        
        2-d numpy array with total expenditure and monthly affordability
        analagous to sklearn predict_proba function.
        """
    
        # log the request
        logging.info('{"affordabilityCalculationInput": %s}', df.to_json(orient='records'))
        
        # associate indiscretionary expenditure and deduct from income
        expenditure = df.apply(self.get_expenditure, axis=1)
        expenditure = expenditure + df['mortgage_or_rent'] + df['monthly_credit_commitments']
        affordability = df['monthly_income'] - expenditure
        
        # set properties from non-mandatory fields
        if 'disposable_income_mutliplier' not in df:
            disposable_income_mutliplier = 0.5
        
        # apply disposable income multiplier
        affordability = affordability * disposable_income_mutliplier
        return(np.stack([expenditure.values, affordability.values], axis=1))
    
    def calculate_from_file(self, filename: str):
        
        df = pd.read_json(filename)
        return(self.calculate(df))
    
    def calculate_from_json(self, json: list):
    
        df = pd.DataFrame.from_records(json)
        return(self.calculate(df))