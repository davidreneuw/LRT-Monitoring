#!/nrn/home/NRN/dcalp/anaconda3/bin/python
import os.path
import syslog
import logging
import logging.config
from datetime import date, timedelta, datetime
from pathlib import Path
import subprocess

USER = os.path.expanduser('~')
# Creates logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

# Gets date
day = datetime.today().strftime('%d')
month = datetime.today().strftime('%m')

# Sets handler
handler = logging.FileHandler(
        USER + '/lrtOps/git/crio-data-reduction/log/checkfiles/checkfiles%s%s.log'%(month, day)
        )
logger.addHandler(handler)

# Sets format
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

fmt2 = lambda x : "%02d" % x  #format hours,month,day
fmt3 = lambda x : "%03d" % x  #format Day of year

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
