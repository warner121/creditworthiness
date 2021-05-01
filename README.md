# TODO

* fix bug where file and api input to scorecard provide different results (ordering problem?)
* ~~make pricing accept multiple input records and update schemas accordingly~~
* make output more readable
* automated code check
* add test coverage
* dockerise
* consider alternatives to passing credit and affordability evaluators to pricing
* ~~prevent duplicate columns on multiple calls to evaluators~~

# creditworthiness

3-in-1 credit risk, affordability risk and risk-based pricing service. Still very much work-in-progress but the output below should give you an idea where this is heading. 

## affordability

```shell
$ curl -i -H "Content-Type: application/json" -X POST -d '[{"monthly_income":5000,"mortgage_or_rent":200,"monthly_credit_commitments":0,"employment_status":"full_time","no_of_adults":1,"no_of_dependants":0}]' http://localhost:5000/creditworthiness/api/v1.0/affordability
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 74
Server: Werkzeug/0.14.1 Python/3.7.2
Date: Fri, 02 Aug 2019 15:15:30 GMT

{
  "affordability": [
    [
      1727.625, 
      1636.1875
    ]
  ]
}
```

## credit risk

```shell
$ curl --location --request POST 'http://127.0.0.1:5000/creditworthiness/api/v1.0/scorecard' \
--header 'Content-Type: application/json' \
--data-raw '[
    {
        "statusOfExistingCheckingAccount": -1,
        "durationInMonths": 60,
        "creditHistory": "existing credits paid back duly till now",
        "purpose": "business",
        "creditAmount": 7297,
        "savingsAccountOrBonds": 0,
        "presentEmploymentSince": 1.0,
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
  "prediction": {
    "class": [
      true
    ], 
    "probabilities": [
      [
        0.0761257257501865, 
        0.9238742742498135
      ]
    ]
  }
}
```

## risk-based pricing

```shell
$ curl -i -H "Content-Type: application/json" -X POST -d '[{"monthly_income":5000,"mortgage_or_rent":200,"monthly_credit_commitments":0,"employment_status":"full_time","no_of_adults":1,"no_of_dependants":0,"Age":67,"Sex":"male","Job":2,"Housing":"own","Saving accounts":null,"Checking account":"little","Purpose":"radio/TV","Risk":"good"}]' http://localhost:5000/creditworthiness/api/v1.0/pricing
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 735
Server: Werkzeug/0.14.1 Python/3.7.2
Date: Fri, 02 Aug 2019 15:17:55 GMT

[
  [
    {
      "Credit amount": 250, 
      "data": [
        {
          "Duration": 4, 
          "data": {
            "Interest rate": 0.1, 
            "Monthly payment": 63.80748609432485
          }
        }, 
        {
          "Duration": 8, 
          "data": {
            "Interest rate": 0.1, 
            "Monthly payment": 32.43322017304352
          }
        }, 
        {
          "Duration": 12, 
          "data": {
            "Interest rate": 0.1, 
            "Monthly payment": 21.978971807502468
          }
        }, 
        {
          "Duration": 24, 
          "data": {
            "Interest rate": 0.15, 
            "Monthly payment": 12.12166201173779
          }
        }
      ]
    }
  ]
]
```
