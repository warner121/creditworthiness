from flask import Flask
from flask_json_schema import JsonSchema

app = Flask(__name__)
schema = JsonSchema(app)

from app import views
