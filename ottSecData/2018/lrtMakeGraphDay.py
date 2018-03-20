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
from math import ceil,sqrt
from scipy import signal
from datetime import date,datetime,timedelta
from matplotlib.ticker import MultipleLocator
from dateutil.rrule import rrule,DAILY
import sys
import time
import logging
import logging.config
import numpy as np
import pandas as pd
from formatData import Data, Date, mkFiles # custom
# matplot has a weird import due to running
# an old version of python
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
plt.ioff()


# Creates logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Gets date DIFFERENT FROM DATE IN CODE
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


###################
#------CLASSES----#
###################
class Config(): #customization options
    def __init__(self,date,loc,fs):
        self.loc = loc
        self.size = (15,15) #size of plot
        self.fs = fs
        self.fmt = 'png'
        self.savedir = '/home/akovachi/lrt_data/plots/'
        self.save = (self.savedir+'%s/%s/%s/%s/%s%s%s%s%shz[filtfilt].png'
                %(loc,date.y,date.m,date.d,loc,
                    date.y,date.m,date.d,self.fs))

    def direc(self,mode,date):
        if mode == 'sec':
            return ('/home/akovachi/lrt_data/ottSecData/%s/'%(date.y))

class axisGet():
    def __init__(self):

        self.xMj = np.arange(0.0,24.1,1)  # x major ticks
        self.xMn = np.arange(0.0,24.1,1/4)# x minor ticks

    def yaxis (self,dat1,dat2):

        self.ymx = max(
                np.amax(np.absolute(dat1)),
                np.amax(np.absolute(dat2))
                )
        self.ymx = ceil(self.ymx) # max y scale
        self.ymx = ((self.ymx+1) if (self.ymx%2==1) else (self.ymx))

        self.ytc = np.arange(-self.ymx,self.ymx+1,self.ymx/5) # y ticks

def plot(
        mode,loc,date,fs,**kwargs):

    logger.info(
            'Working on file {0} {1}-{2}-{3}, {4}'.format(
                loc,date.y,month,date.d,mode))

    hour = kwargs.get('hour',None)
    config = Config(date,loc,fs)

    
    #########################
    #----DATA COLLECTION----#
    #########################

    ott = Data('sec',date,'OTT',config.direc(mode,date),hour=hour)
    logger.info('Got OTT data')
    lrt = Data(mode, date,loc,config.direc(mode,date),hour=hour)
    logger.info('Got LRT data')
    
    if not hour: # is hour not None
        lrt.makeSmooth(10)
        lrt.getSpikes(sigma = 4.0)
    
    lrt.makeRoC()
    lrt.makeVariance()

    logger.info('Creating plot for hour day')
 
    ######################
    #---PLOTTING SETUP---#
    ######################


    axis= axisGet()
    names=['X','Y','Z','F','F-F*']

    

    def setup(plots,scale,span):
        fig, ax = plt.subplots(plots,figsize=config.size)
        fig.text(.5,.04,'Time(%s)'%(scale),ha='center',va='center')
        fig.suptitle(
            '{0} {1}/{2}/{3} {4} {5}Hz Data'
            %(loc, date.y, date.m, date.d, span, group),
            fontsize=20
            )

    if not (mode=='v32Hz' or mode=='v100Hz'):
        setup(5,'Hour','Whole Day')
    else:
        setup(4,'Min',('Hour '+fmt2(hour)+'00'))

    LRT = [lrt.X, lrt.Y, lrt.Z, lrt.F]
    OTT = [ott.X, ott.Y, ott.Z, ott.F]
    ROC = [lrt.rocX, lrt.rocY, lrt.rocZ, lrt.rocF]
    AVG = [ [lrt.avgX, lrt.avgY, lrt.avgZ, lrt.avgF],
            [ott.avgX, ott.avgY, ott.avgZ, ott.avgF]]

    if (mode=='v32Hz' or mode=='v100Hz'):
        STD = [ [spikesX[0],spikesX[1]-lrt.avgX],
                [spikesY[0],spikesY[1]-lrt.avgY],
                [spikesZ[0],spikesZ[1]-lrt.avgZ],
                [spikesF[0],spikesF[1]-lrt.avgF],]

    

    ###################
    #---PLOT MAKING---#
    ###################

    for k in range(4):
        ax[k].plot(lrt.T, LRT[k], 'b-', 
                label='{} Data {}'.format(loc,AVG[0][k]))

        ax[k].plot(ott.T, OTT[k], 'b-', 
                label='{} Data {}'.format(loc,AVG[0][k]))

        axtwn = ax[k].twinx()
        axtwn.plot(lrt.T, ROC[k],'r-', 
                label='Rate of Change',alpha = .4)

        if (mode=='v32Hz' or mode=='v100Hz'):
            ax[k].plot(STD[k][0], STD[K][1], 'gx', makersize=10, alpha=.5)

        # y axis scale
        axis.yaxis(lrt.data[channel],ott.data[channel])
        ax[channel].set_yticks(axis.ytc)
        ax[channel].set_ylim([-axis.ymx,axis.ymx])
        ax[channel].set_xticks(axis.xMj)
        ax[channel].set_xticks(axis.xMn,minor=True)
        ax[channel].grid(which='both')

        # this labels the plots
        ax[channel].set_ylabel('%s variance (nT)'%(names[channel]))
    
        # sets legends
        ax[channel].legend(loc=2,prop={'size':12})

    #if not (mode=='v32Hz' or mode=='v100Hz'):





            


                

    #################
    #--SAVING PLOT--#
    #################

    plt.tight_layout()
    fig.subplots_adjust(top=0.88)
    
    plt.savefig(
            config.dir,
            format=config.fmt
            )
    plt.close('all')

    logger.info(
            'Plot completed and saved to' 
            ' %s'
            %(config.dir)
            )

    

def __auto__():
    
    date0,date1,date2,date3 = Date(0),Date(1),Date(2),Date(3)
    start_time = time.time()

    # creates file directory for plots
    mkFiles(
            date0.y,
            date0.m,
            date0.d
            )

    hourlyTimes = pd.read_table(
            '/home/akovachi/lrt_data/lrtRecords/lrtRecords%s%s.txt'
            %(date1.m,date1.d),
            sep=' '
            )
    hourlyTimes = hourlyTimes[['HH','LOC']]
    hourlyTimes = hourlyTimes.drop_duplicates()

    #---DAYPLOT---#
    for loc in ['LRE','LRO','LRS']:
        try:
            plot('sec',loc,date2,1)
       
        except:
            raise

        """try:
            _plotFF(loc,date2,)"""

    for x in range(len(hourlyTimes)):
        whichTimes = hourlyTimes.iloc[x]
        try:
            plot('v32Hz',whichTimes.LOC,date1,32)

        except:
            raise

    #---HOURLYPLOT---#

    print('--- %s seconds ---'%(time.time() - start_time))

if __name__ == "__main__":
    __auto__()
