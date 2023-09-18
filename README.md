# Quotes-API

![Project logo](https://i0.wp.com/blog.logoscdn.com/wp-content/uploads/2016/06/quote-620x324.jpg)

Welcome to the Quotes API project! This API allows you to manage and retrieve quotes, authors, and categories for inspirational and motivational content.

## Prerequistes
Before you begin, ensure you have met the following requirements:
- Python3
- virtualenv

### Installation
Clone this repository:
```shell
git clone https://github.com/MehakKambo/quotes-api.git
cd quotes-api
```

Create and Activate virtual environment:
```shell
python3 -m venv env
source env/bin/activate
```

Install all the dependencies:
```shell
pip install -r requirements.txt
```

Running the API
```shell
Flask run
```

Your Flask server will begin running and can be accessed at [http://127.0.0.1:5000](http://127.0.0.1:5000)
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

## Run the SQL Script
``` bash
\i /path/to/the/schema.sql 
```

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository.
2. Create your feature branch: 
```shell
git checkout -b feature-name
```
3. Commit Your changes:
```shell
git commit -m 'Add some feature'
```
4. Push to the branch:
```shell
git push origin feature-name
```
5. Submit a pull request.


## License
This project is licensed under the MIT License.