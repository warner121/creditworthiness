# TODO

* ~~fix bug where file and api input to scorecard provide different results (ordering problem?)~~
* ~~make pricing accept multiple input records and update schemas accordingly~~
* make output more readable
* automated code check
* add test coverage
* ~~dockerise~~
* ~~consider alternatives to passing credit and affordability evaluators to pricing~~
* ~~prevent duplicate columns on multiple calls to evaluators~~

# creditworthiness

Integrated 3-in-1 web service / recommender system offering credit risk, affordability risk and risk-based pricing. Utilises the classic 'German Credit Risk' dataset from Universität Hamburg for the credit risk model (scorecard) and UK Office of National Statistics for the affordability model (expenditure). Finally both models are combined to recommend a selection of personal loan products that would be considered suitable according to both criteria.

## affordability

The ons_expenditure endpoint provides a lookup against the ONS summary statistics referenced in resources/a23final201718.xls. The data was originally sourced from https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/expenditure/datasets/expenditurebyhouseholdcompositionuktablea23.

Total montly expenditure for 2 adults and 2 children according to ONS is £783.10 (weekly) / 7 * 30.25 = £3,384 (monthly).

```shell
$ curl --location --request POST 'http://127.0.0.1:5000/creditworthiness/api/v1.0/ons_expenditure' \
--header 'Content-Type: application/json' \
--data-raw '[
    {
        "retirementStatus": "non_retired",
        "numberOfAdults": 2,
        "numberOfChildren": 2
    }
]'
{
  "ons_expenditure": [
    3383.68
  ]
}
```

The web service implements graduated scaling beyond the categories explicitly defined by ONS. Thus, by increasing the number of children to 4.

```shell
$ curl --location --request POST 'http://127.0.0.1:5000/creditworthiness/api/v1.0/ons_expenditure' \
--header 'Content-Type: application/json' \
--data-raw '[
    {
        "retirementStatus": "non_retired",
        "numberOfAdults": 2,
        "numberOfChildren": 4
    }
]'
{
  "ons_expenditure": [
    3629.02
  ]
}
```

By using the /ons_expenditure/full extension we can obtain a breakdown of this expenditure.

```shell
$ curl --location --request POST 'http://127.0.0.1:5000/creditworthiness/api/v1.0/ons_expenditure/full' \
--header 'Content-Type: application/json' \
--data-raw '[
    {
        "retirementStatus": "non_retired",
        "numberOfAdults": 2,
        "numberOfChildren": 4
    }
]'
{
  "ons_expenditure": [
    {
      "alcoholicDrinksTobaccoAndNarcotics": 65.07, 
      "clothingAndFootwear": 168.29, 
      "communication": 116.43, 
      "education": 115.46, 
      "foodAndNonAlcoholicDrinks": 433.45, 
      "health": 32.29, 
      "householdGoodsAndServices": 250.48, 
      "miscellaneousGoodsAndServices": 237.27, 
      "netHousingFuelAndPower": 492.15, 
      "otherExpenditureItems": 505.36, 
      "recreationAndCulture": 448.12, 
      "restaurantsAndHotels": 306.74, 
      "transport": 457.91
    }
  ]
}
```

Finally it is also possible to override the national averages by passing the specific expenditure categories as input. Cutting out the alcohol, tobacco and narcotics reduces the total monthly expenditure by £65.07

```shell
$ curl --location --request POST 'http://127.0.0.1:5000/creditworthiness/api/v1.0/ons_expenditure' \
--header 'Content-Type: application/json' \
--data-raw '[
    {
        "retirementStatus": "non_retired",
        "numberOfAdults": 2,
        "numberOfChildren": 4,
        "alcoholicDrinksTobaccoAndNarcotics": 0
    }
]'
{
  "ons_expenditure": [
    3563.95
  ]
}
```

## credit risk

The /scorecard endoints implement a simple category-based logistic regression model (dubbed 'scorecard' in consumer credit) using the 'German Credit Risk' dataset from Universität Hamburg.

The first example evaluates an application returns a boolean signifing if the loan is more likely to be repaid (true) or default (false).

```shell
$ curl --location --request POST 'http://127.0.0.1:5000/creditworthiness/api/v1.0/scorecard' \
--header 'Content-Type: application/json' \
--data-raw '[
    {
        "statusOfExistingCheckingAccount": 1000,
        "durationInMonths": 12,
        "creditHistory": "existing credits paid back duly till now",
        "purpose": "business",
        "creditAmount": 250,
        "savingsAccountOrBonds": 10000,
        "presentEmploymentSince": 5,
        "installmentRateInPercentageOfDisposableIncome": 1,
        "personalStatusAndSex": "male: divorced",
        "otherDebtorsOrGuarantors": "none",
        "presentResidenceSince": 1,
        "property": "real estate",
        "ageInYears": 19,
        "otherInstallmentPlans": "bank",
        "housing": "rent",
        "numberOfExistingCreditsAtThisBank": 1,
        "job": "unskilled - resident",
        "numberOfPeopleBeingLiableToProvideMaintenanceFor": 1,
        "telephone": "none",
        "foreignWorker": "yes"
    }
]'
{
    "credit_risk": [
        true
    ]
}
```

Extending to the /scorecard/proba endpoint returns the probabilities for the same application as a list in the format [p(good), p(bad)].

```shell
$ curl --location --request POST 'http://127.0.0.1:5000/creditworthiness/api/v1.0/scorecard/proba' \
--header 'Content-Type: application/json' \
--data-raw '[
    {
        "statusOfExistingCheckingAccount": 1000,
        "durationInMonths": 12,
        "creditHistory": "existing credits paid back duly till now",
        "purpose": "business",
        "creditAmount": 250,
        "savingsAccountOrBonds": 10000,
        "presentEmploymentSince": 5,
        "installmentRateInPercentageOfDisposableIncome": 1,
        "personalStatusAndSex": "male: divorced",
        "otherDebtorsOrGuarantors": "none",
        "presentResidenceSince": 1,
        "property": "real estate",
        "ageInYears": 19,
        "otherInstallmentPlans": "bank",
        "housing": "rent",
        "numberOfExistingCreditsAtThisBank": 1,
        "job": "unskilled - resident",
        "numberOfPeopleBeingLiableToProvideMaintenanceFor": 1,
        "telephone": "none",
        "foreignWorker": "yes"
    }
]'
{
    "credit_risk": [
        [
            0.08568171940360014,
            0.9143182805963999
        ]
    ]
}
```

## risk-based pricing

The pricing service brings it all together, illustrating a series of up to 6 credit limits / products complete with montly payments, and expected profit on the loan. Note some features of the original scorecard model are not required as they are derived from the affordability parameters internally.

```shell
$ curl --location --request POST 'http://127.0.0.1:5000/creditworthiness/api/v1.0/pricing' \
--header 'Content-Type: application/json' \
--data-raw '[
    {
        "monthlyIncomeAfterTax": 5000,
        "retirementStatus": "non_retired",
        "numberOfAdults": 2,
        "numberOfChildren": 0,
        "statusOfExistingCheckingAccount": 1000,
        "creditHistory": "existing credits paid back duly till now",
        "purpose": "business",
        "savingsAccountOrBonds": 10000,
        "presentEmploymentSince": 5,
        "personalStatusAndSex": "male: divorced",
        "otherDebtorsOrGuarantors": "none",
        "presentResidenceSince": 1,
        "property": "real estate",
        "ageInYears": 49,
        "otherInstallmentPlans": "bank",
        "housing": "rent",
        "numberOfExistingCreditsAtThisBank": 1,
        "job": "unskilled - resident",
        "telephone": "yes, registered under the customers name",
        "foreignWorker": "yes"
    }
]'
{
    "suggested_products": [
        [
            {
                "creditAmount": 500,
                "disposableIncome": 2142.68,
                "durationInMonths": 4,
                "index": 0,
                "interestRate": 0.15,
                "monthlyPayment": 128.93,
                "pGood": 0.97,
                "profit": 0.88,
                "totalCost": 515.72
            },
            {
                "creditAmount": 1000,
                "disposableIncome": 2142.68,
                "durationInMonths": 8,
                "index": 0,
                "interestRate": 0.1,
                "monthlyPayment": 129.73,
                "pGood": 0.97,
                "profit": 2.6,
                "totalCost": 1037.86
            },
            {
                "creditAmount": 2500,
                "disposableIncome": 2142.68,
                "durationInMonths": 12,
                "index": 0,
                "interestRate": 0.15,
                "monthlyPayment": 225.65,
                "pGood": 0.94,
                "profit": 43.14,
                "totalCost": 2707.75
            },
            {
                "creditAmount": 5000,
                "disposableIncome": 2142.68,
                "durationInMonths": 24,
                "index": 0,
                "interestRate": 0.15,
                "monthlyPayment": 242.43,
                "pGood": 0.89,
                "profit": 185.84,
                "totalCost": 5818.4
            },
            {
                "creditAmount": 5000,
                "disposableIncome": 2142.68,
                "durationInMonths": 36,
                "index": 0,
                "interestRate": 0.1,
                "monthlyPayment": 161.34,
                "pGood": 0.89,
                "profit": 168.92,
                "totalCost": 5808.09
            },
            {
                "creditAmount": 5000,
                "disposableIncome": 2142.68,
                "durationInMonths": 72,
                "index": 0,
                "interestRate": 0.15,
                "monthlyPayment": 105.73,
                "pGood": 0.75,
                "profit": 702.56,
                "totalCost": 7612.2
            }
        ]
    ]
}
```
