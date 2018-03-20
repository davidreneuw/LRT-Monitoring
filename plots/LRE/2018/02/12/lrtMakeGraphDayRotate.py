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
    # Gets data collected at OTT station
    try:
        ottData,ottAvg = ft.getNorm(year,day,DoY,auto,0,86400)
        ottTime = np.arange(0,len(ottData[0])) /3600
    except:
        logger.warning(
                'The OTT normal data for %s-%s-%s'
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
                    ' could not be found' 
                 %(loc,year,month,day,fmt2(hour))
                    )

            # need to fill empty time with null data
            nanArray = np.empty(115200)
            nanArray[:] = np.nan

            x = np.hstack([x,nanArray])
            y = np.hstack([y,nanArray])
            z = np.hstack([z,nanArray])
            f = np.hstack([f,nanArray])
            logger.warning('File not found using nan array')

        else:
            # appending new data to array
            x = np.hstack((x,np.array(ft.getData(32,1,rawFile)[0])))
            y = np.hstack((y,np.array(ft.getData(32,2,rawFile)[0])))
            z = np.hstack((z,np.array(ft.getData(32,3,rawFile)[0])))
            f = np.hstack((f,np.array(ft.getData(32,4,rawFile)[0])))

            

            logger.info('Found hour %s00'%(fmt2(hour)))
    # We need this info so that we can
    # preform the roation
    xvar,xavg = ft.variance(x)
    yvar,yavg = ft.variance(y)
    zvar,zavg = ft.variance(z)
    fvar,favg = ft.variance(f)

    # create details needed for filtfilt
    nyquistRateCutoff = 0.125
    butterworthFilterDegree = 10
    b, a =signal.butter(butterworthFilterDegree, nyquistRateCutoff)
    logger.info('Butterworth filter created')
    logger.debug('Butterworth array 1: %s Butterworth array 2: %s'%(a,b))

    try:
        # for more infor on filtfilt please refer to:
        # https://docs.scipy.org/doc/scipy-0.18.1/reference/generated/scipy.signal.filtfilt.html
        
        v1 = ottAvg[:3]
        v2 = np.array([xavg,yavg,zavg])

        u1 = v1 / np.linalg.norm(v1)
        u2 = v2 / np.linalg.norm(v2)

        #get cross product
        crossProduct = np.cross(u1,u2)
        #shorter name for use later idk
        t = crossProduct

        sin_phi = np.linalg.norm(crossProduct)
        cos_phi = np.dot(u1,u2)

        vx = np.array([
            [   0 ,-t[2], t[1]],
            [ t[2],   0 ,-t[0]],
            [-t[1], t[0],   0 ]])

        vx2 = np.linalg.matrix_power(vx,2)

        I = np.array([
            [1,0,0],
            [0,1,0],
            [0,0,1]])

        R = I + vx + vx2* (1-cos_phi)/(sin_phi)**2

        # A * R = B where be is the transformed orientation
        # we have to transpose A to have the axis correct
        # then transpose it back after
        logger.debug('X: %s Y: %s Z: %s'%(x,y,z))
        A = np.array([x,y,z]).transpose()
        logger.debug('After mult it looks like this: %s '%(A))
        logger.debug('Rotated axis look like %s %s %s %s'%(A[0],A[100],A[2000],A[10000]))

        B = np.matmul(A,R).transpose()
        # B[0] now x B[1] is Y B[2] is Z
        logger.debug('After mult it looks like this: %s '%(B))
        logger.debug('Rotated axis look like %s %s %s'%(B[0],B[1],B[2]))

        f = np.sqrt(B[0]**2+B[1]**2+B[2]**2)

        x,xavg = ft.variance(B[0])#signal.filtfilt(b, a, B[0], padlen = 50))
        y,yavg = ft.variance(B[1])#signal.filtfilt(b, a, B[1], padlen = 50))
        z,zavg = ft.variance(B[2])#signal.filtfilt(b, a, B[2], padlen = 50))
        f,favg = ft.variance(f)#signal.filtfilt(b, a, f, padlen = 50))


        
    except:
        logger.critical('Unable to preform filter. Program halting')
        raise


    # we can do this here since filtfilt does not change file size
    time1  = np.arange(len(x)) * (1 / (group*60*60)) #used for all raw

    logger.info('Creating plot for hour day')
 
    # Relates channel to direction
    direction=['X','Y','Z','F']
    data = [x,y,z,f]
    average = [xavg,yavg,zavg,favg]
    sigma = 2

    major_ticks = np.arange(0.0,24.1,1)
    minor_ticks = np.arange(0.0,24.1,1/4)

    # Creating plot NORMAL SIZE (15,15)
    fig, ax = plt.subplots(4,figsize=(15,15))
    fig.text(.5,.04,'Time(hour)',ha='center',va='center')    
    # Sets title
    fig.suptitle(
            '%s %s/%s/%s Full Day %sHz Data'
            %(loc,year,month,day,group),
            fontsize=20
            )


    for channel in range(4):

        logger.info('Plotting channel %s '%(direction[channel]))

        # plot 1aI: average
        try:
            ax[channel].plot(
                    time1,
                    data[channel],
                    'b-',
                    label='%s Data %s'%(loc, average[channel])
                    )
        except:
            logger.error('Plot for LRT data unsucessful ')
            raise # have not yet found an error
        else:
            logger.info('Plot for LRT data sucessful ')

            # normal data
        try:
            ax[channel].plot(
                ottTime,
                ottData[channel],
                'c-',
                label='OTT Data %s'%(ottAvg[channel])
                )
        except:
            logger.error('Error while plotting OTT data')
        else:
            logger.info('Plotting OTT data successful')

        logger.info('Setting plot details')        
    
        ymax = max(
                np.amax(np.absolute(data[channel])),
                np.amax(np.absolute(ottData[channel]))
                )
        ymax = ceil(ymax)
        ymax = ((ymax+1) if (ymax%2==1) else (ymax))

        yticks = np.arange(-ymax,ymax+1,ymax/5)
        ax[channel].set_yticks(yticks)
        ax[channel].set_ylim([-ymax,ymax])
        ax[channel].set_xticks(major_ticks)
        ax[channel].set_xticks(minor_ticks,minor=True)
        ax[channel].grid(which='both')

        # this labels the plots
        ax[channel].set_ylabel('%s variance (nT)'%(direction[channel]))
        

        # sets legends
        ax[channel].legend(loc=2,prop={'size':12})
                

    
    plt.tight_layout()
    fig.subplots_adjust(top=0.88)
    subprocess.call(['mkdir','-p','./plots/%s/%s/%s/%s'%(loc,year,month,day)])
    plt.savefig(
            '/home/akovachi/lrt_data/plots/%s/%s/%s/%s/%s%s%s%s%shz[filtrotate].png'
            %(loc,year,month,day,loc,year,month,day,group),
            format='png'
            )
    plt.close('all')

    logger.info(
            'Plot completed and saved to' 
            './plots/%s/%s/%s/%s/%s%s%s%s%shz[filtrotate].png'
            %(loc,year,month,day,loc,year,month,day,group)
            )

    

def __auto__():
    yesterday = datetime.today()-timedelta(1)
    yday = fmt2(int(yesterday.strftime('%d'))-1)
    ymonth = fmt2(int(yesterday.strftime('%m')))
    yDoY = fmt3(int(yesterday.strftime('%j'))-1)
    yyear = yesterday.strftime('%Y')

    start_time = time.time()

    # creates file directory for plots
    ft.mkFiles(
            yyear,
            ymonth,
            yday
            )

    # creates plots
    for loc in ['LRE','LRO','LRS']:
        __plot__(
                loc,
                yyear,
                ymonth,
                yday,
                DoY = yDoY,
                auto = True
                )

    print('--- %s seconds ---'%(time.time() - start_time))

__auto__()
