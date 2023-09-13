from flask import Flask, Response
import os
import psycopg2
import json

app = Flask(__name__)
app.config['CONNECTION_STRING'] = os.environ.get('CONNECTION_STRING')

# The default route returns a random quote
@app.route("/", methods=['GET'])
def get_random_quote():
    conn = psycopg2.connect(app.config['CONNECTION_STRING'])
    query = """
    SELECT Quotes.text, Authors.name, Categories.name
    FROM Quotes
    JOIN Authors ON Quotes.authorID = Authors.ID
    JOIN Categories ON Quotes.categoryID = Categories.ID
    ORDER BY random()
    LIMIT 1;
    """
    cursor = conn.cursor()
    cursor.execute(query)
    quote, author_name, category = cursor.fetchone()
    cursor.close()
    conn.close()
    
    response_data = {'quote': quote, 'author': author_name, 'category': category}
    json_response = json.dumps(response_data)
    
    return Response(json_response, content_type='application/json')

# Returns a list of Authors
@app.route('/authors', methods=['GET'])
def get_all_authors():
    conn = psycopg2.connect(app.config['CONNECTION_STRING'])
    query = "SELECT name FROM Authors ORDER BY name;"
    cursor = conn.cursor()
    cursor.execute(query)
    
    authors = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    response_data =  {"authors": authors}
    
    json_response = json.dumps(response_data)
    return Response(json_response, content_type='application/json')
