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

    data = MakeData() # start data class
    procDate = Date(xback)
    if IS_DEV == "True":
      procDate.y="2020"
      procDate.m="04"
      procDate.d="25"
      procDate.j="116"

    #-----COLLECT DATA------#

    # PREVIOUS DAY
    try:
        hour = '23'
        date = Date(xback + 1) #day3
        if IS_DEV=="True":
          date.y="2020"
          date.m="04"
          date.d="24"
          date.j="115"
        data.add_tdms(loc, date, hour)

        chop1 = len(data.data[0]) # used for removing extra days later
        logger.info('Got previous Day')

    # MAIN DAY
        for hour in range(24):
            hour = fmt2(hour)
            date = Date(xback)
            if IS_DEV=="True":
              date.y="2020"
              date.m="04"
              date.d="25"
              date.j="116"
            data.add_tdms(loc, date, hour)
            logger.info('Hour %s fine', hour)

    # NEXT DAY
        temp = len(data.data[0])

        hour = '00'
        date = Date(xback - 1)
        if IS_DEV=="True":
          date.y="2020"
          date.m="04"
          date.d="26"
          date.j="117"
        data.add_tdms(loc, date, hour)

        chop2 = len(data.data[0]) - temp
        logger.info('Got next Day')

    except FileNotFoundError:
        raise FailedToCollectDataError('FailedToCollectDataError: ' +
                                       'File for {}/{}/{} hour: {} location: {} not found'.format(
                    date.y, date.m, date.d, hour, loc))

    #----FORMAT DATA----#
    logger.debug('Before any filtering' +
                 'Data len: {} Data looks like: {}'.format(
                     len(data.data[2]), data.data[2]))

    sizebefore = len(data.time)
    data.filtsample(.5, 1*60*60*26, 100)
    sizeafter = len(data.time)

    chop1 = int(round(chop1*sizeafter/sizebefore))
    chop2 = int(round(chop2*sizeafter/sizebefore))
    data.chop(chop1, chop2)

    #print('Filtered Length: ' + str(len(data.time)))
    
    #ott = Data('sec', procDate, 'OTT', 
    #           ('/daqs/geomag_data/real_time/magnetic/' + procDate.y + '/'))
    data.add_tdms(loc, procDate, hour=None, ppm=True)
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

    #----SAVE DATA-----#
    date2 = Date(xback)
    if IS_DEV=="True":
      date2.y="2020"
      date2.m="04"
      date2.d="25"
      date2.j="116"
    file_name = (USER + 
                 '/lrt/%s/RT1Hz/%s/%s%s%s%svsec.sec'
                 %(loc,date2.y,loc,date2.y,date2.m,date2.d))
    logger.debug(file_name)
    from decimal import Decimal, ROUND_HALF_UP

    with open(file_name, 'w', 1) as data_base:
        logger.debug('Making database for day')
        for iterate, time in enumerate(data.time):
            
            time = Decimal(time)
            time = Decimal(time.quantize(Decimal('.001'),
                                             rounding=ROUND_HALF_UP))
            time, mili = divmod(time, 1)
            minute, second = divmod(time, 60)
            hour, minute = divmod(minute, 60)
            hour = hour%24
            
            mili = str(mili).split('.')
            time = "%02d:%02d:%02d:%s" % (hour, minute, 
                                        second, mili[1])
            data_base.write('%s-%s-%s %s %s    %s %s %s %s\n'
                            %(
                                date2.y,
                                date2.m,
                                date2.d,
                                time,
                                date2.j,
                                '%.2f'%data.data[0][iterate],
                                '%.2f'%data.data[1][iterate],
                                '%.2f'%data.data[2][iterate],
                                '%.2f'%data.data[3][iterate])
                           )

    logger.info('Done')

if __name__ == '__main__':
    for place in ['LRE','LRS','LRO']:
        try:
            main(loc=place)
        except FailedToCollectDataError as err:
            logger.error(err)
        except:
            raise

