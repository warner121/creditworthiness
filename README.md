# creditworthiness

3-in-1 credit risk, affordability risk and risk-based pricing service. Still very much work-in-progress but the output below should give you an idea where this is heading. 

## affordability

```shell
$ curl -i -H "Content-Type: application/json" -X POST -d '{"monthly_income":5000,"mortgage_or_rent":200,"monthly_credit_commitments":0,"employment_status":"full_time","no_of_adults":1,"no_of_dependants":0}' http://localhost:5000/creditworthiness/api/v1.0/affordability
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 74
Server: Werkzeug/0.14.1 Python/3.7.2
Date: Thu, 11 Jul 2019 20:15:23 GMT

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
$ curl -i -H "Content-Type: application/json" -X POST -d '{"Age":67,"Sex":"male","Job":2,"Housing":"own","Saving accounts":null,"Checking account":"little","Credit amount":1169,"Duration":6,"Purpose":"radio/TV","Risk":"good"}' http://localhost:5000/creditworthiness/api/v1.0/scorecard/predict
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 164
Server: Werkzeug/0.14.1 Python/3.7.2
Date: Thu, 11 Jul 2019 20:16:56 GMT

{
  "prediction": {
    "class": [
      "good"
    ], 
    "probabilities": [
      [
        0.12486210066697356, 
        0.8751378993330264
      ]
    ]
  }
}
```

## risk-based pricing

```shell
$ curl -i -H "Content-Type: application/json" -X POST -d '{"monthly_income":5000,"mortgage_or_rent":200,"monthly_credit_commitments":0,"employment_status":"full_time","no_of_adults":1,"no_of_dependants":0,"Age":67,"Sex":"male","Job":2,"Housing":"own","Saving accounts":null,"Checking account":"little","Purpose":"radio/TV","Risk":"good"}' http://localhost:5000/creditworthiness/api/v1.0/pricing
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 235
Server: Werkzeug/0.14.1 Python/3.7.2
Date: Thu, 11 Jul 2019 20:18:07 GMT

{
  "pricing": "{\"Interest rate\":{\"[4,250]\":0.1,\"[8,250]\":0.1,\"[12,250]\":0.1,\"[24,250]\":0.15},\"Monthly payment\":{\"[4,250]\":63.8074860943,\"[8,250]\":32.433220173,\"[12,250]\":21.9789718075,\"[24,250]\":12.1216620117}}"
}
```
