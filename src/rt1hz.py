"""
This file will search through LRT folders and create a text file for
the 1hz real time data. This data is created by taking the 32hz data
filtering it to 1hz and then resampling that data to 1hz
"""
import logging
import logging.config
from formatdata import MakeData, Date

# Creates logger
date = Date(0)
logging.filename = '/home/akovachi/lrt_data/log/rt1hz/rt1hz%s%s.log'%(
    date.m, date.d)
logging.config.fileConfig('/home/akovachi/lrt_data/logging.conf')
logger = logging.getLogger('rt1hz')

# fmt2 just takes a number and formats it to two digits before the decimal
# used it enough to make a program
fmt2 = lambda x: "%02d" % x
fmt3 = lambda x: "%03d" % x
fmt5 = lambda x: "%05d" % x

class FailedToCollectDataError(Exception):
    pass

def main(loc='LRE', xback=0):

    data = MakeData() # start data class

    #-----COLLECT DATA------#

    # PREVIOUS DAY
    try:
        hour = '23'
        date = Date(xback + 3) #day3
        data.add_tdms(loc, date, hour)

        chop1 = len(data.data[0]) # used for removing extra days later

        logger.info('Got previous Day')

    # MAIN DAY
        for hour in range(24):
            hour = fmt2(hour)
            date = Date(xback + 2)
            data.add_tdms(loc, date, hour)

            logger.info('Hour %s fine', hour)


        data.add_tdms(loc, date, hour=None, ppm=True)

    # NEXT DAY
        temp = len(data.data[0])

        hour = '00'
        date = Date(xback + 1)
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

    sizebefore = len(data.data[0])
    data.filtsample(.5, 1, 32)
    sizeafter = len(data.data[0])

    chop1 = int(chop1*sizeafter/sizebefore)
    chop2 = int(chop2*sizeafter/sizebefore)
    data.chop(chop1, chop2)

    #----SAVE DATA-----#
    date2 = Date(xback + 2)
    file_name = ('/home/dcalp/lrt/' +
                 '%s/RT1Hz/%s%s%s%svsec.sec'
                 %(loc, loc, date2.y, date2.m, date2.d))
    with open(file_name, 'w', 1) as data_base:
        for iterate in range(86400):

            minute, second = divmod(iterate, 60)
            hour, minute = divmod(minute, 60)
            time = "%02d:%02d:%02d:000" % (hour, minute, second)
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
    for place in ['LRO', 'LRE', 'LRS']:
        try:
            main(loc=place)
        except FailedToCollectDataError as err:
            logger.error(err)
        except:
            raise

