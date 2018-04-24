#!/bin/bash
date1="`date '+%m%d'`"
date2="`date -d "1 day ago" '+%m%d'`"
test -s $HOME/cRio-data-reduction/log/checkfiles/checkfiles$date1.log && cat $HOME/cRio-data-reduction/log/checkfiles/checkfiles$date1.log |mail -s "Error: Missing Files" andrew.kovachik@canada.ca,kovachik.andrew@gmail.com

test -s $HOME/cRio-data-reduction/log/graphing/graphing$date1.log && cat $HOME/cRio-data-reduction/log/graphing/graphing$date1.log | mail -s "Graph Log" andrew.kovachik@canada.ca, kovachik.andrew@gmail.com

cat $HOME/cRio-data-reduction/filetransfer.log | mail -s "Transfer Log" andrew.kovachik@canada.ca, kovachik.andrew@gmail.com

test -s $HOME/cRio-data-reduction/log/recordlrt/recordlrt$date1.log && cat $HOME/cRio-data-reduction/log/recordlrt/recordlrt$date1.log | mail -s "Interference Log" andrew.kovachik@canada.ca, kovachik.andrew@gmail.com

test -s $HOME/cRio-data-reduction/log/rt1hz/rt1hz$date1.log && cat $HOME/cRio-data-reduction/log/rt1hz/rt1hz$date1.log | mail -s "rt1hz Log" andrew.kovachik@canada.ca, kovachik.andrew@gmail.com

cat $HOME/cRio-data-reduction/lrtRecords/lrtRecords$date2.txt | mail -s 'lrt records' andrew.kovachik@canada.ca, kovachik.andrew@gmail.com
