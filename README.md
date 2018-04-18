## New version has been overwriting by mistake.
## Currently outdated

The following is a breif explanation of the file formating for LRT.tdms filesand an explanation of the the import python files

By using the package `npTDMS` (an addition to numpy package) we can read the `.tdms` file type.
The values can be reached refering to a specific node on the tree. A tdms file is broken up into different types of objects;the root object, the group object, and the channel object. 

The root object records background info such as file name, title, and author.
The group and channel objects are related. The group object defines the type ofdata you want to look at (in our case all of the data is either 'v32Hz' or 'v100Hz' group).The channel refers to which record device you wish to look under.

For example:
Suppose you had a device that recorded 100Hz and 32Hz with 2 channels.Then you would be able to look up data under

<'100Hz', 'channel 1'>

<'100Hz', 'channel 2'>

<'32Hz', 'channel 1'>

<'32Hz', 'channel 2'>

and each would have their own set of data.


Specifics:
- The data recorded by the sites output everything under both '100Hz' and '32Hz'

- Each site has 4 channels you can call ['channel 1', 'channel 2', 'channel 3', 'channel 4'] 

-channel 1 refers to X 

-channel 2 refers to y 

-channel 3 refers to z 

-channel 4 refers to F

-32Hz  files are in the Serial Folder

-100Hz files are in the Analog folder

## Python scripts overview

There are 4 main python scripts:

`formatdata.py`
- Includes the classes for collecting, compiling and altering data 
- Has individual attributes for x, y, z, f 
- In the future will just have a single attribute list for x, y, z, f

`rt1hz.py `
- Uses `formatdata.py` 
- Reads through 32hz tdms files and creates 1hz files 

`recordlrt.py `
- Uses `formatdata.py `
- Reads through 32hz tdms files and creates a list of times that had   
  high noise and times of possible interferance 
- Returns a fair number of false positives and could be refined

graph.py 
- Uses `formatdata.py `
- Plots Entire days using the created 1hz files 
- Plots hourly times of those returned by `recordlrt.py`
  
## Manual Usage  

To become accustomed with some of the features built in try running some of the following code:

We can start by importing the files needed and operating on some data. The way this is done may appear a little
awkward with how the date is used, but this program was created to be run automatically. So the date is created
with a variable of days ago
```
from src.formatdata import Date, Data
two_days_ago = Date(1)
data = Data('secNew', two_days_ago, 'LRO', '/home/dcalp/lrt/LRO/RT1Hz/')
data.data[0]
```
This will output the x data stream for LRO from two days ago. Try running the
above for `data.data[0]`, `data.data[1]`, `data.data[2]`.

Now we will continue and do some operations on the data to create new attributes.

```
# Creates 10s running average
data.make_smooth(10)
data.data[0]

# Create rate of change attribute
data.make_rate_change()
data.roc[0]

# Changes data to be in average+-variance
data.make_variance()
data.data[0]
data.avg[0]
```
Consider looking in the source for more options and experimenting.


## Setup
 
 For an explanation on how to set up anaconda read the text file `ANACONDAINSTALL.txt`
 
 To automate these procedures add the following to you `crontab -e` file
 
 ```
 1 1 * * * /home/akovachi/lrt_data/bashFiles/pullfiles.sh &> /home/akovachi/lrt_data/log/filetransfer.log

2 1 * * * /home/akovachi/lrt_data/bashFiles/dataRoutines.sh

20 1 * * * /home/akovachi/lrt_data/bashFiles/sendEmail.sh

0 */3 * * * /home/akovachi/lrt_data/bashFiles/getLrtData.sh

 ```
 
In each of the bash files the absolute directory will have to be changed to the users own name.

As well, a  similar change needs to be made in each of the python scripts about where to find the logging config

```
logging.filename = '[project location]/log/graphing/graphing%s%s.log'%(
        date.m,date.d)
logging.config.fileConfig('[project location]/logging.conf')
```

## SSH Connection

SSH connection needs to be made to a few servers however their IP's will not be listed here. The list of servers used by the programs on default are listed below.

- Sun2 server

- LRE

- LRS

- LRO

