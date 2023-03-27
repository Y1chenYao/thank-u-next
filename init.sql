CREATE DATABASE IF NOT EXISTS project;

USE project;
DROP TABLE IF EXISTS reviews;

CREATE TABLE reviews(
    id int DEFAULT NULL,
    professor varchar(255),
    overall int,
    difficulty int,
    work int,
    review varchar(2000),
    course varchar(255),
    course_id int
);

-- INSERT INTO reviews VALUE(1,'I''m Watching You','Bruce and Kris Jenner celebrate their anniversary. Kim and Tommy Davis buy themselves a stripper pole as a gift, and the youngest Jenner plays on it. Kim appears on The Tyra Banks Show Where she is interviewed about Kim''s sex tape. Kourtney deals with relationship drama.');

INSERT INTO reviews VALUE(0,'Laura Barre',3,3,2,'I took this class with Roger Figueroa, Joanna Fiddler, and Laura Barre. The content of the class is really interesting and useful in everyday life. There are 5 easy in-class assignments, a quiz, and 3 exams. You don''t have to go to class and the workload is light, but exams are all multiple choice with really specific questions that you need to memorize off the slides.  ','NS 1150',0)