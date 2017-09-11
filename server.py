#!/usr/bin/python3

import datetime
import tornado.ioloop
import tornado.web
import json
import scraper
import sys
import email_sender
import schedule
import time
import threading

class MainHandler(tornado.web.RequestHandler):
    def initialize(self, database):
        self.database = database

    def get(self):
        self.database['requests'] = self.database.get('requests', 0) + 1
        self.write(self.database)

def make_app(store):
    return tornado.web.Application([
        (r"/", MainHandler, dict(database=store)),
    ])

def create_body(a):
    body = """
    %s, %s
    %s, %s
    %s
    Hyra %s
    Länk %s
    Karta %s
    Planskiss %s
    """ % (a.get('address'), a.get('area'), a.get('size'), a.get('nbr_rooms'), a.get('level'), a.get('rent'), a.get('url'), a.get('google_maps_url'), a.get('floor_plan', 'Planlösning saknas'))

    return body

def get_timestamp():
    return '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())

def create_body_json(appartment):
    return json.dumps(appartment, sort_keys=True, indent=2)

def scrape_and_check(store, username, password, gmail_user, gmail_password):
    old_appartments = store.get('appartments', [])
    old_urls = [oa.get('url') for oa in old_appartments]
    appartments = scraper.scrape(username, password)
    new_appartments = []
    for a in appartments:
        if a.get('url') not in old_urls:
            print(get_timestamp() + " NEW " + a.get('url'))
            new_appartments.append(a)

    store['appartments'] = appartments
    for a in new_appartments:
        email_sender.send_email(gmail_user, gmail_password, "Ny lgh!", create_body(a))
        break

def job(datastore, username, password, gmail_user, gmail_password):
    print(get_timestamp() + " job run")
    scrape_and_check(datastore, username, password, gmail_user, gmail_password)

def schedule_func(datastore, username, password, gmail_user, gmail_password):
    print("I'm working...")
    schedule.every(10).minutes.do(lambda: job(datastore, username, password, gmail_user, gmail_password))
    while 1:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    datastore = dict()
    username = sys.argv[1]
    password = sys.argv[2]
    gmail_user = sys.argv[3]
    gmail_password = sys.argv[4]

    schedule_thread = threading.Thread(target=schedule_func, args=(datastore, username, password, gmail_user, gmail_password))
    schedule_thread.start()

    print('Starting server')

    app = make_app(datastore)
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
