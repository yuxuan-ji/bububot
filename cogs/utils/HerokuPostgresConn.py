# A module containing a connection to bububot's heroku postgres server
# To use this connection, do 'from HerokuPostgresConn import conn, c'


def get_conn():
    '''Uses DATABASE_URL env variable defined on Heroku's server
    Returns (connection, cursor)'''
    import os
    import psycopg2
    import urllib.parse as urlparse

    urlparse.uses_netloc.append("postgres")
    url = urlparse.urlparse(os.environ["DATABASE_URL"])  # DATABASE_URL is an env var in Heroku's server environnement
    
    conn = psycopg2.connect(
                            database=url.path[1:],
                            user=url.username,
                            password=url.password,
                            host=url.hostname,
                            port=url.port
                            )
    
    c = conn.cursor()  # The cursors executes SQL statements
    return conn, c


def get_conn_shell():
    '''Manually grab DATABASE_URL from the shell *requires heroku on shell
    Returns (connection, cursor)'''
    import psycopg2
    import subprocess
    
    proc = subprocess.Popen('heroku config:get DATABASE_URL -a bububot', stdout=subprocess.PIPE, shell=True)
    db_url = proc.stdout.read().decode('utf-8').strip()
    
    conn = psycopg2.connect(db_url)
    c = conn.cursor()  # The cursors executes SQL statements

    return conn, c


def get_conn_manual(db_url):
    '''Takes an inputed DATABASE_URL and returns (connection, cursor)'''
    import psycopg2

    conn = psycopg2.connect(db_url)
    c = conn.cursor()  # The cursors executes SQL statements

    return conn, c