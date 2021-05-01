import pandas as pd
import numpy as np
import re

from sklearn.preprocessing import FunctionTransformer
from sklearn.compose import make_column_transformer

def labelStatusOfExistingCheckingAccount(x: np.array):
    x = pd.cut(x, bins=[-np.inf, 0, 200, np.inf], labels=['A11', 'A12', 'A13'], right=False)
    x = x.astype(object).fillna('A14')
    return pd.DataFrame(x)

def labelCreditHistory(x: np.array):
    x = x.apply(lambda x: re.sub('[^a-zA-Z]', '', x).lower())
    y = pd.Series({'nocreditstaken': 'A30',
                   'allcreditspaidbackduly': 'A30',
                   'allcreditsatthisbankpaidbackduly': 'A31',
                   'existingcreditspaidbackdulytillnow': 'A32',
                   'delayinpayingoffinthepast': 'A33',
                   'criticalaccount': 'A34',
                   'othercreditsexistingnotatthisbank': 'A34'})
    x = x.replace(y)
    return pd.DataFrame(x)

def labelPurpose(x: np.array):
    x = x.apply(lambda x: re.sub('[^a-zA-Z]', '', x).lower())
    y = pd.Series({'carnew': 'A40',
                   'carused': 'A41',
                   'furnitureequipment': 'A42',
                   'radiotelevision': 'A43',
                   'domesticappliances': 'A44',
                   'repairs': 'A45',
                   'education': 'A46',
                   'vacation': 'A47',
                   'retraining': 'A48',
                   'business': 'A49',
                   'others': 'A410'})
    x = x.replace(y)
    return pd.DataFrame(x)

def labelSavingsAccountOrBonds(x: np.array):
    x = pd.cut(x, bins=[-np.inf, 100, 500, 1000, np.inf], labels=['A61', 'A62', 'A63', 'A64'], right=False)
    x = x.astype(object).fillna('A65')
    return pd.DataFrame(x)

def labelPresentEmploymentSince(x: np.array):
    x = pd.cut(x, bins=[-np.inf, 1, 4, 7, np.inf], labels=['A72', 'A73', 'A74', 'A75'], right=False)
    x = x.astype(object).fillna('A71')
    return pd.DataFrame(x)

def labelPersonalStatusAndSex(x: np.array):
    x = x.apply(lambda x: re.sub('[^a-zA-Z]', '', x).lower())
    y = pd.Series({'maledivorced': 'A91',
                   'maleseparated': 'A91',
                   'femaledivorced': 'A92',
                   'femaleseparated': 'A92',
                   'femalemarried': 'A92',
                   'malesingle': 'A93',
                   'malemarried': 'A94',
                   'malewidowed': 'A94',
                   'femalesingle': 'A95'})
    x = x.replace(y)
    return pd.DataFrame(x)

def labelOtherDebtorsOrGuarantors(x: np.array):
    x = x.apply(lambda x: re.sub('[^a-zA-Z]', '', x).lower())
    y = pd.Series({'none': 'A101',
                   'coapplicant': 'A102',
                   'guarantor': 'A103'})
    x = x.replace(y)
    return pd.DataFrame(x)

def labelProperty(x: np.array):
    x = x.apply(lambda x: re.sub('[^a-zA-Z]', '', x).lower())
    y = pd.Series({'realestate': 'A121',
                   'buildingsocietysavingsagreement': 'A122',
                   'lifeinsurance': 'A122',
                   'car': 'A123',
                   'other': 'A123',
                   'unknown': 'A124',
                   'noproperty': 'A124'})
    x = x.replace(y)
    return pd.DataFrame(x)

def labelOtherInstallmentPlans(x: np.array):
    x = x.apply(lambda x: re.sub('[^a-zA-Z]', '', x).lower())
    y = pd.Series({'bank': 'A141',
                   'stores': 'A142',
                   'none': 'A143'})
    x = x.replace(y)
    return pd.DataFrame(x)

def labelHousing(x: np.array):
    x = x.apply(lambda x: re.sub('[^a-zA-Z]', '', x).lower())
    y = pd.Series({'rent': 'A151',
                   'own': 'A152',
                   'forfree': 'A153'})
    x = x.replace(y)
    return pd.DataFrame(x)

def labelJob(x: np.array):
    x = x.apply(lambda x: re.sub('[^a-zA-Z]', '', x).lower())
    y = pd.Series({'unemployed': 'A171',
                   'unskillednonresident': 'A171',
                   'unskilledresident': 'A172',
                   'skilledemployee': 'A173',
                   'official': 'A173',
                   'management': 'A174',
                   'selfemployed': 'A174',
                   'highlyqualifiedemployee': 'A174',
                   'officer': 'A174'})
    x = x.replace(y)
    return pd.DataFrame(x)

def labelTelephone(x: np.array):
    x = x.apply(lambda x: re.sub('[^a-zA-Z]', '', x).lower())
    y = pd.Series({'none': 'A191',
                   'yesregisteredunderthecustomersname': 'A192'})
    x = x.replace(y)
    return pd.DataFrame(x)

def labelForeignWorker(x: np.array):
    x = x.apply(lambda x: re.sub('[^a-zA-Z]', '', x).lower())
    y = pd.Series({'yes': 'A201',
                   'no': 'A202'})
    x = x.replace(y)
    return pd.DataFrame(x)

def labelDummy(x: np.array):
    return pd.DataFrame(x)

GermanCreditColumnTransformer = make_column_transformer(
    (FunctionTransformer(labelStatusOfExistingCheckingAccount), 'statusOfExistingCheckingAccount'), 
    (FunctionTransformer(labelDummy), 'durationInMonths'), 
    (FunctionTransformer(labelCreditHistory), 'creditHistory'),
    (FunctionTransformer(labelPurpose), 'purpose'), 
    (FunctionTransformer(labelDummy), 'creditAmount'), 
    (FunctionTransformer(labelSavingsAccountOrBonds), 'savingsAccountOrBonds'),
    (FunctionTransformer(labelPresentEmploymentSince), 'presentEmploymentSince'),
    (FunctionTransformer(labelDummy), 'installmentRateInPercentageOfDisposableIncome'), 
    (FunctionTransformer(labelPersonalStatusAndSex), 'personalStatusAndSex'),
    (FunctionTransformer(labelOtherDebtorsOrGuarantors), 'otherDebtorsOrGuarantors'), 
    (FunctionTransformer(labelDummy), 'presentResidenceSince'),
    (FunctionTransformer(labelProperty), 'property'),
    (FunctionTransformer(labelDummy), 'ageInYears'), 
    (FunctionTransformer(labelOtherInstallmentPlans), 'otherInstallmentPlans'), 
    (FunctionTransformer(labelHousing), 'housing'),
    (FunctionTransformer(labelDummy), 'numberOfExistingCreditsAtThisBank'), 
    (FunctionTransformer(labelJob), 'job'), 
    (FunctionTransformer(labelDummy), 'numberOfPeopleBeingLiableToProvideMaintenanceFor'), 
    (FunctionTransformer(labelTelephone), 'telephone'),
    (FunctionTransformer(labelForeignWorker), 'foreignWorker'))
