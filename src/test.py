import pandas as pd
import numpy as np
from datetime import datetime, timedelta

columns = ['loc', 'year', 'time', 'x', 'y', 'z', 'f']
for i in np.arange(108, 327):
    try:
        # This section is meant to replicate exactly how data is loaded in formatdata.py
        print("Day %s."%i)
        filename = ("/nrn/home/NRN/drene/crio-data-reduction/ottSecData/2021/OTT2021%s.sec")%i
        df = pd.read_fwf(filename, header=None, names=columns)
        t = datetime.strptime(df['time'][0], '%j:%H:%M:%S')
        df['time'] = df['time'].map(lambda x:float((datetime.strptime(x, '%j:%H:%M:%S') - t).total_seconds()))
        raw = [df['x'], df['y'], df['z'], df['f']]
        data = raw.copy()
        fstar = np.sqrt(data[0]**2 + data[1]**2 + data[2]**2)
        print("Day %s worked."%i)
    except TypeError:
        print("======== DAY %s DID NOT WORK, SCANNING..."%i)
        for e in range(3):
            print(("Column {} has {} elements.".format(e, len(data[e]))))
            for j in range(len(data[e])-1):
                try:
                    float(data[e][j+1])
                except:
                    print("Non float detected at position {index}: ".format(index=j+1)+data[e][j+1])
            print("--------------------")