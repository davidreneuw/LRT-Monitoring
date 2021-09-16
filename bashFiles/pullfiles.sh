#!/bin/bash

echo "retrieving data from OTT "

year=$(date +"%Y")

rsync -azOv /daqs/geomag_data/real_time/magnetic/$year/OTT$year* $HOME/lrtOps/git/crio-data-reduction/ottSecData/$year
