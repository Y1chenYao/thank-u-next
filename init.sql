CREATE DATABASE IF NOT EXISTS project;

USE project;
DROP TABLE IF EXISTS reviews;

CREATE TABLE reviews(
    id int,
    title varchar(64),
    descr varchar(1024)
);

INSERT INTO reviews VALUE(1,'I''m Watching You','Bruce and Kris Jenner celebrate their anniversary. Kim and Tommy Davis buy themselves a stripper pole as a gift, and the youngest Jenner plays on it. Kim appears on The Tyra Banks Show Where she is interviewed about Kim''s sex tape. Kourtney deals with relationship drama.');