#!/home/akovachi/anaconda3/bin/python
"""
Author Andrew Kovachik

Natural Resources Canada

This program will take tdms files in the one hour format
and output a text file for when there was activity
"""
# Default Packages
import logging
import logging.config
import os.path
from os.path import expanduser
import configparser as cp
from datetime import datetime
# Third Party Packages
import numpy as np
# Custom Packages
from formatdata import Date, Data, get_std_dev

# Creates logger
USER = expanduser('~') + '/git'
date = Date(0)
logging.filename = (USER + '/crio-data-reduction/log/recordlrt/recordlrt%s%s.log'%(
        date.m,date.d))
logging.config.fileConfig(USER + '/crio-data-reduction/logging.conf')
logger = logging.getLogger('recordlrt')

fmt2 = lambda x: "%02d" % x  #format hours,month,day
fmt3 = lambda x: "%03d" % x  #format Day of year


class Config(): #customization options
    def __init__(self, date, samp_freq):
        self.config = cp.RawConfigParser()
        self.config.read((USER + '/crio-data-reduction/option.conf'))
        self.samp_freq = samp_freq
        self.date = date
        self.save = expanduser(self.config.get('RECORD', 'save_dir'))
        self.lrt_dir = expanduser(self.config.get('RECORD', 'lrt_dir'))
        self.dir = None

    def direc(self, loc):
        """ Creates a directory for the location specified"""

        self.loc = loc
        self.dir = (self.lrt_dir.format(self.loc, self.date.y))


def main(xback=2):
    """
    Goes through the past day of data and creates a file for the
    times which were very active
    """
    date = Date(xback)
    time = 10
    group = 32
    cfg = Config(date, 32)



    file_name = (cfg.save + 'lrtRecords%s%s.txt'%(date.m, date.d))
    logger.info('Working on file: %s', file_name)

    with open(file_name, 'w', 1) as data_base:
        data_base.write('YYYY MM DD HH MI LOC D MAG\n')

    for loc in ['LRE', 'LRO', 'LRS']:
        for hour in range(24):
            try:
                cfg.direc(loc)

                logger.info('Opening file %s%s%s%s[%s]v%sHz.tdms',
                            loc, date.y, date.m,
                            date.d, fmt2(hour), group)

                data = Data('v32Hz', cfg.date, cfg.loc,
                            cfg.dir, hour=fmt2(hour))

                data.make_smooth(time)
                rough = data.raw 
                smooth = data.data

                logger.info('Opened file %s%s%s%s[%s]v%sHz.tdms',
                            loc, date.y, date.m,
                            date.d, fmt2(hour), group)

                for channel in range(4):
                    spikes = get_std_dev(
                        rough[channel],
                        smooth[channel],
                        group
                    )

                    if np.any(spikes):
                        record_data(spikes[0], loc, date, 
                                    fmt2(hour), channel, file_name)

            except FileNotFoundError:
                logger.warning('File Not Found %s%s%s%s[%s]v%sHz.tdms \
                        Continuing to next file. ',
                               loc, date.y, date.m, date.d, fmt2(hour), group)

            except ValueError:
                logger.error('File is corrupted empty or missing array \
                        for data %s%s%s%s[%s]v%sHz.tdms. ',
                             loc, date.y, date.m,
                             date.d, fmt2(hour), group)
            except:
                raise


def record_data(data, loc, date, hour, channel, file_name):
    """
    Goes through data and records info if there is a high
    amount of points beyond standard deviation

    :type data: numpy array
    :param data: data to be searched through for spikes

    :type loc: str
    :param loc: location that is being searched through

    :type date: class
    :param date: hold all values of the current date

    :type hour: str formated to 2 digits exp('04', '09', '15', etc)
    :param hour: the current hour being looked for in a 2 digit string

    :type channel: int
    :param channel: refers to the direction (i.e. channel) being looked at
                    0 being x, 1 being y, 2 being z, 3 being f
    """

    logger.debug(file_name)
    logger.debug(data)
    logger.debug(len(data))

    signal = ['X', 'Y', 'Z', 'F']
    logger.debug('Checking %s %s %s %s %s %s ',
                 date.y, date.m, date.d, hour, loc, signal[channel])

    while np.any(data):
        logger.debug(len(data))

        time_start = data[0]
        time_now = time_start
        count = 1

        for iterate in range(1, len(data)):
            if data[iterate] <= (time_now + 1.5):
                count += 1
                time_now = data[iterate]

        if count >= 99:
            logger.debug(
                '%s %s %s %s %s %s %s %s ',
                date.y, date.m, date.d, hour, fmt2(time_start/60),
                loc, signal[channel], count)

            with open(file_name, 'a', 1) as data_base:
                data_base.write(
                    "%s %s %s %s %s %s %s %s\n"
                    %(date.y, date.m, date.d, hour,
                      fmt2(time_start/60), loc,
                      signal[channel], count)
                    )
        for iterate in range(count):
            if not np.any(data):
                break
            data = np.delete(data, 0, 0)

if __name__ == '__main__':
    main()
