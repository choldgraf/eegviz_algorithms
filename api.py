import scipy as sp
import numpy as np
import mne
import pandas as pd

'''This is a brief document detailing some of the functionality that we’d
like to have in our API for processing EEG signals from multiple people. 
It should be an evolving collection of functions / classes, written
in Python. Eventually, this will hopefully make its way into the actual 
unction documentation.'''


# Functions
def extract_band(signal, freq_band, kind='timeseries'):
    '''Extract information at a particular frequency band in the signal.
    This will extract either the amplitude across time, or a single
    value for power of a particular frequency band in 'signal'. 

    INPUTS
    ------
    signal : {float, array-like}
        The EEG signals, assumed to be time x channels.
    freq_band : {tuple w/ 2 ints, 'delta', 'theta', 'alpha', 'beta', 'gamma']
        The frequency band to extract. If 
    kind : {'timeseries', 'power'}
        Whether to extract the analytic amplitude over time ('timeseries')
        or a single value for the power ('power') in the data.

    RETURNS:
    timeseries, band amplitude over time or single value for power
     '''
     pass


def 


