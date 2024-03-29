import config
import psycopg2
from psycopg2.extras import execute_values
import requests
import time
import threading
import signal
import sys
import datetime
from collections import defaultdict

class Scraper:
    def __init__(self):
        self.host = config.POSTGRES_HOST
        self.db = config.POSTGRES_DB
        self.user = config.POSTGRES_USER
        self.password = config.POSTGRES_PASSWORD
        self.apikey = config.APIKEY
        self.deploykey = config.DEPLOYKEY
        self.proxy_pass = config.PROXY_PASS
        self.lastran = config.LASTRAN
        self.conn, self.cur = self.connect()

    def main(self):
        try:
            self.scrapebikes(self.conn, self.cur)
            self.scrapetrips(self.lastran, 1800, self.conn, self.cur)
            # self.backtrackpos(self.conn,self.cur)
            while True: 
                    time.sleep(1)
        except KeyboardInterrupt:
            self.cleanup()

    def cleanup(self):
        print("\nAttempting to close connections and quit gracefully")
        self.disconnect(self.conn, self.cur)
        configfile = open('config.py', 'w')
        configfile.write("POSTGRES_HOST = '{}'\nPOSTGRES_DB = '{}'\nPOSTGRES_USER = '{}'\nPOSTGRES_PASSWORD = '{}'\nAPIKEY = '{}'\nDEPLOYKEY = '{}'\nPROXY_PASS = '{}'\nLASTRAN = {}"
                .format(
                    self.host,
                    self.db,
                    self.user,
                    self.password,
                    self.apikey,
                    self.deploykey,
                    self.proxy_pass,
                    self.lastran
                    )
                )
        configfile.close()
        print("Closed sucessfully")
        sys.exit(0)

    def connect(self):
        """ Connect to the PostgreSQL database server """
        conn = None
        try:
            # connect to the PostgreSQL server
            print('Connecting to the PostgreSQL database...')
            conn = psycopg2.connect(host=self.host,database=self.db, user=self.user, password=self.password)

            # create a cursor
            cur = conn.cursor()

            return conn, cur
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    def disconnect(self, conn, cur):
        if cur is not None:
            cur.close()
            print('Cursor connection closed.')
        if conn is not None:
            conn.close()
            print('Database connection closed.')

    def scrapebikes(self, conn, cur):
        """Scrape bike information"""
        print('Scraping bikes at {}'.format(str(datetime.datetime.now())))
        payload = {'format': 'json', 'fields': 'lat,lon,isReserved,isDisabled,createdAt,lastSeenAtPos,linger_time_minutes,linger_time_hours,linger_time_days', 'authorization': self.apikey}
        req = requests.get('http://nodes.geoservices.tamu.edu/api/veoride/bikes/', params=payload)
        if req.status_code != 200 or not req.json():
            print('Request Failed at ' + str(datetime.datetime.now()))
            errorfile = open('error.log', 'a+')
            errorfile.write('Request Failed at ' + str(datetime.datetime.now()))
            errorfile.close()
            biketimer = threading.Timer(600.0, self.scrapebikes, [conn, cur])
            biketimer.daemon = True
            biketimer.start()
        else: 
            print('Finished scraping bikes at {}'.format(str(datetime.datetime.now())))
            self.insertbikes(req, conn, cur)

    def insertbikes(self, request, conn, cur):
        print('Starting bikes insert')
        sql = "DELETE FROM bikes"
        cur.execute(sql)
        conn.commit()
        data = request.json()
        columns = data[0].keys()
        query = "INSERT INTO bikes (\"{}\") VALUES %s".format('","'.join(columns))
        values = [[value for value in bike.values()] for bike in data]
        execute_values(cur, query, values)
        conn.commit()
        print('Finished bikes insert')
        curtime = int(time.time() * 1000)
        for i in range(len(data)):
            data[i]['time'] = curtime
        columns = data[0].keys()
        query = "INSERT INTO historical_bikes (\"{}\") VALUES %s".format('","'.join(columns))
        values = [[value for value in bike.values()] for bike in data]
        execute_values(cur, query, values)
        conn.commit()
        print('Finished historical_bikes insert')
        biketimer = threading.Timer(300.0, self.scrapebikes, [conn, cur])
        biketimer.daemon = True
        biketimer.start()

    def scrapetrips(self, starttime, nexttime, conn, cur):
        print('Strarting trips scrape at {}'.format(str(datetime.datetime.now())))
        payload = {'format': 'json', 'end_time_gte': starttime, 'fields': 'device_id,start_time,end_time,start_latitude,start_longitude,end_latitude,end_longitude', 'authorization': self.apikey}
        req = requests.get('https://nodes.geoservices.tamu.edu/api/veoride/trips/', params=payload)
        print('Finished trips scrape at {}'.format(str(datetime.datetime.now())))
        if not req.json():
            nexttime = nexttime * 1.5
            print('No recent trips, waiting {} minutes before trying again'.format(nexttime/60))
            triptimer = threading.Timer(nexttime, self.scrapetrips, [self.lastran, nexttime, conn, cur])
            triptimer.daemon = True
            triptimer.start()
        else:
            self.inserttrips(req, conn, cur)
    def inserttrips(self, request, conn, cur):
        print('Starting trips insert')
        data = request.json()
        columns = data[0].keys()
        query = "INSERT INTO trips2 (\"{}\") VALUES %s".format('","'.join(columns))
        values = [[value for value in trip.values()] for trip in data]
        execute_values(cur, query, values)
        conn.commit()
        print('Finished trips insert')
        self.lastran = int(time.time() * 1000)
        triptimer = threading.Timer(1800.0, self.scrapetrips, [self.lastran, 1800, conn, cur])
        triptimer.daemon = True
        triptimer.start()

if __name__ == '__main__':
    Scraper().main()
