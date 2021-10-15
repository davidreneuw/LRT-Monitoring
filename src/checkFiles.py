#!/nrn/home/NRN/drene/anaconda3/bin/python
import os.path
import syslog
import logging
import logging.config
from datetime import date, timedelta, datetime
from pathlib import Path
import subprocess
import configparser

USER = os.path.expanduser('~')
config = configparser.ConfigParser()
config.read('option.conf')
BASE = config['PATHS']['file_directory']
IS_DEV = config['DEV']['is_dev']

# Creates logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

# Gets date
if IS_DEV == "True":
  day = "27"
  month = "04"
else:
  day = datetime.today().strftime('%d')
  month = datetime.today().strftime('%m')

# Sets handler
handler = logging.FileHandler(
        USER + BASE +'/log/checkfiles/checkfiles%s%s.log'%(month, day)
        )
logger.addHandler(handler)

# Sets format
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

fmt2 = lambda x : "%02d" % x  #format hours,month,day
fmt3 = lambda x : "%03d" % x  #format Day of year

if IS_DEV == "True":
  day = "27"
  month = "04"
  year = "2020"
else:
  yesterday = date.today()-timedelta(1)
  day = yesterday.strftime('%d')
  month = yesterday.strftime('%m')
  year = yesterday.strftime('%Y')



for loc in ['LRE','LRO','LRS']:
    for hour in range(1,24):
        my_file = Path(
                USER + '/lrt/%s/Analog/%s/%s%s%s%s[%s]v100Hz.tdms'
                %(loc, year, loc, year, month, day, fmt2(hour))
                )

        if my_file.exists() == False:
            logger.warning(
                    'File not found for %s%s%s%s[%s]v100Hz.tdms'
                    %(loc, year, month, day, fmt2(hour))
                    )


    my_file = Path(
            USER + '/lrt/%s/Serial/%s/%s%s%s%sv1sec.tdms'
            %(loc, year, loc, year, month, day))

    if my_file.exists() == False:
        logger.warning(
                'File not found for %s%s%s%sv1sec.tdms'
                %(loc, year, month, day)
                )
