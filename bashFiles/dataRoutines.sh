#!/bin/sh
$HOME/anaconda3/bin/python $HOME/lrt_data/src/checkFiles.py
$HOME/anaconda3/bin/python $HOME/lrt_data/src/rt1hz.py
$HOME/anaconda3/bin/python $HOME/lrt_data/src/recordlrt.py
$HOME/anaconda3/bin/python $HOME/lrt_data/src/graph.py
