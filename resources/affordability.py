import logging
import json

from os import path

class Affordability():
    """Affordability Calculation Class."""

    def __init__(
        self, monthly_income=0, mortgage_or_rent=0, monthly_credit_commitments=0,
        employment_status='full_time', no_of_adults=1, no_of_dependants=0): 
        
        self.setMonthlyIncome(monthly_income)
        self.setMortgageOrRent(mortgage_or_rent)
        self.setMonthlyCreditCommitments(monthly_credit_commitments)
        self.setEmploymentStatus(employment_status)
        self.setNoOfDependants(no_of_dependants)
        self.setNoOfAdults(no_of_adults)
        self._disposable_income_mutliplier = 0.5

    def _ensureInteger(self, integer: int):
        """Convert to integer else 0."""

        if isinstance(integer, int): 
            return(integer)
        else:
            try:
                integer = int(integer)
                logging.info('converting value to integer')
                return(integer)
            except ValueError:
                logging.warning('"%s" could not be converted to an integer', integer)  
        return(0)
    
    def _isRetired(self):
        """Check if appplicant is retired"""
        
        return(self._employment_status in ('pension'))
        
    def setMonthlyIncome(self, monthly_income: int):
        
        self._monthly_income = self._ensureInteger(monthly_income)
        if self._monthly_income not in range(5000):
            self._monthly_income = 0
            logging.info('monthly_income out of range')
        
    def setMortgageOrRent(self, morgage_or_rent: int):
        
        self._morgage_or_rent = self._ensureInteger(morgage_or_rent)
        if self._morgage_or_rent not in range(5000):
            self._morgage_or_rent = 5000
            logging.info('morgage_or_rent out of range')
            
    def setMonthlyCreditCommitments(self, monthly_credit_commitments: int):
        
        self._monthly_credit_commitments = self._ensureInteger(monthly_credit_commitments)
        if self._monthly_credit_commitments < 0:
            self._monthly_credit_commitments = 0
            logging.info('monthly_credit_commitments out of range')
            
    def setEmploymentStatus(self, employment_status: str):
        
        if employment_status in (
            'full_time', 'part_time', 'self_employed', 'student', 
            'pension', 'temporary', 'benfits'):
            self._employment_status = employment_status
        
    def setNoOfDependants(self, no_of_dependants: int):
        
        self._no_of_dependants = self._ensureInteger(no_of_dependants)
        if self._no_of_dependants not in range(0, 9):
            self._no_of_dependants = 9
            logging.info('no_of_dependants out of range')
            
    def setNoOfAdults(self, no_of_adults: int):
        
        self._no_of_adults = self._ensureInteger(no_of_adults)
        if self._no_of_adults not in range(1, 9):
            self._no_of_adults = 1
            logging.info('no_of_adults out of range')

    def getONSExpenditure(self):
        
        # read ONS data file
        ons_json = path.join(path.dirname(__file__), 'a23final201718.json')
        with open(ons_json) as ONS_data:
            expenditure = json.load(ONS_data)
        ONS_data.close()
        
        # determine expediture
        if self._no_of_adults == 1: 
            ONS_expenditure = expenditure['non_retired']['one_adult']
            if self._isRetired(): self.ONS_expenditure = expenditure['retired']['other_retired']['one_adult']
            if self._no_of_dependants == 1: ONS_expenditure = expenditure['retired_and_non_retired']['one_adult']['one_child']
            if self._no_of_dependants >= 2: ONS_expenditure = expenditure['retired_and_non_retired']['one_adult']['two_or_more_children']
        if self._no_of_adults == 2:
            ONS_expenditure = expenditure['non_retired']['two_adults']
            if self._isRetired(): ONS_expenditure = expenditure['retired']['other_retired']['two_adults']
            if self._no_of_dependants == 1: ONS_expenditure = expenditure['retired_and_non_retired']['two_adults']['one_child']
            if self._no_of_dependants == 2: ONS_expenditure = expenditure['retired_and_non_retired']['two_adults']['two_children']
            if self._no_of_dependants >= 3: ONS_expenditure = expenditure['retired_and_non_retired']['two_adults']['three_or_more_children']
        if self._no_of_adults >= 3:
            ONS_expenditure = expenditure['retired_and_non_retired']['three_adults']['without_children']
            if self._no_of_dependants >= 1: ONS_expenditure = expenditure['retired_and_non_retired']['three_adults']['with_children']
                
        # scale up weekly to monthly
        ONS_expenditure = (ONS_expenditure / 7) * 30.25
        return(ONS_expenditure)
        
    def getNetDisposableIncome(self):

        net_disposable_income = self._monthly_income
        net_disposable_income = net_disposable_income - self._morgage_or_rent
        net_disposable_income = net_disposable_income - self._monthly_credit_commitments
        net_disposable_income = net_disposable_income - self.getONSExpenditure()
        return(net_disposable_income)
    
    def getAffordability(self):
        
        affordability = self.getNetDisposableIncome() * self._disposable_income_mutliplier
        return(affordability)