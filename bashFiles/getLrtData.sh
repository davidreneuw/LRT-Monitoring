echo retrieving data from LRO
rsync -azOv --timeout=60 rt_daq@132.156.101.161://U/data/Serial/Port_1/LRO/2018/ /home/dcalp/lrt/LRO/Serial/2018
rsync -azOv --timeout=60 rt_daq@132.156.101.161://U/data/Serial/Port_4/LRO/2018/ /home/dcalp/lrt/LRO/Serial/2018
rsync -azOv --timeout=60 rt_daq@132.156.101.161://U/data/Analog/LRO/2018/ /home/dcalp/lrt/LRO/Analog/2018

echo retrieving data from LRE
rsync -azOv --timeout=60 rt_daq@72.142.185.22://U/data/Serial/Port_1/LRE/2018/ /home/dcalp/lrt/LRE/Serial/2018
rsync -azOv --timeout=60 rt_daq@72.142.185.22://U/data/Serial/Port_4/LRE/2018/ /home/dcalp/lrt/LRE/Serial/2018
rsync -azOv --timeout=60 rt_daq@72.142.185.22://U/data/Analog/LRE/2018/ /home/dcalp/lrt/LRE/Analog/2018
   
echo retrieving data from LRS
rsync -azOv --timeout=60 rt_daq@72.142.185.20://U/data/Serial/Port_1/LRS/2018/ /home/dcalp/lrt/LRS/Serial/2018
rsync -azOv --timeout=60 rt_daq@72.142.185.20://U/data/Serial/Port_4/LRS/2018/ /home/dcalp/lrt/LRS/Serial/2018
rsync -azOv --timeout=60 rt_daq@72.142.185.20://U/data/Analog/LRS/2018/ /home/dcalp/lrt/LRS/Analog/2018
   
echo retrieving data from LRS
rsync -azOv admin@132.156.101.160://U/data/Serial/Port_1/NM1/2018/ /home/dcalp/lrt/NM1/Serial/2018
rsync -azOv admin@132.156.101.160://U/data/Serial/Port_4/NM1/2018/ /home/dcalp/lrt/NM1/Serial/2018
rsync -azOv admin@132.156.101.160://U/data/Analog/NM1/2018/ /home/dcalp/lrt/NM1/Analog/2018
