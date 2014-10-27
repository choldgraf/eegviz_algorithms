import scipy as sp
import numpy as np
import mne
import pandas as pd
from mne.time_frequency import multitaper_psd
from mne.filter import band_pass_filter
from IPython import embed

freq_dict = {'delta': [-np.inf, 4],
             'theta': [4, 7],
             'alpha': [8, 15],
             'beta': [16, 31],
             'gamma': [32, 70]}

__all__ = ['convert_to_short_format',
           'extract_raw_values',
           'extract_band',
           'extract_freq_power',
           'read_dump',
           'unravel_raw_values']


# Munging and I/O
def convert_to_short_format(df, pull_cols=['start_time', 'end_time', 'username']):
    data_str = str(df['data'].values)
    # Reset index so we have access to start_time again
    stt, end, usr = df.reset_index().iloc[0, :][pull_cols]
    data_concat = np.array([df['data'].values, stt, end, usr])
    df = pd.DataFrame(data_concat[None, :], columns=['data']+pull_cols).set_index(['start_time'])
    return df


def unravel_raw_values(df, freq='2ms', raw_label='raw_values', id_label='username'):
    '''
    Unravels the values in "raw_values" so that we can concatenate
    across multiple timepoints, subjects, etc.
    
    raw_values contains an array of timepoints over 2 seconds, this basically
    turns it into a different entry for each number, and interpolates the
    timing between the first/last timepoint.
    
    INPUTS
    --------
    df : (pandas DataFrame)
        The dataframe from a raw dump that you want unraveled.
    freq : (str)
        The period of the input signal (roughly). AKA, 1/Fs
    '''
    vals_df = []
    for ix, row in df.iterrows():
        vals = extract_raw_values(row, raw_label=raw_label)
        
        # Create time index for given set of vals, assuming Fs is 512Hz
        vals_ix = pd.date_range(df.index[0], periods=vals.shape[0], freq=freq)
        id_ix = [row[id_label]] * len(vals_ix)
        columns = [raw_label]
        new_ix = pd.MultiIndex.from_arrays([vals_ix, id_ix], names=['time', 'id'])
        vals_df.append(pd.DataFrame(vals, index=new_ix, columns=columns))
    vals_df = pd.concat(vals_df)
    return vals_df


def read_dump(dump_path, kind='json', quality_cutoff=5,
              dtype_list_of_ints=['signal_quality']):
    '''
    Reads in data in the form of a csv file (located at dump_path).
    Note that it must have a very particular structure, so if variables
    change, this will probably break.
    '''
    # Pull data from dump
    if kind == 'csv':
        df = pd.read_csv(dump_path)
    elif kind == 'json':
        df = pd.read_json(dump_path)
    df = df.set_index(['start_time'])
    df = df.replace('\N', np.NaN).dropna(axis=0)
    df[dtype_list_of_ints] = df[dtype_list_of_ints].astype(int)
    df.index = pd.to_datetime(df.index)
    df = df.sort().query('signal_quality < @quality_cutoff')
    return df


def extract_raw_values(series, raw_label='raw_values'):
    '''Simple function to extract the "raw_values" field of a series and
    do some quick string processing on it.
    '''
    data_label = series[raw_label]
    if isinstance(data_label, str):
        return np.array(data_label.strip('{}').split(',')).astype(int)
    else:
        return np.array(data_label).astype(int)


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
            raise NameError("freq_band must be one of: {0}".format(freq_dict.keys()))
    else:
        try:
            lo, hi = freq_band
        except (ValueError, TypeError):
            raise NameError('You need to supply a two-length value, or a string for freq_band')
            
    if kind == 'timeseries':
        signal_out = band_pass_filter(signal.T, Fs, lo, hi)
    elif kind == 'power':
        psd, psd_freqs = multitaper_psd(signal.T, Fs, lo, hi)
        signal_out = np.mean(psd)
    return signal_out    


def extract_freq_power(signal, Fs, apply_log=True):
    '''Extracts the full PSD for an input signal. Assumes
    that the signal is time x sources
    '''
    psd, freqs_psd = multitaper_psd(signal.T, Fs)
    if apply_log:
        psd = np.log(psd)
    return psd, freqs_psd