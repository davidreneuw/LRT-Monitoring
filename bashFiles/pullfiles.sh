#!/bin/bash

echo "retrieving data from OTT "

year=$(date +"%Y")

rsync -azOv geomag_ops@132.156.100.222:/daqs1_data/geomag_data/real_time/magnetic/OTT2018* $HOME/git/crio-data-reduction/ottSecData/$year
