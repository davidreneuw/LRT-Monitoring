"""
Andrew Kovachik

@ Natural Resources Canada
This file will search through LRT folders and create a text file for
the 1hz real time data. This data is created by taking the 32hz data
filtering it to 1hz and then resampling that data to 1hz
"""
import logging
import logging.config
import os.path
from datetime import timedelta
import datetime
from decimal import Decimal, ROUND_HALF_UP
from formatdata import MakeData, Date, Data
from correctrotation import find_best_scalar, find_best_tri_rot
import configparser

# Loading configs
USER = os.path.expanduser('~')
config = configparser.ConfigParser()
config.read(USER+'/crio-data-reduction/option.conf')
BASE = config['PATHS']['file_directory']
IS_DEV = config['DEV']['is_dev']
LRT_PATH = config['PATHS']['lrt_file_directory']
SAVE_DIR = config['GRAPH']['secNew_dir']
# Creates logger
date = Date(0)
if IS_DEV == "True":
  date.y="2020"
  date.m="04"
  date.d="27"
  date.j="118"
logging.filename = (USER + BASE+ '/log/rt1hz/rt1hz%s%s.log'%(
    date.m, date.d))
logging.config.fileConfig(USER + BASE+'/logging.conf')
logger = logging.getLogger('rt1hz')

# fmt2 just takes a number and formats it to two digits before the decimal
# used it enough to make a program
fmt2 = lambda x: "%02d" % x
fmt3 = lambda x: "%03d" % x
fmt5 = lambda x: "%05d" % x

class FailedToCollectDataError(Exception):
    pass

def main(loc='LRE', xback=2):
  with open(USER+BASE+'/log/lastday.txt') as f:
    data = f.readlines()[0]
    lst = data.split("-")
    lastday = datetime.date(int(lst[2]), int(lst[1]), int(lst[0]))
  delta = timedelta(1)
  
  
  data = MakeData() # start data class
  procDate = Date(xback)
  if IS_DEV == "True":
    procDate.y="2020"
    procDate.m="04"
    procDate.d="25"
    procDate.j="116"
    procDate.dateObj = datetime.date(2020, 4, 25)
  
  while lastday <= procDate.dateObj and not (lastday > procDate.dateObj):
    #-----COLLECT DATA------#
  
    # PREVIOUS DAY
    hour = '23'
    cdate = lastday-timedelta(1) #day3
    dayObj = Date(1)
    [dayObj.y, dayObj.m, dayObj.d] = [cdate.year, cdate.month, cdate.day]
    
    try:
      data.add_tdms(loc, dayObj, hour)
      chop1 = len(data.data[0]) # used for removing extra days later
      logger.info('Got previous Day')
    except FileNotFoundError:
      chop1 = len(data.data[0])
      logger.warning('FailedToCollectDataError: ' + 'File for {}/{}/{} hour: {} location: {} not found'.format(dayObj.y, dayObj.m, dayObj.d, hour, loc))
  
    # MAIN DAY
    for hour in range(24):
      hour = fmt2(hour)
      cdate = lastday
      dayObj = Date(1)
      [dayObj.y, dayObj.m, dayObj.d] = [cdate.year, cdate.month, cdate.day]
      try:
        data.add_tdms(loc, dayObj, hour)
        logger.info('Hour %s fine', hour)
      except FileNotFoundError:
        logger.warning('FailedToCollectDataError: ' + 'File for {}/{}/{} hour: {} location: {} not found'.format(dayObj.y, dayObj.m, dayObj.d, hour, loc))
  
    # NEXT DAY
    temp = len(data.data[0])
    hour = '00'
    cdate = lastday+timedelta(1)
    dayObj = Date(1)
    [dayObj.y, dayObj.m, dayObj.d] = [cdate.year, cdate.month, cdate.day]
    try:
      data.add_tdms(loc, dayObj, hour)
      chop2 = len(data.data[0]) - temp
      logger.info('Got next Day')
    except FileNotFoundError:
      chop2 = len(data.data[0]) - temp
      logger.warning('FailedToCollectDataError: ' + 'File for {}/{}/{} hour: {} location: {} not found'.format(dayObj.y, dayObj.m, dayObj.d, hour, loc))
      
  
    #----FORMAT DATA----#
    logger.debug('Before any filtering' +
                   'Data len: {} Data looks like: {}'.format(
                       len(data.data[2]), data.data[2]))

    try:
      sizebefore = len(data.time)
      data.filtsample(.5, 1*60*60*26, 100)
      sizeafter = len(data.time)
    
      chop1 = int(round(chop1*sizeafter/sizebefore))
      chop2 = int(round(chop2*sizeafter/sizebefore))
      data.chop(chop1, chop2)
    
      #print('Filtered Length: ' + str(len(data.time)))
      #ott = Data('sec', procDate, 'OTT', 
      #           ('/daqs/geomag_data/real_time/magnetic/' + procDate.y + '/'))
      dayObj = Date(1)
      [dayObj.y, dayObj.m, dayObj.d] = [lastday.year, lastday.month, lastday.day]
      try:
        data.add_tdms(loc, dayObj, hour=None, ppm=True)
      except:
        logger.warning("Could not add v1sec data for {}/{}/{}, location: {}, file not found.".format(dayObj.y, dayObj.m, dayObj.d, loc))
      # TODO: Determine is second scalar should be removed
      # Often all terms in second scalr =~ 1
        
      #print('OTT 1Hz Time  Length: ' + str(len(ott.time)))
      #print('OTT 1Hz Data  Length: ' + str(len(ott.data[0])))
    
      """
      try:
        data.data[:3] = find_best_scalar(data.data[:3], ott.data[:3],
                                            return_scaled=True)
        data.data[:3] = find_best_tri_rot(data.data[:3], ott.data[:3],
                                              .1, return_rotated=True)
        data.data[:3] = find_best_scalar(data.data[:3], ott.data[:3],
                                            return_scaled=True)
      except ValueError as err:
        logger.error(err)
      except:
        raise
      """
    except:
      logger.error("Could not format data. Not enough data.") 
  
    #----SAVE DATA-----#
    #try:
    
    file_name = (LRT_PATH+'/%s/RT1Hz/%s/%s%s%02d%02dvsec.sec'
                  %(loc,dayObj.y,loc,dayObj.y,int(dayObj.m),int(dayObj.d)))
    logger.debug(file_name)
  
    with open(file_name, 'w', 1) as data_base:
      logger.debug('Making database for day')
      for iterate, time in enumerate(data.time):
        time = Decimal(time)
        time = Decimal(time.quantize(Decimal('.001'), rounding=ROUND_HALF_UP))
        time, mili = divmod(time, 1)
        minute, second = divmod(time, 60)
        hour, minute = divmod(minute, 60)
        hour = hour%24
        mili = str(mili).split('.')
        time = "%02d:%02d:%02d:%s" % (hour, minute, second, mili[1])
        data_base.write('%s-%s-%s %s %s    %s %s %s %s\n'
        %(
                                  dayObj.y,
                                  dayObj.m,
                                  dayObj.d,
                                  time,
                                  dayObj.j,
                                  '%.2f'%data.data[0][iterate],
                                  '%.2f'%data.data[1][iterate],
                                  '%.2f'%data.data[2][iterate],
                                  '%.2f'%data.data[3][iterate])
                            )
  
    logger.info('Done')
    #except:
    #  logger.error("Could not save data.")
    lastday += delta
    

if __name__ == '__main__':
    for place in ['LRE','LRS','LRO']:
        main(loc=place)

