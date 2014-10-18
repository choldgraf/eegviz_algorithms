import scipy as sp
import numpy as np
import mne
import pandas as pd
from mne.time_frequency import multitaper_psd
from mne.filter import band_pass_filter

freq_dict = {'delta': [-np.inf, 4],
             'theta': [4, 7],
             'alpha': [8, 15],
             'beta': [16, 31],
             'gamma': [32, 70]}

__all__ = ['extract_raw_values',
           'extract_band',
           'extract_freq_power',
           'read_dump']


# Munging
def read_dump(dump_path, quality_cutoff=5,
              dtype_list_of_ints=['id', 'signal_quality']):
    '''
    Reads in data in the form of a csv file (located at dump_path).
    Note that it must have a very particular structure, so if variables
    change, this will probably break.
    '''
    # Pull data from dump
    df = pd.read_csv(dump_path).set_index(['start_time'])
    df = df.replace('\N', np.NaN).dropna(axis=0)
    df[dtype_list_of_ints] = df[dtype_list_of_ints].astype(int)
    df.index = pd.to_datetime(df.index)
    df = df.sort().query('signal_quality < @quality_cutoff')
    return df


def extract_raw_values(series):
    return np.array(series['raw_values'].strip('{}').split(',')).astype(int)


# Feature extraction
def extract_band(signal, Fs, freq_band, kind='timeseries'):
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
    if isinstance(freq_band, str):
        try:
            lo, hi = freq_dict[freq_band]
        except NameError:
            print("freq_band must be one of: {0}".format(freq_dict.keys()))    
    else:
        try:
            lo, hi = freq_band
        except (ValueError, TypeError):
            print('You need to supply a two-length value, or a string for freq_band')
            
    if kind == 'timeseries':
        signal_out = band_pass_filter(signal.T, Fs, lo, hi)
    elif kind == 'power':
        psd, psd_freqs = multitaper_psd(signal.T, Fs, lo, hi)
        signal_out = np.mean(psd)
    return signal_out    


def extract_freq_power(signal, Fs, apply_log=True):
    psd, freqs_psd = multitaper_psd(signal.T, Fs)
    if apply_log:
        psd = np.log(psd)
    return psd, freqs_psd