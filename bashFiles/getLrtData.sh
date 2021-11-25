curYear=$(date +'%Y')

echo retrieving data from LRO
rsync -azOv --bwlimit=100 rt_daq@132.156.101.161://U/data/Serial/Port_1/LRO/$curYear/ /lrt/lrt/LRO/Serial/$curYear
rsync -azOv --bwlimit=100 rt_daq@132.156.101.161://U/data/Serial/Port_4/LRO/$curYear/ /lrt/lrt/LRO/Serial/$curYear
rsync -azOv --bwlimit=100 rt_daq@132.156.101.161://U/data/Analog/LRO/$curYear/ /lrt/lrt/LRO/Analog/$curYear
rsync -azOv --bwlimit=100 rt_daq@132.156.101.161://c/log/DFM28*.xml /lrt/lrt/LRO/ConfigFiles

echo retrieving data from LRE
rsync -azOv --bwlimit=100 rt_daq@72.142.185.22://U/data/Serial/Port_1/LRE/$curYear/ /lrt/lrt/LRE/Serial/$curYear
rsync -azOv --bwlimit=100 rt_daq@72.142.185.22://U/data/Serial/Port_4/LRE/$curYear/ /lrt/lrt/LRE/Serial/$curYear
rsync -azOv --bwlimit=100 rt_daq@72.142.185.22://U/data/Analog/LRE/$curYear/ /lrt/lrt/LRE/Analog/$curYear
rsync -azOv --bwlimit=100 rt_daq@72.142.185.22://c/log/DFM28*.xml /lrt/lrt/LRE/ConfigFiles
   
echo retrieving data from LRS
rsync -azOv --bwlimit=100 rt_daq@72.142.185.20://U/data/Serial/Port_1/LRS/$curYear/ /lrt/lrt/LRS/Serial/$curYear
rsync -azOv --bwlimit=100 rt_daq@72.142.185.20://U/data/Serial/Port_4/LRS/$curYear/ /lrt/lrt/LRS/Serial/$curYear
rsync -azOv --bwlimit=100 rt_daq@72.142.185.20://U/data/Analog/LRS/$curYear/ /lrt/lrt/LRS/Analog/$curYear
rsync -azOv --bwlimit=100 rt_daq@72.142.185.20://c/log/DFM28*.xml /lrt/lrt/LRS/ConfigFiles
   
#echo retrieving data from MC1 
#rsync -azOv admin@132.156.101.162://U/data/Serial/Port_1/MC1/2019/ /nrn/home/NRN/dcalp/lrt/MC1/Serial/2019
#rsync -azOv admin@132.156.101.162://U/data/Serial/Port_4/MC1/2019/ /nrn/home/NRN/dcalp/lrt/MC1/Serial/2019
#rsync -azOv admin@132.156.101.162://U/data/Analog/MC1/2019/ /nrn/home/NRN/dcalp/lrt/MC1/Analog/2019
