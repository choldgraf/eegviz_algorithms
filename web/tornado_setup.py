from tornado import ioloop, web, httpserver
import tornado
import requests
import json
import pandas as pd
import time
import numpy as np
from eeg_viz import algorithms as api
from IPython import embed
from bokeh.plotting import output_server, line, figure, curplot, show, cursession
from bokeh.objects import Glyph
import ipdb


class MainHandler(web.RequestHandler):
    def initialize(self):
        self.database = {}
        self.database_raw = {}

    def handle_data(self, Fs=512, band='alpha'):
        ## Data processing 
        df = api.read_dump(self.data_json, quality_cutoff=5)
        # If there is only one username that comes in, it'll be read out as a larger array
        if df.shape[0] > 500:
            df = api.convert_to_short_format(df)
        df = api.unravel_raw_values(df, raw_label='data')
        grp_id = df.groupby(level='id')
        for i_id, vals in grp_id:
            self.database_raw[i_id] = vals
        self.data = grp_id.apply(api.extract_band, Fs, band, kind='power')

        if VIZ:
            # Viz
            y_disp = self.ds.data['y']
            y_disp = np.roll(y_disp, 1)
            y_disp[-1] = self.data.mean()
            self.ds.data["y"] = y_disp
            cursession().store_objects(self.ds)
            time.sleep(.10)
        print self.data
        print self.database_raw

    def get(self):
        self.write("Hello, world")

    def post(self):
        self.data_json = self.get_argument('data')

        if VIZ:
            renderer = [r for r in curplot().renderers if isinstance(r, Glyph)][0]
            self.ds = renderer.data_source
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

        self.write(self.data.to_json())
        self.flush()


def main(port=8989, viz=False):
    application = web.Application([(r"/", MainHandler)])
    http_server = httpserver.HTTPServer(application)
    http_server.listen(port)
    tornado.ioloop.IOLoop.instance().start()

VIZ = True

if __name__ == "__main__":
    if VIZ:
        # Note - run python bokeh-server first
        output_server('Server plotting')
        last_ten_y = np.zeros(10)
        last_ten_x = np.arange(10)
        figure(x_range=[0, 10], tools="pan,wheel_zoom,box_zoom,reset,previewsave")
        line(last_ten_x, last_ten_y)
        show()
    main()