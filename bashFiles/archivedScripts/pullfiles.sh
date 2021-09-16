#!/bin/bash

echo "retrieving data from OTT "

year=$(date +"%Y")

rsync -azOv -e "ssh -i ~/.ssh/id_rsa" dcalp@ssh.seismo.nrcan.gc.ca:/daqs/geomag_data/real_time/magnetic/OTT$year* $HOME/git/crio-data-reduction/ottSecData/$year
