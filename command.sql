CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    username VARCHAR (50) UNIQUE NOT NULL,
    password VARCHAR NOT NULL
);

CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    isbn VARCHAR NOT NULL,
    title text NOT NULL,
    author text NOT NULL,
    year integer NOT NULL
);
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    book_id integer NOT NULL,
    username VARCHAR (50) NOT NULL,
    rate integer NOT NULL,
    review text NOT NULL
);