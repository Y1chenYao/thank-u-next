CREATE DATABASE IF NOT EXISTS project;

USE project;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS cossim;

CREATE TABLE reviews(
    professor varchar(255),
    overall int,
    difficulty int,
    work int,
    review varchar(2000),
    course varchar(255),
    course_id int
);

CREATE TABLE cossim (
    prof1 varchar(255),
    prof2 varchar(255),
    cosine_similarity float
);

INSERT INTO reviews VALUE("Laura Barre",3.0,3.0,2.0,"I took this class with Roger Figueroa, Joanna Fiddler, and Laura Barre. The content of the class is really interesting and useful in everyday life. There are 5 easy in-class assignments, a quiz, and 3 exams. You don""t have to go to class and the workload is light, but exams are all multiple choice with really specific questions that you need to memorize off the slides.  ","NS1150",0);

INSERT INTO cossim VALUE ('Laura Barre', 'James Cutting', '52.713');
INSERT INTO cossim VALUE ('Laura Barre', 'Bruce Monger', '50.467');
INSERT INTO cossim VALUE ('Laura Barre', 'Anthony Bretscher', '50.425');
INSERT INTO cossim VALUE ('Laura Barre', 'Anthony Burrow', '48.17');
INSERT INTO cossim VALUE ('Laura Barre', 'Brad Wellstead', '47.259');
INSERT INTO cossim VALUE ('Laura Barre', 'David Gries', '46.643');
INSERT INTO cossim VALUE ('Laura Barre', 'Abby Drake', '46.596');
INSERT INTO cossim VALUE ('Laura Barre', 'Bruce Ganem', '43.258');
INSERT INTO cossim VALUE ('Laura Barre', 'Anne Bracy', '41.725');
INSERT INTO cossim VALUE ('Laura Barre', 'Ben Rissing', '41.264');
INSERT INTO cossim VALUE ('Laura Barre', 'Anke van Zuylen', '41.028');
INSERT INTO cossim VALUE ('Laura Barre', 'Adam Klausner', '40.536');
INSERT INTO cossim VALUE ('Laura Barre', 'Brian Crane', '38.99');
INSERT INTO cossim VALUE ('Laura Barre', 'Alice Fulton', '38.96');
INSERT INTO cossim VALUE ('Laura Barre', 'Beth Rhoades', '38.471');
INSERT INTO cossim VALUE ('Laura Barre', 'Alex Townsend', '37.542');
INSERT INTO cossim VALUE ('Laura Barre', 'Bik-Kwoon Tye', '37.389');
INSERT INTO cossim VALUE ('Laura Barre', 'Brenda Dietrich', '37.182');
INSERT INTO cossim VALUE ('Laura Barre', 'Alexander Flecker', '36.861');
INSERT INTO cossim VALUE ('Laura Barre', 'Andre Leclair', '36.734');