.headers on
.mode column

SELECT    start_time, t_name, m_title, prod_year, COUNT(t_id) as nbr_of_tickets
    FROM      customers
              JOIN  tickets USING(username)
              JOIN  performances USING(p_id)
              JOIN  movies USING(imdb_key)
    GROUP BY username;