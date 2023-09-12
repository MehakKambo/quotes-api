from flask import Flask
import os
import psycopg2
from dotenv import load_dotenv, find_dotenv
from markupsafe import escape

app = Flask(__name__)
load_dotenv(find_dotenv())
app.config['CONNECTION_STRING'] = os.environ.get('CONNECTION_STRING')


@app.route("/hi")
def hello():
    return "<p>Hello, World!</p>"