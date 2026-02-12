from bottle import request, response, get, post, run 
import sqlite3
import hashlib

db = sqlite3.connect('movies.sqlite')
db.set_trace_callback(print)
HOST = 'localhost'
PORT = 7007

@get('/ping')
def pong():
  response.status = 200
  return 'pong'

@post('/reset')
def reset_db():
  c = db.cursor()
  c.executescript(
    '''
      DELETE FROM performances;
      DELETE FROM tickets;
      DELETE FROM customers;
      DELETE FROM movies;
      DELETE FROM theatres;
      

      INSERT INTO theatres (t_name, capacity) VALUES
      ('Kino', 10),
      ('Regal', 16),
      ('Skandia', 100);
    '''
  )
  db.commit()

@post('/users')
def add_user():
  """
  Add user in following format:
  {
     "username": "alice",
     "fullName": "Alice Lidell",
     "pwd": "PersonWomanManCameraTV"
  }
  """
  user = request.json
  username = user["username"]
  full_name = user["fullName"]
  pwd = user["pwd"]
  hashed_pwd = hash_pwd(pwd)
  c = db.cursor()
  c.execute(
    '''
    INSERT INTO customers (username, full_name, hash_pass) VALUES
    (?, ?, ?)
    RETURNING username;
    '''
    ,
    [username, full_name, hashed_pwd]
  )
  res = c.fetchone()
  if res:
    response.status = 201
    return res[0]
  else:
    response.status = 400
    return ""
  db.commit()

def hash_pwd(pwd: str) -> str:
  hashed_pwd = hashlib.sha256(pwd.encode('utf-8')).hexdigest()
  return hashed_pwd

@post('/movies')
def add_movie():
  """
  Add movie in following format:
  {
    "imdbKey": "tt4975722",
    "title": "Moonlight",
    "year": 2016
  }
  """
  movie = request.json
  print(movie)
  imdb_key = movie["imdbKey"]
  title = movie["title"]
  year = movie["year"]
  c = db.cursor()
  c.execute(
    '''
    INSERT INTO movies (imdb_key, m_title, prod_year) VALUES
    (?, ?, ?)
    RETURNING imdb_key;
    ''',
    [imdb_key, title, year]
  )
  res = c.fetchone()
  if res:
    response.status = 201
    return f'/movies/{res[0]}'
  else:
    response.status = 400
    return ""


@post('/performances')
def add_performance():
  """
  Add performance in following format:
  {
     "imdbKey": "tt5580390",
     "theater": "Kino",
     "date": "2021-02-22",
     "time": "19:00"
  }
  """
  performance = request.json
  imdb_key = performance["imdbKey"]
  theater = performance["theater"]
  date = performance["date"]
  time = performance["time"]
  start_time = date + " " + time + ":00"
  c = db.cursor()
  c.execute(
    '''
    INSERT INTO performances (imdb_key, t_name, start_time) VALUES
    (?, ?, ?);
    ''',
    [imdb_key, theater, start_time]
  )
  res = c.fetchone()
  if res:
    response.status = 201
    return f'/performances/{res[0]}'
  else:
    response.status = 400
    return "No such movie or theater"

@get('/movies')
def get_movies():
  """
  Returns a list of all movies in following format:
  [
  {
    "imdbKey": "tt4975722",
    "title": "Moonlight",
    "year": 2016
  },
  ]
  """
  c = db.cursor()
  c.execute(
    '''
    SELECT 
    '''
  )


@get('/movies/<id>')
def get_movie_by_id(id: str):
  """
  Returns movie by id in following format:
  {
   "imdbKey": "tt4975722",
    "title": "Moonlight",
    "year": 2016
  }
  
  :param id: Description
  :type id: str
  """

@get('/performances')
def get_performances():
  """
  Returns 
  """

def main():
  run(host=HOST, port=PORT)
if __name__ == '__main__':
  main()

