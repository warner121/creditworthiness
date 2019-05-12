import json

from os import path

class Affordability():
    """Affordability Calculation Class"""

    def __init__(self, request): 
        
        # set properties from mandatory fields
        self._monthly_income = request['monthly_income']
        self._mortgage_or_rent = request['mortgage_or_rent']
        self._monthly_credit_commitments = request['monthly_credit_commitments']
        self._employment_status = request['employment_status']
        self._no_of_dependants = request['no_of_dependants']
        self._no_of_adults = request['no_of_adults']
        
        # set non-mandatory fields
        try: self._disposable_income_mutliplier =request['disposable_income_mutliplier']
        except KeyError: self._disposable_income_mutliplier = 0.5

    def _isRetired(self):
        """Check if appplicant is retired"""
        
        return(self._employment_status in ('pension'))
        
    def getONSExpenditure(self):
        """Lookup indiscretionary spending based on household composition"""
        
        # read ONS data file
        ons_json = path.join(path.dirname(__file__), '../resources/a23final201718.json')
        with open(ons_json) as ONS_data:
            expenditure = json.load(ONS_data)
        ONS_data.close()
        
        # determine expediture
        if self._no_of_adults == 1: 
            ONS_expenditure = expenditure['non_retired']['one_adult']
            if self._isRetired(): self.ONS_expenditure = expenditure['retired']['other_retired']['one_adult']
            if self._no_of_dependants == 1: ONS_expenditure += expenditure['retired_and_non_retired']['one_adult']['one_child']
            if self._no_of_dependants >= 2: ONS_expenditure += expenditure['retired_and_non_retired']['one_adult']['two_or_more_children'] * self._no_of_dependants
        if self._no_of_adults == 2:
            ONS_expenditure = expenditure['non_retired']['two_adults']
            if self._isRetired(): ONS_expenditure = expenditure['retired']['other_retired']['two_adults']
            if self._no_of_dependants == 1: ONS_expenditure += expenditure['retired_and_non_retired']['two_adults']['one_child']
            if self._no_of_dependants == 2: ONS_expenditure += expenditure['retired_and_non_retired']['two_adults']['two_children'] * self._no_of_dependants
            if self._no_of_dependants >= 3: ONS_expenditure += expenditure['retired_and_non_retired']['two_adults']['three_or_more_children'] * self._no_of_dependants
        if self._no_of_adults >= 3:
            ONS_expenditure = expenditure['retired_and_non_retired']['three_adults']['without_children']
            if self._no_of_dependants >= 1: ONS_expenditure += expenditure['retired_and_non_retired']['three_adults']['with_children'] * self._no_of_dependants
                
        # scale up weekly to monthly
        ONS_expenditure = (ONS_expenditure / 7) * 30.25
        return(ONS_expenditure)
        
    def getAffordability(self):
        """Calculate affordability"""

        # deduct indiscretionary income
        affordability = self._monthly_income
        affordability = affordability - self._mortgage_or_rent
        affordability = affordability - self._monthly_credit_commitments
        affordability = affordability - self.getONSExpenditure()
        
        # apply disposable income multiplier
        affordability = affordability * self._disposable_income_mutliplier
        return(affordability)