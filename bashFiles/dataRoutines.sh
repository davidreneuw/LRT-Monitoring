#!/bin/sh
$HOME/anaconda3/bin/python $HOME/git/crio-data-reduction/src/checkFiles.py
$HOME/anaconda3/bin/python $HOME/git/crio-data-reduction/src/rt1hz.py
$HOME/anaconda3/bin/python $HOME/git/crio-data-reduction/src/recordlrt.py
$HOME/anaconda3/bin/python $HOME/git/crio-data-reduction/src/graph.py
