from tornado import ioloop, web, httpserver
import tornado
import requests
import json
import pandas as pd
from eeg_viz import algorithms as api


class MainHandler(web.RequestHandler):
    def get(self):
        self.write("Hello, world")

    def post(self):
        data_json = self.get_argument('data')
        df = api.read_dump(data_json, quality_cutoff=5)
        print df


def main(port=8989):
    application = web.Application([(r"/", MainHandler)])
    http_server = httpserver.HTTPServer(application)
    http_server.listen(port)
    tornado.ioloop.IOLoop.instance().start()


# In[4]:

if __name__ == "__main__":
    main()