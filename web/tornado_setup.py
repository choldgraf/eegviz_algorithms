from tornado import ioloop, web, httpserver
import tornado
import requests
import json
import pandas as pd
from eeg_viz import algorithms as api
from IPython import embed


class MainHandler(web.RequestHandler):
    def handle_data(self, Fs=512, band='alpha'):
        df = api.read_dump(self.data_json, quality_cutoff=5)
        df = api.unravel_raw_values(df)
        print type(band)
        self.data = df.groupby(level='id').apply(api.extract_band, Fs, band, kind='power')
        print self.data

    def get(self):
        self.write("Hello, world")

    def post(self):
        self.data_json = self.get_argument('data')
        try:
            band = self.get_argument('band')
        except web.MissingArgumentError:
            band = 'alpha'
            print('No band provided, setting to default ({0})'.format(band))

        try:
            Fs = self.get_argument('Fs')
        except web.MissingArgumentError:
            Fs = 512
            print('No Fs provided, setting to default ({0})'.format(Fs))

        if isinstance(band, unicode):
            band = str(band)
        self.handle_data(band=band, Fs=Fs)


def main(port=8989):
    application = web.Application([(r"/", MainHandler)])
    http_server = httpserver.HTTPServer(application)
    http_server.listen(port)
    tornado.ioloop.IOLoop.instance().start()


# In[4]:

if __name__ == "__main__":
    main()