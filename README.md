# creditworthiness
Application for the assessment of creditworthiness

curl -i -H "Content-Type: application/json" -X POST -d '{"monthly_income":2000, "mortgage_or_rent":200, "monthly_credit_commitments":0, "employment_status":"full_time", "no_of_adults":1, "no_of_dependants":0}' http://localhost:5000/creditworthiness/api/v1.0/affordability
HTTP/1.0 201 CREATED
Content-Type: application/json
Content-Length: 32
Server: Werkzeug/0.14.1 Python/3.7.2
Date: Wed, 24 Apr 2019 20:12:12 GMT

{
  "affordability": 136.1875
}