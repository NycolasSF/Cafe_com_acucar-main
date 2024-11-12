-- Cria o banco de dados gamepygame
CREATE DATABASE IF NOT EXISTS gamepygame;

USE gamepygame;

CREATE TABLE IF NOT EXISTS players (
    _id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    points INT DEFAULT 0
);

INSERT INTO players (name, points)
VALUES ('Player One', 0);