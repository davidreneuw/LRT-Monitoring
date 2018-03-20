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

# Import Packages
from nptdms import TdmsFile
from math import ceil,sqrt
from scipy import signal
from datetime import date,datetime,timedelta
from matplotlib.ticker import MultipleLocator
from dateutil.rrule import rrule,DAILY
import sys
import time
import subprocess
import logging
import logging.config
import numpy as np
import pandas as pd
import formatData as ft # custom
# matplot has a weird import due to running
# an old version of python
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
plt.ioff()


# Creates logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Gets date
day = datetime.today().strftime('%d')
month = datetime.today().strftime('%m')

# Sets handler
handler = logging.FileHandler(
        '/home/akovachi/logFiles/graphing/graphingDay%s%s.log'%(month,day)
        )
logger.addHandler(handler)

# Sets format
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)


#fmt2 just takes a number and formats it to two digits before the decimal
#used it enough to make a program
fmt2 = lambda x : "%02d" % x  #format hours,month,day
fmt3 = lambda x : "%03d" % x  #format Day of year



def __plot__(
        loc,
        year,
        month,
        day,
        recordSpikes = True,
        group = 32, 
        DoY = fmt3(int(date.today().strftime('%j'))),
        auto = False
        ):
    """Takes the date input and ot outputs an entire day of data that has been
    filt to consider the nyquist rate

    Args:
    ----
        loc (str): one of ('LRE','LRE','LRO','LRN')
        year (int): year desired
        month (int): between 1-12
        day (int): between 1-31 depending on month
        recordSpikes (bool): if true the program will record outlier
                            data to a txt file
        group (int): either 32 or 100
        DoY (fmt3(int)): the day of year expressed as a 3 digit string
        
    Returns:
    -------
        matplotlib graph saved to the correct directory if the files exist
    Notes:
    -----
        THE DIRECTORY MUST EXIST BEFORE GRAPH IS SAVED

        The data has 4 channels [1,2,3,4]
            -1 indicates x
            -2 indicates y
            -3 indicates z
            -4 indicates F
    """
    logger.info(
            'Working on file %s %s-%s-%s '
            %(loc,year,month,day)
            )
    
    # Gets data collected by ppm device
    try:
        ppmFile = TdmsFile('/home/dcalp/lrt/'
                '%s/Serial/%s/%s%s%s%sv1sec.tdms'
                %(loc,year,loc,year,month,day))
        ppmRaw = ppmFile.object('v1sec','channel 1').data

        ppmTime = np.arange(0,len(ppmRaw)) /3600

    except:
        logger.warning(
                'The ppm data for %s-%s-%s'
                ' could not be found'
                %(year,month,day)
                )
        raise
    else:
        logger.info('OTT data collected successfully')

    x = np.array([])
    y = np.array([])
    z = np.array([])
    f = np.array([])

    nanArray = np.empty(86400)
    nanArray[:] = np.nan



    # collect 24 hours of data and append them to their 
    # respective array x,y,z
    for hour in range(24):
        try: 
            rawFile = ft.getFile(
            loc,year,month,day,fmt2(hour),group
            )
        except:
            logger.warning(
                    'The file for %s %s-%s-%s [%s] '
                    ' could not be found. Creating nan data'
                    %(loc,year,month,day,fmt2(hour))
                    )

            # append nan array for missing data
            f = np.hstack((f,nanArray))
            

        else:
            # appending new data to array
            f = np.hstack((f,np.array(ft.getData(32,4,rawFile)[0])))

            logger.info('Found hour %s00'%(fmt2(hour)))

    logger.debug('x array looks like: %s'%(x))

    # create details needed for filtfilt
    nyquistRateCutoff = .125
    butterworthFilterDegree = 10
    b, a =signal.butter(butterworthFilterDegree,nyquistRateCutoff, analog=False)
    logger.info('Butterworth filter created')
    logger.debug('Butterworth array 1: %s Butterworth array 2: %s'%(a,b))

    try:
        # for more infor on filtfilt please refer to:
        # https://docs.scipy.org/doc/scipy-0.18.1/reference/generated/scipy.signal.filtfilt.html
        logger.debug('Before filter f looks like %s %s'%(f[:500],f[-500]))
        logger.info('Filtering data')
        f = signal.filtfilt(b, a, f, padlen = 500)
        logger.debug('After filter f looks like %s %s'%(f[:500],f[-500]))
        #ppmRaw = signal.filtfilt(b,a,ppmRaw,padlen = 50)
        logger.info('Data has been filtered')

        # So there's so weird stuff being done here
        # signal.resample works MUCH faster if the length 
        # is a power of 2. So we are pad to the next power
        # sampling at 1Hz for the new size of data
        # then taking only the amount at the end we care about

        n = len(f)
        y = np.floor(np.log2(n))
        nextpow2  = np.power(2, y+1)

        f  = np.lib.pad(f , (0, int(nextpow2-n)), mode='constant',constant_values= (0,0))
        
        logger.debug('f has len: %s and looks like %s'
                %(len(f),f))

        terms = len(f)
        resample = int(np.ceil(86400/n*terms))

        f = signal.resample(f, resample)
        f = f[:86400]

        logger.debug('After resample f looks like %s %s'%(f[:500],f[:-500]))

        logger.info('Data has been resampled')
        time = np.arange(86400) / 3600


    except:
        logger.critical('Unable to preform filter. Program halting')
        raise


    # we can do this here since filtfilt does not change file size
    time1  = np.arange(len(x)) * (1 / (group*60*60)) #used for all raw

    logger.info('Creating plot for hour day')
 
    # Relates channel to direction
    ff = ppmRaw - f
    ffvar,ffavg = ft.variance(ff)
    sigma = 2

    major_ticks = np.arange(0.0,24.1,1)
    minor_ticks = np.arange(0.0,24.1,1/4)

    # Creating plot NORMAL SIZE (15,15)
    fig, ax = plt.subplots(3,figsize=(15,15))
    fig.text(.5,.04,'Time(hour)',ha='center',va='center')     
    # Sets title
    fig.suptitle(
            '%s %s/%s/%s Full Day 1Hz Data F-F*'
            %(loc,year,month,day),
            fontsize=20
            )

    logger.info('Plotting f-f* ')

    # plot 1aI: average
    if True:
        ax[0].plot(
                time[1000:-1000],
                f[1000:-1000],
                'b-',
                label='F* Data'
                )

        ax[1].plot(
                time,
                ppmRaw,
                'c-',
                label='F Data'
                )

        ax[2].plot(
                time[1000:-1000],
                ff[1000:-1000],
                'r',
                label='F-F*'
                )

    #except:
     #   raise # have not yet found an error
    #else:
     #   logger.info('Plot for LRT data sucessful ')

    logger.info('Setting plot details')        
    
    #ymax = max(
           # np.absolute(ffvar)
            #)
            
    #ymax = ceil(ymax)
    #ymax = ((ymax+1) if (ymax%2==1) else (ymax))

    
    #yticks = np.arange(-ymax,ymax+1,ymax/5)
    #ax.set_yticks(yticks)
    #ax.set_ylim([-ymax,ymax])
    for x in range(3):
        
        ax[x].set_xticks(major_ticks)
        ax[x].set_xticks(minor_ticks,minor=True)
        ax[x].grid(which='both')

    # this labels the plots
    ax[0].set_ylabel('F* (nT)')
    ax[1].set_ylabel('F (nt)')
    ax[2].set_ylabel('F-F (nt)')
        

    # sets legends
    plt.legend(loc=2,prop={'size':12})
                
    subprocess.call(['mkdir','-p','./plots/%s/%s/%s/%s'%(loc,year,month,day)])
    plt.savefig(
            '/home/akovachi/lrt_data/plots/%s/%s/%s/%s/%s%s%s%s1hz[f-f].png'
            %(loc,year,month,day,loc,year,month,day),
            format='png'
            )
    plt.close('all')

    logger.info(
            'Plot completed and saved to' 
            './plots/%s/%s/%s/%s/%s%s%s%s1Hz[f-f].png'
            %(loc,year,month,day,loc,year,month,day)
            )

    

def __auto__():
    
    yesterday = datetime.today()-timedelta(1)
    yday = fmt2(13)#fmt2(int(yesterday.strftime('%d')))
    ymonth = fmt2(int(yesterday.strftime('%m')))
    yDoY = fmt3(int(yesterday.strftime('%j')))
    yyear = yesterday.strftime('%Y')

    start_time = time.time()

    # creates file directory for plots
    ft.mkFiles(
            yyear,
            ymonth,
            yday
            )

    # creates plots
    for loc in ['LRO']:
        try:
            __plot__(
                    loc,
                    yyear,
                    ymonth,
                    yday,
                    DoY = yDoY,
                    auto = True
                    )
        except :
            logger.error:('Cannot plot data.')
            raise

    print('--- %s seconds ---'%(time.time() - start_time))

__auto__()
