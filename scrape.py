import config
import psycopg2
from psycopg2.extras import execute_values
import requests
import time
import threading

def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(host=config.POSTGRES_HOST,database=config.POSTGRES_DB, user=config.POSTGRES_USER, password=config.POSTGRES_PASSWORD)

        # create a cursor
        cur = conn.cursor()

        return conn, cur
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

def disconnect(conn, cur):
    if cur is not None:
        cur.close()
        print('Cursor connection closed.')
    if conn is not None:
        conn.close()
        print('Database connection closed.')

def scrapebikes(conn, cur):
    """Scrape bike information"""
    print('Scraping bikes')
    payload = {'format': 'json', 'fields': 'lat,lon,isReserved,isDisabled,createdAt,lastSeenAtPos,linger_time_minutes,linger_time_hours,linger_time_days', 'authorization': config.APIKEY}
    req = requests.get('http://nodes.geoservices.tamu.edu/api/veoride/bikes/', params=payload)
    print('Finished scraping bikes')
    insertbikes(req, conn, cur)

def insertbikes(request, conn, cur):
    print('Starting bikes insert')
    sql = "DELETE FROM bikes"
    cur.execute(sql)
    data = request.json()
    columns = data[0].keys()
    query = "INSERT INTO bikes (\"{}\") VALUES %s".format('","'.join(columns))
    values = [[value for value in bike.values()] for bike in data]
    execute_values(cur, query, values)
    conn.commit()
    print('Finished bikes insert')
    biketimer = threading.Timer(600.0, scrapebikes, [conn, cur])
    biketimer.start()

def scrapetrips(conn, cur):
    print('Strarting trips scrape')
    lastten = int(time.time() * 1000) - 1800000 # Want to get current time - 10 minutes
    payload = {'format': 'json', 'end_time_gte': lastten, 'fields': 'start_time,end_time,start_latitude,start_longitude,end_latitude,end_longitude', 'authorization': config.APIKEY}
    req = requests.get('https://nodes.geoservices.tamu.edu/api/veoride/trips/', params=payload)
    print('Finished trips scrape')
    inserttrips(req, conn, cur)

def inserttrips(request, conn, cur):
    print('Starting trips insert')
    data = request.json()
    columns = data[0].keys()
    query = "INSERT INTO trips (\"{}\") VALUES %s".format('","'.join(columns))
    values = [[value for value in trip.values()] for trip in data]
    execute_values(cur, query, values)
    conn.commit()
    print('Finished trips insert')
    triptimer = threading.Timer(1800.0, scrapetrips, [conn, cur])
    triptimer.start()

if __name__ == '__main__':
    conn, cur = connect()
    scrapebikes(conn, cur)
    scrapetrips(conn, cur)
