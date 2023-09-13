# Quotes-API

## Tentative Endpoints
1. **Retrieve Random Quote**
   - **Endpoint:** `/quotes/random`
   - **Method:** GET
   - **Description:** Returns a randomly selected quote from the database.

2. **Retrieve Quote by ID**
   - **Endpoint:** `/quotes/{id}`
   - **Method:** GET
   - **Description:** Retrieves a specific quote by its unique identifier (ID).

3. **List Quotes by Author**
   - **Endpoint:** `/quotes/author/{authorName}`
   - **Method:** GET
   - **Description:** Retrieves a list of quotes by a specific author.

4. **List Quotes by Category**
   - **Endpoint:** `/quotes/category/{categoryName}`
   - **Method:** GET
   - **Description:** Retrieves a list of quotes belonging to a specific category.

5. **Search Quotes**
   - **Endpoint:** `/quotes/search`
   - **Method:** GET
   - **Description:** Allows users to search for quotes based on keywords, author names, or categories.

6. **Add a New Quote**
   - **Endpoint:** `/quotes`
   - **Method:** POST
   - **Description:** Allows users to submit new quotes to be added to the database.

7. **Update Quote**
   - **Endpoint:** `/quotes/{id}`
   - **Method:** PUT or PATCH
   - **Description:** Allows users to update an existing quote by providing new text, author, or category.

8. **Delete Quote**
   - **Endpoint:** `/quotes/{id}`
   - **Method:** DELETE
   - **Description:** Allows users to delete a quote from the database by its ID.

9. **List All Authors**
   - **Endpoint:** `/authors`
   - **Method:** GET
   - **Description:** Retrieves a list of all authors from the database.

10. **List All Categories**
    - **Endpoint:** `/categories`
    - **Method:** GET
    - **Description:** Retrieves a list of all categories for quotes.


## Database Schema  
![Alt Text](https://github.com/MehakKambo/quotes-api/blob/main/schema.png)

## SQL Script
``` bash
\i /path/to/the/schema.sql 
```