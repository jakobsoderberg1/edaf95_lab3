from bottle import request, response, get, post, run 
import sqlite3

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
  c.execute(
    """
      DELETE * FROM customers;
      DELETE * FROM movies;
      DELETE * FROM theaters;
      DELETE * FROM screenings;
      DELETE * FROM tickets;

      INSERT INTO table theaters (t_name, capacity) VALUES
      ("Kino", 10),
      ("Regal", 16 seats)
      ("Skandia", 100 seats)
    """
  )
  

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
  pass

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
  pass

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

