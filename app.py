from flask import Flask, Response, request
import os
import psycopg2
from markupsafe import escape
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
    
    return Response(json_response, content_type='application/json'), 200

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
    return Response(json_response, content_type='application/json'), 200

# Returns the quote data provided the ID of that quote
@app.route('/quotes/<int:quote_id_raw>', methods=['GET'])
def get_quote_by_id(quote_id_raw: int):
    conn = psycopg2.connect(app.config['CONNECTION_STRING'])
    quote_id = escape(quote_id_raw)
    query = """
    SELECT Quotes.text, Authors.name, Categories.name
    FROM Quotes
    JOIN Authors ON Quotes.authorID = Authors.ID
    JOIN Categories ON Quotes.categoryID = Categories.ID
    WHERE Quotes.ID = %s;
    """
    cursor = conn.cursor()
    cursor.execute(query, (quote_id,))
    
    quote_data = cursor.fetchone()
    
    if not quote_data:
        response_data = {"error": "Quote not found"}
        json_response = json.dumps(response_data)
        
        return Response(json_response, 404, content_type='application/json')
    
    cursor.close()
    conn.close()
    
    quote_text, author_name, category_name = quote_data
    
    response_data = {
        "quote": quote_text, 
        "author": author_name,
        "category": category_name
    }
    
    json_response = json.dumps(response_data)
    return Response(json_response, content_type='application/json'), 200
    
# Returns the 10 quotes provided the author name
# unless the limit is provided as parameter
@app.route('/quotes/author/<string:author_name_raw>', methods=['GET'])
def get_quotes_by_author(author_name_raw: str):
    conn = psycopg2.connect(app.config['CONNECTION_STRING'])
    cursor = conn.cursor()
    author_name = escape(author_name_raw)
    limit = request.args.get('limit', default=10, type=int)
    
    # Returns the number of total quotes for the given author
    count_query = """
    SELECT COUNT(*) AS total_quotes
    FROM Quotes
    WHERE authorID = (
        SELECT ID FROM Authors 
        WHERE name ILIKE %s
    );
    """
    
    quotes_query = """
    SELECT Quotes.text
    FROM Quotes
    WHERE authorID = (
        SELECT Authors.ID FROM Authors
        WHERE Authors.name ILIKE %s)
    LIMIT %s;
    """
    
    cursor.execute(count_query, (author_name,))
    quote_count = cursor.fetchone()
    
    cursor.execute(quotes_query, (author_name, limit,))
    quotes = [quote[0] for quote in cursor.fetchall()]
    
    # No quotes found
    if quote_count[0] < 1:
        response_data = {
            "error": "quotes not found!"
        }
        json_response = json.dumps(response_data)
        return Response(json_response, 404, content_type='application/json')
    
    author_name = author_name.title()
    response_data = {
        "total quotes available": quote_count[0],
        "amount of quotes returned": len(quotes),
        "author": author_name,
        "quotes": quotes
    }
    
    json_response = json.dumps(response_data)
    return Response(json_response, 200, content_type='application/json')