#!/usr/bin/python
"""
Author:
Andrew Kovachik

Natural Resources Canada

Version 0.4

If you have questions about my code feel free to
send them to kovachik.andrew@gmail.com

Recent Changes:
    - Moved files from lrtMakeGraph to here to make
    lrtMakeGraph me readable

"""
# Default packages
import subprocess
import os.path
from datetime import timedelta, datetime
# 3rd party packages
import numpy as np
import pandas as pd
from nptdms import TdmsFile
from scipy import signal
import logging
import configparser

USER = os.path.expanduser('~')
config = configparser.ConfigParser()
config.read('option.conf')
BASE = config['PATHS']['file_directory']
LRT_PATH = config['PATHS']['lrt_file_directory']

class UnknownFileType(Exception):
    pass

fmt2 = lambda x: "%02d" % x  #format hours,month,day
fmt3 = lambda x: "%03d" % x  #format Day of year

class Date():
    """Custom data class I used so the values have leading zeroes"""
    def __init__(self, delta):
        date = datetime.today()-timedelta(delta)
        self.d = fmt2(int(date.strftime('%d')))
        self.m = fmt2(int(date.strftime('%m')))
        self.j = fmt3(int(date.strftime('%j')))
        self.y = date.strftime('%Y')

class Data():
    """
    Holds data for x y z f and allows the user to find averages
    variance, smooth the data, get std deviation points outside
    n number of sigma.
    """
    def __init__(self, filetype, date, site, directory, **kwargs):
        """
        Constructor

        Args
        ----
        filetype: str that refers to data file formating
        date: class that include year,month,day,doy
        site: str 3 characters long all caps
        directory: str file path to directory for file
        hour: used in the case of tdms files for which hour to use
        """

        self.date = date
        self.filetype = filetype
        self.site = site
        self.dir = directory
        self.hour = kwargs.get('hour', None)
        if isinstance(self.hour, int):
            self.hour = fmt2(self.hour)


        frmt = {'dty': self.dir, # for formating file dir
                'site' : self.site,
                'y' : date.y,
                'm' : date.m,
                'd' : date.d,
                'j' : date.j,
                'h' : self.hour
               }

        if self.filetype == 'secNew': # specify file dir
            self.file = '{dty}{site}{y}{m}{d}vsec.sec'.format(**frmt)
            self.samp_freq = 1

        elif self.filetype == 'sec':
            self.file = '{dty}{site}{y}{j}.sec'.format(**frmt)
            self.samp_freq = 1

        elif self.filetype == 'min':
            self.file = '{dty}{site}{y}{j}.min'.format(**frmt)
            self.samp_freq = 1/60

        elif self.filetype == 'v32Hz':
            self.file = '{dty}{site}{y}{m}{d}[{h}]v32Hz.tdms'.format(**frmt)
            self.samp_freq = 32
        elif self.filetype == 'v32HzVoltTemp':
            self.file = '{dty}{site}{y}{m}{d}[{h}]v32HzVoltTemp.tdms'.format(**frmt)
            self.samp_freq = 32

        elif self.filetype == 'v100Hz':
            self.file = '{dty}{site}{y}{m}{d}[{h}]v100Hz.tdms'.format(**frmt)
            self.samp_freq = 100
        else:
            raise UnknownFileType(
                'Attribute %s does not match allowed Data file types'
                %(filetype))



        if not (self.filetype == 'v32Hz' or self.filetype == 'v32HzVoltTemp' or self.filetype == 'v100Hz'):

            if self.filetype == 'secNew':
                # time looks like HH:MM:SS:MSS
                columns = ['date', 'time', 'doy', 'x', 'y', 'z', 'f']
                data_frame = pd.read_fwf(self.file, header=None, names=columns)
                t = datetime.strptime(data_frame['time'][0], '%H:%M:%S:%f')
                data_frame['time'] = data_frame['time'].map(
                    lambda x:
                    float((datetime.strptime(x, '%H:%M:%S:%f') - t
                         ).total_seconds()))

            elif self.filetype == 'sec' or self.filetype == 'min':
                # time looks like JJJ:HH:MM:SS
                columns = ['loc', 'year', 'time', 'x', 'y', 'z', 'f']
                data_frame = pd.read_fwf(self.file, header=None, names=columns)
                t = datetime.strptime(data_frame['time'][0], '%j:%H:%M:%S')
                data_frame['time'] = data_frame['time'].map(
                    lambda x:
                    float((datetime.strptime(x, '%j:%H:%M:%S') - t
                          ).total_seconds()))
            if self.hour:
                self.time = data_frame.time/60
            else:
                self.time = data_frame.time/3600
            self.raw = [data_frame.x,
                        data_frame.y,
                        data_frame.z,
                        data_frame.f]
        else:
            self.file = TdmsFile.read(self.file)
            time = self.file[self.filetype]['sec of day'].data/60
            self.time = time-int(self.hour)*60
            self.raw = [self.file[self.filetype]['channel 1'].data,
                        self.file[self.filetype]['channel 2'].data,
                        self.file[self.filetype]['channel 3'].data,
                        self.file[self.filetype]['channel 4'].data]

        self.ppm = self.raw[3]
        self.data = self.raw.copy()
        # Currently undefined attributes
        self.roc = [0, 0, 0, 0]
        self.avg = [0, 0, 0, 0]
        self.spikes = [0, 0, 0, 0]
        self.Fstar = None

        if self.hour and not (filetype == 'v32Hz' or filetype == 'v32HzVoltTemp' or filetype == 'v100Hz'):
            self.hour_range()


    def make_smooth(self, time):
        """
        Creates a running average of the data

        :type time: int
        :param time: time in seconds to average over
        ----------
        """
        time = time * self.samp_freq
        for iterate in range(len(self.data)):
            self.data[iterate] = np.convolve(self.data[iterate],
                                             np.ones(time)/time,
                                             mode='valid')

            self.raw[iterate] = self.raw[iterate][int(time/2):-int(time/2)+1]

        self.ppm = self.ppm[int(time/2):-int(time/2)+1]
        self.time = self.time[int(time/2):-int(time/2)+1]



    def make_rate_change(self):
        """ Calculates the the rate of change bettween
        every set of data points in an array

        Args:
        ----
        samp_freq: sampling frequency used for find roc since data points are not
        always 1 sec apart

        Creates:
        -------
        A new data set with averaged data
        """
        for iterate in range(len(self.data)):
            self.roc[iterate] = rate_of_change(self.data[iterate],
                                               self.samp_freq)
    def make_variance(self):
        """ Calculates the average of an np.array and returns
        the array with the average subtracted from each data point

        Args:
        ----
        array (np.array): the data to work on

        Returns:
        -------
        a np.array: the new data set
        a float: the average of the data
        """
        for iterate in range(len(self.data)):
            self.data[iterate], self.avg[iterate] = variance(self.data[iterate])

    def get_spikes(self, sigma=4.0):
        """
        creates a list of points that were n sigma away from the norm
        """
        for iterate in range(len(self.data)):
            self.spikes[iterate] = get_std_dev(self.raw[iterate],
                                               self.data[iterate],
                                               self.samp_freq,
                                               sigma)

    def hour_range(self):
        """
        Takes day files and creates hour files out of them
        """
        #data points = samp_freq*60*24
        skip = int(self.hour) * 60 * 60 * self.samp_freq
        upto = skip + self.samp_freq * 60 * 60

        for iterate in range(len(self.data)):
            self.data[iterate] = self.data[iterate][skip:upto]

        self.time = self.time[skip:upto] - int(self.hour)*60

    def chop(self, chop1, chop2):
        """Chops of the ends of the axis to make them a certain range"""

        for iterate in range(len(self.data)):
            self.data[iterate] = self.data[iterate][chop1:-chop2]

        self.time = self.time[chop1:-chop2]

        if self.Fstar:
            self.Fstar = self.Fstar[chop1:-chop2]

    def fstar(self):
        """Creates the estimated F and saves the old one under raw"""
        self.data[3] = np.sqrt(self.data[0]**2 +
                               self.data[1]**2 +
                               self.data[2]**2)

        self.fstar = self.data[3]

    def ffstar(self):
        """Returns a numpy array of f-f*"""
        return self.fstar - self.ppm

class MakeData():
    """ Used by rt1hz.py """
    def __init__(self):
        self.data = [np.array([]),
                     np.array([]),
                     np.array([]),
                     np.array([])]
        self.time = np.array([])

    def chop(self, chop1, chop2):
        """Chops edges of paramaters"""
        for iterate in range(len(self.data)):
            self.data[iterate] = self.data[iterate][chop1:-chop2]
        self.time = self.time[chop1:-chop2]

    def add_tdms(self, loc, date, hour, ppm=False, voltTemp=False):

        datafile = GetTdms(loc, date, hour, ppm, voltTemp)
        if ppm:
            self.add_f(datafile)
        elif voltTemp:
            self.add_voltTemp(datafile)
        else:
            self.add_xyz(datafile)

    def filtsample(self, filt_freq, desr_freq, samp_freq):
        """
        Both filters then samples the inputed data

        :type filt_freq: float
        :param filt_freq: desired frequency after filter

        :type desr_freq: float
        :param desr_freq: desired sampling frquency

        :type samp_freq: float
        :param samp_freq: current sampling frequency
        """
        dif = -abs(samp_freq*60*60*26 - len(self.data[0]))
        cnt = round(len(self.time)/desr_freq)

        for iterate in range(len(self.data)):
            self.data[iterate] = butter_low_pass(self.data[iterate],
                                                 filt_freq,
                                                 samp_freq)
            self.data[iterate] = self.data[iterate][::cnt]
            self.data[iterate] = self.data[iterate][:desr_freq]
        
        self.time = self.time[::cnt] 
        self.time = self.time[:desr_freq]
    def add_xyz(self, data):
        """
        Adds the mag data to the current data

        :type data: TdmsFile
        :param data: mag data file
        """
        tdms = data.file
        for iterate in range(len(self.data)):
            group = 'v100Hz'
            channel = 'channel %s'%(iterate+1)
            self.data[iterate] = np.hstack((self.data[iterate],
                                            tdms[group][channel].data))
        self.time = np.hstack((self.time, 
                               tdms[group]['sec of day'].data))

    def add_voltTemp(self, data):
        """
        Adds the volt temp data to the current data

        :type data: TdmsFile
        :param data: mag data file
        """
        tdms = data.file
        for iterate in range(len(self.data)):
            """ The group name for voltTemp data is
            the same as xyz as determined by cRio daq """
            group = 'v32Hz'
            channel = 'channel %s'%(iterate+1)
            self.data[iterate] = np.hstack((self.data[iterate],
                                            tdms[group][channel].data))
        self.time = np.hstack((self.time, 
                               tdms[group]['sec of day'].data))
    def add_f(self, data):
        """
        Adds the ppm data

        :type data: TdmsFile
        :param data: ppm data file
        """
        time = data.file['v1sec']['sec of day'].data
        data = data.file['v1sec']['channel 1'].data
 
        #print('ppm: ' + str(len(data)))
        #print('xyz: ' + str(len(self.data[3])))        
        #self.data[3] = np.hstack((self.data[3],data[:86400]))
        
        xyz_time = np.rint(self.time)
        ppm_time = np.rint(time[:86400])
        xyz_good = np.where(xyz_time == ppm_time)[0]
        self.data[3][xyz_good] = data[xyz_good]

    def quick_fourier_plot(self, samp_freq): # used for visual debugging
        """:
        Allows for quick visual of the fft for 1 axis
        """
        import matplotlib.pyplot as plt

        fft, pxx = signal.periodogram(self.data[1], samp_freq)
        plt.loglog(fft, pxx)
        plt.show()


class GetTdms():
    """
    Used by rt1hz.py, recordLRT.py

    Creates a class for a file that the user specifies
    and allows the user to call on a group channel pairing
    to recieve its data.
    """
    def __init__(self, loc, date, hour, ppm=False, voltTemp=False):

        if ppm:
            my_file = (LRT_PATH + '/{0}/Serial/' +
                       '{1}/{0}{1}{2}{3}v1sec.tdms').format(loc, date.y,
                                                            date.m, date.d)

        elif voltTemp:
            my_file = (LRT_PATH + '/{0}/Serial/' +
                       '{1}/{2}/{0}{1}{2}{3}[{4}]v32HzVoltTemp.tdms').format(loc, date.y,
                                                                         date.m,
                                                                         date.d,
                                                                         hour)
        else:
            print((LRT_PATH + '/{0}/Analog/' +
                       '{1}/{0}{1}{2}{3}[{4}]v100Hz.tdms').format(loc, date.y,
                                                                 date.m,
                                                                 date.d,
                                                                 hour))
            my_file = (LRT_PATH + '/{0}/Analog/' +
                       '{1}/{0}{1}{2}{3}[{4}]v100Hz.tdms').format(loc, date.y,
                                                                 date.m,
                                                                 date.d,
                                                                 hour)

            """
            my_file = (LRT_PATH + '/{0}/Serial/' +
                       '{1}/{0}{1}{2}{3}[{4}]v32Hz.tdms').format(loc, date.y,
                                                                 date.m,
                                                                 date.d,
                                                                 hour)
            """
        self.file = TdmsFile.read(my_file)

    def get_data(self, samp_freq, channel, ppm=False):
        """Returns the data for a channel group selected"""
        if ppm:
            group = ('v1sec')
        else:
            group = ('v' + str(samp_freq) + 'Hz')
        channel = ('channel ' + str(channel))
        return self.file[group][channel].data


def rate_of_change(data, samp_freq):
    """Helper function for make_rate_of_change()"""
    roc = np.zeros(len(data))
    for check_time in range(1, len(data) - 1):
        roc[check_time] = ((data[check_time] -
                            data[check_time-1]) *
                           samp_freq)

    return roc

def variance(array):
    """ Helper for makeVariance"""
    avg = np.mean(array)
    array = array - avg
    return array, float('{0:.2f}'.format(avg))


def get_std_dev(raw_data, smooth_data, samp_freq, sigma=4.0):
    """ Takes the raw set of data and the time average set
    and records the data points which where sigma times the
    standard deviation away

    Args:
    ----
        smooth_data(np.array): time averaged data
        samp_freq(int): the number of samples per second of raw_data
        sigma (float): how many std dev away to look for

    Retruns:
    -------
        np.array([(float,float)],[(float,float)]): array of t,y values
        of large deviation data points
    """

    seperation = raw_data - smooth_data
    std = np.std(seperation)

    # makes an array of all (x,y) points that are outside
    # of the std deviation
    return np.array([
        [np.nan, np.nan],
        *[(num / samp_freq / 60, raw_data[num])
          for num in range(len(smooth_data))
            if ((raw_data[num] > (smooth_data[num] + (sigma*std))) or
              (raw_data[num] < (smooth_data[num] - (sigma*std))))
         ]]).transpose()




def butter_low_pass(data, desired, original, order=5):
    """ Creates the coefficients for a low pass butterworth
    filter. That can change data from its original sample rate
    to a desired sample rate

    Args:
    ----
        data (np.array): data to be filtered
c
        desirerd (int): the cutoff point for data in hz
        original (int): the initial sampling rate in hz

    Returns:
    -------
        np.array: of the data after it has been filtered

    Note:
    ----
        I find that the filter will make the data all 0's if the order
    is too high. Not sure if this is my end or scipy.signal. So work with
    CAUTION

     """
    nyq = .5 * original
    cutoff = desired / nyq
    var_b, var_a = signal.butter(order, cutoff,
                                 btype='lowpass',
                                 analog=False)
    return signal.filtfilt(var_b, var_a, data, padlen=10)

def resample_data(data, desired):
    """ Takes in a set of data and resamples the data at the
    desired frequency.

    Args:
    ----
        data (np.array): data to be operated on
        desired (int): the desired sampled points
            over the dataset

    Returns:
    -------
        np.array: of the resamples data

    Notes:
    -----
        Since signal.resample works MUCH faster when the len of
    data is a power of 2, we pad the data at the end with null values
    and then discard them after.
    """
    len_old = len(data)
    thispow2 = np.floor(np.log2(len_old))
    nextpow2 = np.power(2, thispow2 + 1)

    data = np.lib.pad(
        data,
        (0, int(nextpow2 - len_old)),
        mode='constant', constant_values=(0, 0)
        )

    len_new = len(data)
    resample = int(np.ceil(desired * len_new / len_old))
    data = signal.resample(data, resample)
    data = data[:desired]
    return data

def make_files(year, month, day):
    """
    Makes a file directory for all LRT stations
    at the chosen location
    """
    for loc in ['LRE', 'LRO', 'LRS']:
        subprocess.call(['mkdir', '-p',
                         (USER + BASE + '/plots/%s/%s/%s/%s'%(
                             loc, year, month, day))])
