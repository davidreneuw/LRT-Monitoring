#!/bin/bash
date1="`date '+%m%d'`"
date2="`date -d "1 day ago" '+%m%d'`"
test -s $HOME/crio-data-reduction/log/checkfiles/checkfiles$date1.log && cat $HOME/crio-data-reduction/log/checkfiles/checkfiles$date1.log |mail -s "Error: Missing Files" david.rene@nrcan-rncan.gc.ca

test -s $HOME/crio-data-reduction/log/graphing/graphing$date1.log && cat $HOME/crio-data-reduction/log/graphing/graphing$date1.log | mail -s "Graph Log" david.rene@nrcan-rncan.gc.ca

cat $HOME/crio-data-reduction/log/filetransfer.log | mail -s "Transfer Log" david.rene@nrcan-rncan.gc.ca

test -s $HOME/crio-data-reduction/log/recordlrt/recordlrt$date1.log && cat $HOME/crio-data-reduction/log/recordlrt/recordlrt$date1.log | mail -s "Interference Log" david.rene@nrcan-rncan.gc.ca

test -s $HOME/crio-data-reduction/log/rt1hz/rt1hz$date1.log && cat $HOME/crio-data-reduction/log/rt1hz/rt1hz$date1.log | mail -s "rt1hz Log" david.rene@nrcan-rncan.gc.ca

cat $HOME/crio-data-reduction/lrtRecords/lrtRecords$date2.txt | mail -s 'lrt records' david.rene@nrcan-rncan.gc.ca
