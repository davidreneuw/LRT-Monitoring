"""
Andrew Kovachik

@ Natural Resources Canada
This file will search through LRT folders and create a text file for
the 1hz real time data. This data is created by taking the 32hz data
filtering it to 1hz and then resampling that data to 1hz

David Calp

Feb 2021:
Modified to batch process 32Hz Volt Temp data to 1Hz files.
"""
import logging
import logging.config
import sys
import os.path
from formatdata import MakeData, Date, Data
from correctrotation import find_best_scalar, find_best_tri_rot
from datetime import datetime,date,timedelta

USER = os.path.expanduser('~')

# fmt2 just takes a number and formats it to two digits before the decimal
# used it enough to make a program
fmt2 = lambda x: "%02d" % x
fmt3 = lambda x: "%03d" % x
fmt5 = lambda x: "%05d" % x

class FailedToCollectDataError(Exception):
    pass

def main(loc='LRE'):

    data = MakeData() # start data class

    #-----COLLECT DATA------#

    currDate = Date(0)
    yearInt = int(sys.argv[1])
    monthInt = int(sys.argv[2])
    dayInt = int(sys.argv[3])

    runDate = date(yearInt, monthInt, dayInt)
    dateOffset = date(int(currDate.y),int(currDate.m),int(currDate.d)) - runDate
    dateOffsetInDays = dateOffset.days
    procDate = Date(dateOffsetInDays)


    logger.info("processing " + loc + " " + procDate.y + "-" + procDate.m + "-" + procDate.d)
    print("processing " + loc + " " + procDate.y + "-" + procDate.m + "-" + procDate.d)
    prevDay = Date(dateOffsetInDays + 1)
    nextDay = Date(dateOffsetInDays - 1)

    
    # PREVIOUS DAY
    try:
        hour = '23'
        data.add_tdms(loc, prevDay, hour, voltTemp=True)
        chop1 = len(data.data[0]) # used for removing extra days later
        logger.info('Got previous Day')

    except FileNotFoundError:
        raise FailedToCollectDataError('FailedToCollectDataError: ' +
                                       'File for {}/{}/{} hour: {} location: {} not found'.format(
                    prevDay.y, prevDay.m, prevDay.d, hour, loc))
    # MAIN DAY
     
    try:
        for hour in range(24):
            hour = fmt2(hour)
            data.add_tdms(loc, procDate, hour, voltTemp=True)
            logger.info('Hour %s fine', hour)

    except FileNotFoundError:
        raise FailedToCollectDataError('FailedToCollectDataError: ' +
                                       '32Hz File for {}/{}/{} hour: {} location: {} not found'.format(
                    procDate.y, procDate.m, procDate.d, hour, loc))
    """
    try:
        ott = Data('sec', procDate, 'OTT', 
                       ('/daqs/geomag_data/real_time/magnetic/' + procDate.y + '/'))
        data.add_tdms(loc, procDate, hour=None, ppm=True)
    
    except FileNotFoundError:
        raise FailedToCollectDataError('FailedToCollectDataError: ' +
                                       'PPM File for {}/{}/{} hour: {} location: {} not found'.format(
                    procDate.y, procDate.m, procDate.d, hour, loc))
    """

    # NEXT DAY
    try:
        temp = len(data.data[0])

        hour = '00'
        data.add_tdms(loc, nextDay, hour, voltTemp=True)

        chop2 = len(data.data[0]) - temp
        logger.info('Got next Day')


    except FileNotFoundError:
        raise FailedToCollectDataError('FailedToCollectDataError: ' +
                                       'File for {}/{}/{} hour: {} location: {} not found'.format(
                    nextDay.y, nextDay.m, nextDay.d, hour, loc))

    #----FORMAT DATA----#

    logger.info('Before any filtering \n' +
                 'Length: {}'.format(len(data.data[1])) + '\n' +
                 'Time: {}'.format(data.time) + '\n' +
                 'Data: {}'.format(data.data[1]))
    sizebefore = len(data.time)
    data.filtsample(.5, 1*60*60*26, 32)
    sizeafter = len(data.time)
    chop1 = int(round(chop1*sizeafter/sizebefore))
    chop2 = int(round(chop2*sizeafter/sizebefore))
    data.chop(chop1, chop2)

    logger.info('After filtering \n' +
                 'Length: {}'.format(len(data.data[1])) + '\n' +
                 'Time: {}'.format(data.time) + '\n' +
                 'Data: {}'.format(data.data[1]))
    """
    # TODO: Determine is second scalar should be removed
    # Often all terms in second scalr =~ 1
    data.data[:3] = find_best_scalar(data.data[:3], ott.data[:3],
                                     return_scaled=True)
    data.data[:3] = find_best_tri_rot(data.data[:3], ott.data[:3],
                                      .1, return_rotated=True)
    data.data[:3] = find_best_scalar(data.data[:3], ott.data[:3],
                                     return_scaled=True)
    """

    #----SAVE DATA-----#
    file_name = (USER + '/lrt/' +
                 '%s/RT1HzVoltTemp/%s/%s%s%s%svsecVoltTemp.sec'
                 %(loc,procDate.y, loc, procDate.y, procDate.m, procDate.d))
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
                                procDate.y,
                                procDate.m,
                                procDate.d,
                                time,
                                procDate.j,
                                '%.2f'%data.data[0][iterate],
                                '%.2f'%data.data[1][iterate],
                                '%.2f'%data.data[2][iterate],
                                '%.2f'%data.data[3][iterate])
                           )

    logger.info('Done')

if __name__ == '__main__':

    currDate = Date(0)
    yearInt = int(sys.argv[1])
    monthInt = int(sys.argv[2])
    dayInt = int(sys.argv[3])

    runDate = date(yearInt, monthInt, dayInt)
    dateOffset = date(int(currDate.y),int(currDate.m),int(currDate.d)) - runDate
    dateOffsetInDays = dateOffset.days
    procDate = Date(dateOffsetInDays)
    
    # Creates logger
    logging.filename = (USER + '/lrtOps/git/crio-data-reduction/log/rt1hzVoltTemp/rt1hzVoltTemp%s%s%s.log'%(
        procDate.y, procDate.m, procDate.d))
    logging.config.fileConfig(USER + '/lrtOps/git/crio-data-reduction/logging.conf')
    logger = logging.getLogger('rt1hzVoltTemp')
    for place in ['LRO','LRE','LRS']:
        try:
            main(loc=place)
        except FailedToCollectDataError as err:
            logger.error(err)
        except:
            raise

