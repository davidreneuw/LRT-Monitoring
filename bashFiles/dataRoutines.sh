#!/bin/sh
$HOME/anaconda3/bin/python $HOME/cRio-data-reduction/src/checkFiles.py
$HOME/anaconda3/bin/python $HOME/cRio-data-reduction/src/rt1hz.py
$HOME/anaconda3/bin/python $HOME/cRio-data-reduction/src/recordlrt.py
$HOME/anaconda3/bin/python $HOME/cRio-data-reduction/src/graph.py
