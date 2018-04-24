#!/home/akovachi/anaconda3/bin/python

"""
Author:
Andrew Kovachik

Natural Resources Canada

Version 0.6

This program will graph the previous day or day specified(will need to be
entered into this program) filter it using the python package filtfilt

If there is ever a future co-op student updating my code and are
confused you can contact me at kovachik.andrew@gmail.com

"""

# Python packages
from math import ceil
import time
import logging
import logging.config
import os.path
import configparser as cp
# Third party packages
import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
# Custom packages
from formatdata import Data, Date, make_files # custom


# Creates logger
USER=os.path.expanduser('~')
date = Date(1)
logging.filename = (USER + '/lrt_data/log/graphing/graphing%s%s.log'%(
    date.m, date.d))
logging.config.fileConfig(USER + '/lrt_data/logging.conf')
logger = logging.getLogger('graphing')

#------CLASSES----#

class FailedToCollectDataError(Exception):
    pass

class Config(): #customization options
    """Contains attributes and methods related to file specifics"""
    def __init__(self, date, loc, samp_freq, hour):
        self.config = cp.RawConfigParser()
        self.config.read((USER + '/lrt_data/option.conf'))
        self.loc = loc
        self.size = (self.config.getint('GRAPH', 'size_x'), 
                     self.config.getint('GRAPH', 'size_y')) #size of plot
        self.savedir = (self.config.get('GRAPH', 'save_dir'))
        self.samp_freq = samp_freq
        self.fmt = 'png'
        self.hour = hour
        if isinstance(self.hour, int):
            self.hour = '%02d'%(hour)

        if samp_freq == 1:
            self.save = (self.savedir +
                         '%s/%s/%s/%s/%s%s%s%s[%shz][day].png'
                         %(loc, date.y, date.m, date.d, loc,
                           date.y, date.m, date.d,
                           self.samp_freq))

        if samp_freq == 32 or samp_freq == 100:
            self.save = (self.savedir +
                         '%s/%s/%s/%s/%s%s%s%s[%shz][%s].png'
                         %(loc, date.y, date.m, date.d, loc,
                           date.y, date.m, date.d,
                           self.samp_freq, self.hour))

    def direc(self, mode, date):
        """ Returns the directory that the data can be found"""
        if mode == 'sec':
            return (self.config.get('GRAPH', 'sec_dir').format(date.y))
        if mode == 'secNew':
            return (self.config.get('GRAPH', 'secNew_dir').format(self.loc))
        if mode == 'v32Hz':
            return (self.config.get('GRAPH', 'v32Hz_dir').format(self.loc,
                                                                 date.y))

class AxisGet():
    """ Used to specify the range that the axis will show and their scale"""
    def __init__(self, mode):
        """Defines the x axis size and ticks """
        if mode == 'v32Hz' or mode == 'v100Hz':
            self.x_major = np.arange(0.0, 60.1, 10)  # x major ticks
            self.x_minor = np.arange(0.0, 60.1, 10/4)# x minor ticks
        else:
            self.x_major = np.arange(0.0, 24.1, 1)  # x major ticks
            self.x_minor = np.arange(0.0, 24.1, 1/4)# x minor ticks

        self.y_max = None # pylint: disable=invalid-unary-operand-type
        self.y_tick = None

    def yaxis(self, dat1, dat2):
        """Defines y axis size and ticks based on data """
        self.y_max = max(np.amax(np.absolute(dat1)),
                         np.amax(np.absolute(dat2))
                        )
        self.y_max = ceil(self.y_max) # max y scale
        self.y_max = ((self.y_max + 1) if
                      (self.y_max%2 == 1) else (self.y_max))

        self.y_tick = np.arange(-self.y_max,
                                self.y_max+1,
                                self.y_max/5) # y ticks

def plot(mode, loc, date, samp_freq, hour=None, ffstar=False):
    """
    Creates varying types of plots depending on the types specified

    :type mode: string (v32hz or newSec / hour plot or dayplot)
    :param mode: determined the type of plot to make

    :type loc: string
    :param loc: 3 digit all cap string for location of site

    :type date: class
    :param date: contains varying details about the date

    :type samp_freq: float
    :param date: the sampling frequency of the data being plotted

    :type hour: string or None
    :param hour: an int formated to two spaces, used if plotting hours
    """
    config = Config(date, loc, samp_freq, hour)
    axis = AxisGet(mode)

    logger.info('Working on file %s %s-%s-%s, %s',
                loc, date.y, date.m, date.d, mode)

    if isinstance(hour, int):
        logger.info('Working on hour %s', config.hour)

    #----DATA COLLECTION----#

    try:
        ott = Data('sec', date, 'OTT', config.direc('sec', date), hour=hour)
        logger.info('Got OTT data')
    except FileNotFoundError as err:
        raise FailedToCollectDataError('Could not find: OTT sec data. ' +
                                       '%s\%s\%s Hour:%s'
                                       %(date.y, date.m, date.d, hour))

    try:
        lrt = Data(mode, date, loc, config.direc(mode, date), hour=hour)
        logger.info('Got LRT data')
    except FileNotFoundError as err:
        raise FailedToCollectDataError('Could not find: %s %s data. '
                                       %(loc, mode) +
                                       '%s\%s\%s Hour:%s'
                                       %(date.y, date.m, date.d, hour))
    # Apply all data maniplulation needed
    # TODO: Make options for different data manipulations
    lrt.fstar()
    ott.fstar()
    if isinstance(hour, int): # is hour not None
        lrt.make_smooth(10)
        lrt.get_spikes(sigma=4.0)

    lrt.make_rate_change()
    lrt.make_variance()
    ott.make_variance()
    logger.info('Reformated Data')

    #---PLOT DETAILS---#
    names = ['X', 'Y', 'Z', 'F*', 'F-F*']

    # Different names for axis depending on options given
    if  mode == 'v32Hz' or mode == 'v100Hz':
        scale, span = 'Min', ('Hour '+'%02d'%(hour)+'00')
    else:
        scale, span = 'Hour', 'Whole Day'

    if ffstar:
        plots = 5
    else:
        plots = 4

    # Creating subplots
    fig, axes = plt.subplots(plots, figsize=config.size)
    fig.text(.5, .04, 'Time(%s)'%(scale), ha='center', va='center')
    fig.suptitle(
        '{0} {1}/{2}/{3} {4} {5}Hz Data'.format(
            loc, date.y, date.m, date.d, span, samp_freq),
        fontsize=20
        )

    #---PLOT MAKING---#
    logger.info('Creating plot...')

    for k in range(4):

        # Rate of change
        axtwn = axes[k].twinx()
        axtwn.plot(lrt.time, lrt.roc[k], 'r-',
                   label='Rate of Change', alpha=.3)
        logger.info('Plotter RoC')

        # LRT data
        axes[k].plot(lrt.time, lrt.data[k], 'b-',
                     label='{} Data {}'.format(loc, lrt.avg[k]))
        logger.info('Plotted %s', loc)

        # OTT data
        axes[k].plot(ott.time, ott.data[k], 'c-',
                     label='{} Data {}'.format('OTT', ott.avg[k]))
        logger.info('Plotted OTT')

        # Spikes if mode is 32hz or 100hz
        if mode == 'v32Hz' or mode == 'v100Hz':
            axes[k].plot(lrt.spikes[k][0], lrt.spikes[k][1]-lrt.avg[k],
                         'gx', markersize=10, alpha=.75)

    # F-Fstar if option is desired
    if ffstar:
        axes[4].plot(lrt.time, lrt.ffstar(),
                     label='F-F*')
        axes[4].legend(loc=2, prop={'size':12})
        axes[4].grid(which='both')

    # Subplot options
    for k in range(4):
        # y axis scale
        axis.yaxis(lrt.data[k], ott.data[k])
        axes[k].set_yticks(axis.y_tick)
        axes[k].set_ylim([-axis.y_max, axis.y_max])
        axes[k].set_xticks(axis.x_major)
        axes[k].set_xticks(axis.x_minor, minor=True)
        axes[k].grid(which='both')

        # this labels the plots
        axes[k].set_ylabel('%s variance (nT)'%(names[k]))

        # sets legends
        axes[k].legend(loc=2, prop={'size':12})

        logger.info('Added plot details')

    #--SAVING PLOT--#

    plt.tight_layout()
    fig.subplots_adjust(top=0.88)

    plt.savefig(config.save, format=config.fmt)
    plt.close('all')

    logger.info('Plot completed and saved to %s', config.save)

def __auto__(xback=2):

    date2 = Date(xback)

    start_time = time.time()

    # creates file directory for plots
    make_files(date2.y,
               date2.m,
               date2.d
              )

    #---DAYPLOT---#
    for loc in ['LRE', 'LRO', 'LRS']:
        try:
            plot('secNew', loc, date2, 1, ffstar=True)

        except FailedToCollectDataError as err:
            logger.error(err)
    #---HOURPLOT---#
    try:
        hourly_times_file =(USER + '/lrt_data/lrtRecords/lrtRecords%s%s.txt'%(date2.m, date2.d))
        if os.path.isfile(hourly_times_file):
            hourly_times = pd.read_csv(hourly_times_file, sep=' ')
            hourly_times.drop(['YYYY', 'MM', 'DD', 'MI', 'D', 'MAG'], axis=1)
            # All that remains is HH and LOC
            hourly_times.drop_duplicates()
        else:
            raise FailedToCollectDataError('FailedToCollectDataError: ' +
                                           'Could not fine "%s"'
                                           %hourly_times_file)
    except FailedToCollectDataError as err:
        logger.error(err)

    else:
        for iterate in range(len(hourly_times)):
            try:
                plot('v32Hz',
                     hourly_times.iloc[iterate].LOC,
                     date2,
                     32,
                     hour=int(hourly_times.iloc[iterate].HH)
                    )
            except FailedToCollectDataError as err:
                logger.error(err)

    print('--- %s seconds ---'%(time.time() - start_time))

if __name__ == "__main__":
    __auto__()
