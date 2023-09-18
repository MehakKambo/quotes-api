# Quotes-API

## API Endpoints

1. **Retrieve Random Quote**
   - **Endpoint:** `/quotes/random`
   - **Method:** GET
   - **Description:** Returns a randomly selected quote from the database.

2. **Retrieve Quote by ID**
   - **Endpoint:** `/quotes/{id}`
   - **Method:** GET
   - **Description:** Retrieves a specific quote by its unique identifier (ID).

3. **List All Authors**
   - **Endpoint:** `/authors`
   - **Method:** GET
   - **Description:** Retrieves a list of all authors from the database.

4. **List Quotes by Author Name**
   - **Endpoint:** `/quotes/author/{authorName}`
   - **Method:** GET
   - **Description:** Retrieves a list of quotes by a specific author using its name.

5. **List Quotes by Author ID**
   - **Endpoint:** `/quotes/author/{authorID}`
   - **Method:** GET
   - **Description:** Retrieves a list of quotes by a specific author using its ID.

6. **List Quotes by Category Name**
   - **Endpoint:** `/quotes/category/{categoryName}`
   - **Method:** GET
   - **Description:** Retrieves a list of quotes belonging to a specific category using its name.

7. **List Quotes by Category ID**
   - **Endpoint:** `/quotes/category/{categoryID}`
   - **Method:** GET
   - **Description:** Retrieves a list of quotes belonging to a specific category using its ID.

8. **List All Categories**
   - **Endpoint:** `/categories`
   - **Method:** GET
   - **Description:** Retrieves a list of all categories for quotes.

9. **Add a New Quote**
   - **Endpoint:** `/quotes`
   - **Method:** POST
   - **Required URL Parameters:** `["quote", "author", "category"]`
   - **Description:** Allows users to submit new quotes to be added to the database.

10. **Update Quote**
    - **Endpoint:** `/quotes/{id}`
    - **Method:** PATCH
    - **URL Parameters (At least one should be present):** `["quote", "author", "category"]`
    - **Description:** Allows users to update an existing quote by providing new text, author, or category.

## Database Schema  
![Alt Text](https://github.com/MehakKambo/quotes-api/blob/main/schema.png)

## SQL Script
``` bash
\i /path/to/the/schema.sql 
```