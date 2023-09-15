from flask import Flask, Response, request, abort
import os
import psycopg2
from markupsafe import escape
import json

app = Flask(__name__)
app.config['CONNECTION_STRING'] = os.environ.get('CONNECTION_STRING')


#--------------------------------------------------------
# Endpoint 1                                            |
# Returns a randomly selected quote from the database.  |
#--------------------------------------------------------
@app.route("/quotes/random", methods=['GET'])
def get_random_quote():
    conn = psycopg2.connect(app.config['CONNECTION_STRING'])
    limit = request.args.get('limit', default=10, type=int)
    
    query = """
    SELECT Quotes.text, Authors.name, Categories.name
    FROM Quotes
    JOIN Authors ON Quotes.authorID = Authors.ID
    JOIN Categories ON Quotes.categoryID = Categories.ID
    ORDER BY random()
    LIMIT %s;
    """
    cursor = conn.cursor()
    cursor.execute(query, (limit,))
    response_keys = ['quote', 'author', 'category']
    quotes = [dict(zip(response_keys, quote)) for quote in cursor.fetchall()]
    cursor.close()
    conn.close()
    
    response_data = {'randomQuotes': quotes}
    json_response = json.dumps(response_data)
    
    return Response(json_response, 200, content_type='application/json')

#--------------------------------------------------------
# Endpoint 2                                            |
# Returns the quote data provided the ID of that quote  |
#--------------------------------------------------------
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


#--------------------------------------------------------
# Endpoint 3                                            |
# Returns a list of Authors                             |
#--------------------------------------------------------
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


#--------------------------------------------------------
# Endpoint 4                                            |
# Returns the 10 quotes provided the author name        |
# unless the limit is provided as parameter             |
#--------------------------------------------------------
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

#--------------------------------------------------------
# Returns the name of the author, given its ID          |
#--------------------------------------------------------
def get_author_name(author_id: int):
    conn = psycopg2.connect(app.config['CONNECTION_STRING'])
    cursor = conn.cursor()
    
    query = "SELECT name FROM Authors WHERE ID = %s;"
    cursor.execute(query, (author_id,))
    author_name = cursor.fetchone()
    
    if author_name:
        return author_name[0]    
    
    return None
    
#--------------------------------------------------------
# Endpoint 5                                            |
# Returns a list of quotes belonging to a specific      |
# author using the ID                                   |
#--------------------------------------------------------
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

#-------------------------------------------------------------
# Endpoint 6                                                 |
# Returns a list of quotes belonging to a specific category  |
#-------------------------------------------------------------
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

#--------------------------------------------------------
# Returns the name of the category, given its ID        |
#--------------------------------------------------------
def get_category_name(category_id: int):
    conn = psycopg2.connect(app.config['CONNECTION_STRING'])
    cursor = conn.cursor()
    
    query = "SELECT name FROM Categories WHERE ID = %s;"
    cursor.execute(query, (category_id,))
    category_name = cursor.fetchone()
    
    if category_name:
        return category_name[0]    
    
    return None

#--------------------------------------------------------
# Endpoint 7                                            |
# Returns a list of quotes belonging to a specific      |
# category using the ID                                 |
#--------------------------------------------------------
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

#--------------------------------------------------------
# Endpoint 8                                          |
# Returns a list of all categories for quotes           |
#--------------------------------------------------------
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

#--------------------------------------------------------
# Returns the ID of the Author, given the name          |
#--------------------------------------------------------
def get_id_from_author_name(author_name):
    if not author_name:
        return None
    
    conn = psycopg2.connect(app.config['CONNECTION_STRING'])
    cursor = conn.cursor()

    query = "SELECT ID FROM Authors WHERE name ILIKE %s"
    cursor.execute(query, (author_name,))
    author_id = cursor.fetchone()
    
    # If the author doesn't exist, add the author
    if not author_id:
        query = "INSERT INTO Authors (name) VALUES (%s) RETURNING id;"
        try:
            cursor.execute(query, (author_name,))
            conn.commit()
            author_id = cursor.fetchone()
        except (Exception, psycopg2.DatabaseError) as error:
            return {"error": error}, 500
        
    return author_id[0]


#--------------------------------------------------------
# Returns the ID of the category, given the name        |
#--------------------------------------------------------
def get_id_from_category_name(category_name):
    if not category_name:
        return None
    
    conn = psycopg2.connect(app.config['CONNECTION_STRING'])
    cursor = conn.cursor()

    query = "SELECT ID FROM Categories WHERE name ILIKE %s"
    cursor.execute(query, (category_name,))
    category_id = cursor.fetchone()
    
    # If the category doesn't exist, add the category
    if not category_id:
        query = "INSERT INTO Categories (name) VALUES (%s) RETURNING id;"
        try:
            cursor.execute(query, (category_name,))
            conn.commit()
            category_id = cursor.fetchone()
        except (Exception, psycopg2.DatabaseError) as error:
            return {"error": error}, 500
        
    return category_id[0]

#--------------------------------------------------------
# Checks if the quote already exists                    |
#--------------------------------------------------------
def quote_exists(cursor, quote):
    query = "SELECT ID FROM Quotes WHERE text ILIKE %s;"
    cursor.execute(query, (quote,))
    result = cursor.fetchone()
    
    if not result:
        return None
    
    return result[0]
    
#--------------------------------------------------------
# Endpoint 9                                            |
# Adds a new quote to the database provided the         |
# quote, author name, and the category.                 |
#--------------------------------------------------------
@app.route('/quotes', methods=['POST'])
def add_new_quote():
    # Things needed to insert a new quote
    # quote, authorID, categoryID
    conn = psycopg2.connect(app.config['CONNECTION_STRING'])
    cursor = conn.cursor()
    
    # Query parameters
    text = request.args.get('quote', default=None, type=str)
    author_name = request.args.get('author', default=None, type=str)
    category_name = request.args.get('category', default=None, type=str)
    
    # check for any missing parameters
    missing_fields = []
    if not text:
        missing_fields.append("quote text")
    if not author_name:
        missing_fields.append("author name")
    if not category_name:
        missing_fields.append("category")
    if missing_fields:
        response_data = {"error": "couldn't add the quote", "missingFields": missing_fields}
        json_response = json.dumps(response_data)
        return Response(json_response, 400, content_type='application/json')
    
    #check if quote already exists
    quote_already_exists = quote_exists(cursor, text)
    if quote_already_exists:
        return {"error": "quote already exists", "quoteID": quote_already_exists, "quote": text}
    
    author_id = get_id_from_author_name(author_name)
    category_id = get_id_from_category_name(category_name)
    
    if not isinstance(author_id, tuple) or not isinstance(category_id, tuple)\
        or author_id is None or category_id is None:
        return {"error": "couldn't complete the request, try later"} # error while inserting author
    
    query = "INSERT INTO Quotes (text, authorID, categoryID) VALUES (%s, %s, %s) RETURNING ID;"
    try:
        cursor.execute(query, (text, author_id, category_id,))
        conn.commit()
        quote_id = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        response_data = {
            "message": "successfully created a new quote",
            "quoteID": quote_id,
            "author": author_name,
            "quote": text,
            "category": category_name
        }   
        json_response = json.dumps(response_data)
        return Response(json_response, 201, content_type='application/json')
    except (Exception, psycopg2.DatabaseError) as error:
            return {"error": error}, 500
        
#--------------------------------------------------------
# Endpoint 10                                           |
# Update the quote, or the author, or the category      |
#--------------------------------------------------------
@app.route('/quotes/<int:quote_id_raw>', methods=['PATCH'])
def update_quote(quote_id_raw: int):
    conn = psycopg2.connect(app.config['CONNECTION_STRING'])
    cursor = conn.cursor()
    
    # Fields required for updates
    quote_id = escape(quote_id_raw)
    text = request.args.get('quote', default=None, type=str)
    author = request.args.get('author', default=None, type=str)
    authorID = get_id_from_author_name(author)
    category = request.args.get('category', default=None, type=str)
    categoryID = get_id_from_category_name(category)
    
    find_quote_query = "SELECT text FROM Quotes WHERE ID = %s"
    cursor.execute(find_quote_query, (quote_id,))
    existing_quote = cursor.fetchone()
    if not existing_quote:
        return Response(json.dumps({"error": "Quote was not found"}), 
                        status=404, content_type='application/json')
    
    update_quote_query = "UPDATE Quotes SET"
    
    if text:
        update_quote_query += f" text = {text},"
        
    if author:
        update_quote_query += f" authorID = {authorID},"
    
    if category:
        update_quote_query += f" categoryID = {categoryID},"
        
    update_quote_query = update_quote_query.rstrip(',') + f" WHERE ID = {quote_id};"
    try:
        cursor.execute(update_quote_query)
        conn.commit()
        conn.close()
        response_data = {
            "message": "Quote updated succesfully",
            "quoteID": quote_id
        }
        return Response(json.dumps(response_data), status=200, content_type='application/json')
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), status=500, content_type='application/json')