#!/bin/bash

test -s /home/akovachi/lrt_data/log/checkfiles/checkfiles`date +\%m\%d`.log && cat /home/akovachi/lrt_data/log/checkfiles/checkfiles`date +\%m\%d`.log |mail -s "Error: Missing Files" andrew.kovachik@canada.ca,kovachik.andrew@gmail.com

test -s /home/akovachi/lrt_data/log/graphing/graphing`date +\%m\%d`.log && cat /home/akovachi/lrt_data/log/graphing/graphing`date +\%m\%d`.log | mail -s "Graph Log" andrew.kovachik@canada.ca, kovachik.andrew@gmail.com

test -s /home/akovachi/lrt_data/log/graphing/graphingDay`date +\%m\%d`.log && cat /home/akovachi/lrt_data/log/graphing/graphingDay`date +\%m\%d`.log | mail -s "Graph Day Log" andrew.kovachik@canada.ca, kovachik.andrew@gmail.com

cat /home/akovachi/lrt_data/log/filetransfer/filetransfer.log | mail -s "Transfer Log" andrew.kovachik@canada.ca, kovachik.andrew@gmail.com

test -s /home/akovachi/lrt_data/log/record/record`date +\%m\%d`.log && cat /home/akovachi/lrt_data/log/record/record`date +\%m\%d`.log | mail -s "Interference Log" andrew.kovachik@canada.ca, kovachik.andrew@gmail.com

test -s /home/akovachi/lrt_data/log/rt1hz/rt1hz`date +\%m\%d`.log && cat /home/akovachi/lrt_data/log/rt1hz/rt1hz`date +\%m\%d`.log | mail -s "rt1hz Log" andrew.kovachik@canada.ca, kovachik.andrew@gmail.com
