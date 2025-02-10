--import genre list from file
CREATE TABLE IF NOT EXISTS tmp (
    genre TEXT
);

.mode csv
.import genre.csv tmp

INSERT INTO genres (genre) SELECT (genre) FROM tmp;

DROP TABLE tmp;