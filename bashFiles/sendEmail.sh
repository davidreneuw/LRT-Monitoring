#!/bin/bash
date1="`date '+%m%d'`"
date2="`date -d "1 day ago" '+%m%d'`"
test -s $HOME/lrtOps/git/crio-data-reduction/log/checkfiles/checkfiles$date1.log && cat $HOME/lrtOps/git/crio-data-reduction/log/checkfiles/checkfiles$date1.log |mail -s "Error: Missing Files" david.calp@canada.ca

test -s $HOME/lrtOps/git/crio-data-reduction/log/graphing/graphing$date1.log && cat $HOME/lrtOps/git/crio-data-reduction/log/graphing/graphing$date1.log | mail -s "Graph Log" david.calp@canada.ca

cat $HOME/lrtOps/git/crio-data-reduction/filetransfer.log | mail -s "Transfer Log" david.calp@canada.ca

test -s $HOME/lrtOps/git/crio-data-reduction/log/recordlrt/recordlrt$date1.log && cat $HOME/lrtOps/git/crio-data-reduction/log/recordlrt/recordlrt$date1.log | mail -s "Interference Log" david.calp@canada.ca

test -s $HOME/lrtOps/git/crio-data-reduction/log/rt1hz/rt1hz$date1.log && cat $HOME/lrtOps/git/crio-data-reduction/log/rt1hz/rt1hz$date1.log | mail -s "rt1hz Log" david.calp@canada.ca

cat $HOME/git/crio-data-reduction/lrtRecords/lrtRecords$date2.txt | mail -s 'lrt records' david.calp@canada.ca
