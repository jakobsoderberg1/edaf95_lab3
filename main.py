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
  db.commit()
  if res:
    response.status = 201
    return f'/users/{res[0]}'
  else:
    response.status = 400
    return ""
  

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
  db.commit()
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
    (?, ?, ?)
    RETURNING p_id;
    ''',
    [imdb_key, theater, start_time]
  )
  res = c.fetchone()
  db.commit()
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
    SELECT    imdb_key, m_title, prod_year 
    FROM      movies
    WHERE     TRUE;      
    '''
  )
  
  found = [{'imdbKey': imdb_key,
            'title': title,
            'year': year} for imdb_key, title, year in c]
  return {'data': found}


@get('/movies/<imdb_key>')
def get_movie_by_id(imdb_key: str):
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
  c = db.cursor()
  c.execute(
    '''
    SELECT    imdb_key, m_title, prod_year
    FROM      movies
    WHERE     imdb_key = ?;
    ''',
    [imdb_key]
  )
  found = [{'imdbKey': imdb_key,
            'title': title,
            'year': year} for imdb_key, title, year in c]
  return {'data': found}

@get('/performances')
def get_performances():
  '''
  Returns a list of all performances in following format:
  {
    "performanceId": "397582600f8732a0ba01f72cac75a2c2",
    "date": "2021-02-22",
    "startTime": "19:00",
    "title": "The Shape of Water",
    "year": 2017,
    "theater": "Kino",
    "remainingSeats": 10
  }
  '''
  c = db.cursor()
  c.execute(
    '''
    SELECT    p_id, start_time, m_title, prod_year, t_name, capacity - COUNT(t_id) AS remaining_seats
    FROM      performances
              JOIN movies   USING(imdb_key)
              JOIN theatres USING(t_name)
                            LEFT JOIN tickets USING(p_id)
    GROUP BY p_id;
    '''
  )
  found = [
    {
    'performanceId': p_id,
    'date': start_time[:10],
    'startTime': start_time[11:-3],
    'title': m_title,
    'year': prod_year,
    'theater': t_name,
    'remainingSeats': remaining_seats
    }
    for p_id, start_time, m_title, prod_year, t_name, remaining_seats in c]
  return {'data': found}

@post('/tickets')
def buy_ticket():
  """
  Buys a ticket for the provided user if credentials are correct
  """
  user = request.json
  username = user['username']
  pwd = user['pwd']
  p_id = user['performanceId']
  
  c = db.cursor()
  c.execute(
    '''
    SELECT  hash_pass
    FROM    customers
    WHERE   username = ?;
    ''',

    [username]
  )
  hashed_pwd = c.fetchone()[0]
  if not hashed_pwd or hashed_pwd != hash_pwd(pwd):
    response.status = 401
    return "Wrong user credentials"
  c.execute(
    '''
    SELECT  capacity - COUNT(t_id) as remaining_seats
    FROM    performances
            JOIN    theatres USING(t_name)
                  LEFT JOIN   tickets USING(p_id)
    WHERE P_ID = ?
    GROUP BY p_id;
    ''',
    [p_id]
    )
  remaining_seats = c.fetchone()[0]
  if remaining_seats < 1:
    response.status = 400
    return "No tickets left"
  c.execute(
    '''
    INSERT INTO tickets(username, p_id) VALUES
    (?, ?)
    RETURNING t_id;
    ''',
    [username, p_id]
  )
  res = c.fetchone()
  if res:
    response.status = 201
    return f'/tickets/{res[0]}'
  else:
    response.status = 400
    return 'Error'
    


@get('/users/<username>/tickets')
def get_user_tickets(username: str):
  c = db.cursor()
  c.execute(
    '''
    SELECT    start_time, t_name, m_title, prod_year, COUNT(t_id) as nbr_of_tickets
    FROM      customers
              JOIN  tickets USING(username)
              JOIN  performances USING(p_id)
              JOIN  movies USING(imdb_key)
    WHERE username = ?
    GROUP BY  p_id;
    ''',
    [username]
  )
  found = [{
    'date': start_time[:10],
    'startTime': start_time[11:-3],
    'theater': t_name,
    'title': m_title,
    'year': prod_year,
    'nbrOfTickets': nbr_of_tickets
  } for start_time, t_name, m_title, prod_year, nbr_of_tickets in c]
  return {'data': found}

  


def main():
  run(host=HOST, port=PORT)
if __name__ == '__main__':
  main()

