PRAGMA foreign_keys=OFF;

DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS screenings;
DROP TABLE IF EXISTS performances;
DROP TABLE IF EXISTS movies;
DROP TABLE IF EXISTS theatres;
DROP TABLE IF EXISTS theaters;
DROP TABLE IF EXISTS customers;

PRAGMA foreign_keys=ON;

CREATE TABLE theatres(
  t_name    TEXT PRIMARY KEY,
  capacity  INT
);

CREATE TABLE movies(
  imdb_key  TEXT PRIMARY KEY,
  m_title   TEXT,
  prod_year DATE
);

CREATE TABLE performances(
  p_id        TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
  t_name      TEXT,
  imdb_key    TEXT,
  start_time  DATETIME,
  FOREIGN KEY (t_name) REFERENCES theatres(t_name),
  FOREIGN KEY (imdb_key) REFERENCES movies(imdb_key)
);

CREATE TABLE customers(
  username   TEXT PRIMARY KEY,
  full_name  TEXT,
  hash_pass  TEXT
);

CREATE TABLE tickets(
  t_id      TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
  username  TEXT,
  p_id      TEXT,
  FOREIGN KEY (username) REFERENCES customers(username),
  FOREIGN KEY (p_id) REFERENCES performances(p_id)
);
