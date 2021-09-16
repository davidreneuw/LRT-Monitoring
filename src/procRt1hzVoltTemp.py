import rt1hzVoltTemp
import subprocess 
from datetime import timedelta, date

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

start_date = date(2018, 1, 1)
end_date = date(2019, 1, 1)
for single_date in daterange(start_date, end_date):
    print(single_date.strftime("%Y-%m-%d"))
    cmd = ["/nrn/home/NRN/dcalp/anaconda3/bin/python3.6"]
    cmd = cmd + ["/nrn/home/NRN/dcalp/lrtOps/git/crio-data-reduction/src/rt1hzVoltTemp.py"]
    cmd = cmd + [single_date.strftime("%Y"),single_date.strftime("%m"), single_date.strftime("%d")]
    subprocess.call(cmd)
    


