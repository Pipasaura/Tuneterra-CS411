DROP DATABASE IF EXISTS TuneTerra;
CREATE DATABASE TuneTerra;
USE TuneTerra;

CREATE TABLE Champions(
    champ_id INT NOT NULL,
    champ_name VARCHAR(31) NOT NULL,
    playlist1 VARCHAR(255),
    playlist2 VARCHAR(255),
    keyword1 VARCHAR(31),
    keyword2 VARCHAR(31),
    PRIMARY KEY (champ_id)
);

INSERT INTO Champions(champ_id, champ_name, playlist1)
    VALUES (147, 'Seraphine', 'https://open.spotify.com/playlist/36Nu75l6mmj0cil6VLxSx0?si=eb8cd6ec3bcf46d4');

INSERT INTO Champions(champ_id, champ_name, playlist1)
    VALUES (222, 'Jinx', 'https://open.spotify.com/playlist/0zOi2Fe13McYfJm4TIhfzD?si=c52bfb296a59410d')

