#!/bin/bash

echo "retrieving data from OTT "

year=$(date +"%Y")

rsync -azOv 132.156.100.222:/geomag_data/geomag_data/real_time/magnetic/OTT2018* /home/akovachi/lrt_data/ottSecData/$year
