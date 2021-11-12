#!/bin/bash

echo "retrieving 2020 data from OTT"

year=2020

rsync -azOv --timeout=60 --bwlimit=100 drene@ssh.seismo.nrcan.gc.ca:/daqs/geomag_data/GSC/real_time/magnetic/$year/OTT$year* \
/$HOME/crio-data-reduction/ottSecData/$year
