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
    
    return Response(json_response, 200, content_type='application/json')

# Returns a list of Authors
@app.route('/authors', methods=['GET'])
def get_all_authors():
    conn = psycopg2.connect(app.config['CONNECTION_STRING'])
    cursor = conn.cursor()
    limit = request.args.get('limit', default=5, type=int)
    
    count_query = "SELECT COUNT(name) FROM Authors;" 
    cursor.execute(count_query)
    authors_count = cursor.fetchone()
    authors_count = authors_count[0]
    
    authors_query = "SELECT name FROM Authors ORDER BY name LIMIT %s;"
    cursor.execute(authors_query, (limit,))
    authors = [author[0] for author in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    if authors_count < 1:
        response_data = {
            "authors": []
        }
    else:
        response_data =  {
            "total number of authors": authors_count,
            "number of authors returned": len(authors),
            "authors": authors
        }
    
    json_response = json.dumps(response_data)
    return Response(json_response, 200, content_type='application/json')

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
    return Response(json_response, 200, content_type='application/json')
    
# Returns the 10 quotes provided the author name
# unless the limit is provided as parameter
@app.route('/quotes/author/<string:author_name_raw>', methods=['GET'])
def get_quotes_by_author(author_name_raw: str):
    conn = psycopg2.connect(app.config['CONNECTION_STRING'])
    cursor = conn.cursor()
    author_name = escape(author_name_raw)
    limit = request.args.get('limit', default=5, type=int)
    
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
    
    cursor.close()
    conn.close()
    
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

# Returns the name of the author, given its ID
def get_author_name(author_id: int):
    conn = psycopg2.connect(app.config['CONNECTION_STRING'])
    cursor = conn.cursor()
    
    query = "SELECT name FROM Authors WHERE ID = %s;"
    cursor.execute(query, (author_id,))
    author_name = cursor.fetchone()
    
    if author_name:
        return author_name[0]    
    
    return None
    
# Returns a list of quotes belonging to a specific author using the ID
@app.route('/quotes/author/<int:author_id_raw>', methods=['GET'])
def get_quotes_by_authorID(author_id_raw: int):
    conn = psycopg2.connect(app.config['CONNECTION_STRING'])
    cursor = conn.cursor()
    author_id = escape(author_id_raw)
    limit = request.args.get('limit', default=5, type=int)
    
    author_name = get_author_name(author_id)
    
    count_query = """
    SELECT COUNT(text) AS total_quotes
    FROM Quotes
    WHERE authorID =  %s;
    """
    cursor.execute(count_query, (author_id,))
    quote_count = cursor.fetchone()
    quote_count = quote_count[0]
    
    quotes_query = """
    SELECT Quotes.text 
    FROM Quotes
    WHERE Quotes.authorID = %s
    LIMIT %s;
    """
    cursor.execute(quotes_query, (author_id, limit,))
    quotes = [quote[0] for quote in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    if quote_count < 1:
        response_data = {
            "error": "quotes not found!"
        }
        json_response = json.dumps(response_data)
        return Response(json_response, 404, content_type='application/json')
    

    response_data = {
        "total quotes available": quote_count,
        "amount of quotes returned": len(quotes),
        "authorID": int(author_id),
        "authorName": author_name,
        "quotes": quotes
    }
    
    json_response = json.dumps(response_data)
    return Response(json_response, 200, content_type='application/json')

# Returns a list of quotes belonging to a specific category
@app.route('/quotes/category/<string:category_name_raw>', methods=['GET'])
def get_quotes_by_categoryName(category_name_raw: str):
    conn = psycopg2.connect(app.config['CONNECTION_STRING'])
    cursor = conn.cursor()
    category_name = escape(category_name_raw)
    limit = request.args.get('limit', default=5, type=int)
    
    count_query = """
    SELECT COUNT(*) AS total_quotes
    FROM Quotes
    WHERE categoryID = (
        SELECT ID FROM Categories 
        WHERE name ILIKE %s
    );
    """
    
    quotes_query = """
    SELECT Quotes.text 
    FROM Quotes
    WHERE Quotes.categoryID = (
        SELECT ID FROM Categories 
        WHERE Categories.name ILIKE %s
    )
    LIMIT %s;
    """
    
    cursor.execute(count_query, (category_name,))
    quote_count = cursor.fetchone()
    
    cursor.execute(quotes_query, (category_name, limit,))
    quotes = [quote[0] for quote in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    if quote_count[0] < 1:
        response_data = {
            "error": "quotes not found!"
        }
        json_response = json.dumps(response_data)
        return Response(json_response, 404, content_type='application/json')
    

    category_name = category_name.title()
    response_data = {
        "total quotes available": quote_count[0],
        "amount of quotes returned": len(quotes),
        "category": category_name,
        "quotes": quotes
    }
    
    json_response = json.dumps(response_data)
    return Response(json_response, 200, content_type='application/json')

# Returns the name of the category, given its ID
def get_category_name(category_id: int):
    conn = psycopg2.connect(app.config['CONNECTION_STRING'])
    cursor = conn.cursor()
    
    query = "SELECT name FROM Categories WHERE ID = %s;"
    cursor.execute(query, (category_id,))
    category_name = cursor.fetchone()
    
    if category_name:
        return category_name[0]    
    
    return None
    
# Returns a list of quotes belonging to a specific category using the ID
@app.route('/quotes/category/<int:category_id_raw>', methods=['GET'])
def get_quotes_by_categoryID(category_id_raw: int):
    conn = psycopg2.connect(app.config['CONNECTION_STRING'])
    cursor = conn.cursor()
    category_id = escape(category_id_raw)
    limit = request.args.get('limit', default=5, type=int)
    
    category_name = get_category_name(category_id)
    
    count_query = """
    SELECT COUNT(text) AS total_quotes
    FROM Quotes
    WHERE categoryID =  %s;
    """
    cursor.execute(count_query, (category_id,))
    quote_count = cursor.fetchone()
    quote_count = quote_count[0]
    
    quotes_query = """
    SELECT Quotes.text 
    FROM Quotes
    WHERE Quotes.categoryID = %s
    LIMIT %s;
    """
    cursor.execute(quotes_query, (category_id, limit,))
    quotes = [quote[0] for quote in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    if quote_count < 1:
        response_data = {
            "error": "quotes not found!"
        }
        json_response = json.dumps(response_data)
        return Response(json_response, 404, content_type='application/json')
    

    response_data = {
        "total quotes available": quote_count,
        "amount of quotes returned": len(quotes),
        "categoryID": int(category_id),
        "categoryName": category_name,
        "quotes": quotes
    }
    
    json_response = json.dumps(response_data)
    return Response(json_response, 200, content_type='application/json')

# Returns a list of all categories for quotes
@app.route('/categories', methods=['GET'])
def get_all_categories():
    conn = psycopg2.connect(app.config['CONNECTION_STRING'])
    cursor = conn.cursor()
    limit = request.args.get('limit', default=5, type=int)
    
    count_query = "SELECT COUNT(name) FROM Categories;"
    cursor.execute(count_query)
    total_categories = cursor.fetchone()
    total_categories = total_categories[0]
    
    categories_query = "SELECT name FROM Categories ORDER BY name LIMIT %s;"
    cursor.execute(categories_query, (limit,))
    categories = [category[0] for category in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    if total_categories < 1:
        response_data = {
            "categories": []
        }
    else:
        response_data = {
            "total number of categories": total_categories,
            "amount of categories returned": len(categories),
            "categories": categories
        }
        
    json_response = json.dumps(response_data)    
    return Response(json_response, 200, content_type='application/json')    