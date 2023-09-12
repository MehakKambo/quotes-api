-- Create the Authors table
CREATE TABLE Authors (
  id SERIAL NOT NULL,
  name VARCHAR(150) NOT NULL,

  PRIMARY KEY (id)
);

-- Create the Categories table
CREATE TABLE Categories (
  id SERIAL NOT NULL,
  name VARCHAR(100) NOT NULL,

  PRIMARY KEY (id)
);

-- Create the Quotes table
CREATE TABLE Quotes (
  id SERIAL NOT NULL,
  text TEXT NOT NULL,
  authorID INTEGER NOT NULL,
  categoryID INTEGER NOT NULL,

  PRIMARY KEY (id),
  FOREIGN KEY (authorID) REFERENCES Authors(id) DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY (categoryID) REFERENCES Categories(id) DEFERRABLE INITIALLY DEFERRED
);
