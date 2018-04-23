# Installation
On a linux server navigate to the home directory

From this github repository click `Clone or download` then click on `Use SSH` copy the link

Now in the terminal type `$ git clone [Copied directory]`

Upon proper installation the file structure should appear as the following 
```
lrt_data
|-- anaconda3
|-- lrt_data
|   |-- ottSecData (D)
|   |-- lrtRecords (D)
|   |-- logging.conf
|   |-- option.conf
|   |
|   |-- src
|   |   |-- checkFiles.py
|   |   |-- formatdata.py
|   |   |-- rt1hz.py
|   |   `-- graph.py
|   |
|   |-- bashfiles
|   |   |-- pulfiles.sh
|   |   `-- sendEmail.sh
|   | 
|   |-- plots
|   |   |-- LRE (D)
|   |   |-- LRO (D)
|   |   `-- LRS (D)
|   |  
|   |-- logFiles
|   |   |-- record (D)
|   |   |-- graphing (D)
|   |   |-- filestransfer (D)
|   |   `-- checkfiles (D)
```

## Anaconda installation

1. Go to https://repo.continuum.io/
    - This is the anaconda home page

2. On the page find and click on `View All Installers`

3. Select and download `Anaconda-5.0.1-Linux-x86_64.sh`
    - There may be newer versions and they may work
    - The linux server may not support a newer version at
                some point in time

4. Using shell (or any other secure file transfer) move the .sh 
    file to your home directory. In the ssh terminal type:
    `bash Anaconda-5.0.1-Linux-x86_64.sh`
    - Or the extension of the version you installed

5. Select yes to the default options. This will create the `anaconda3` file in your
   home directory.

6. Wait for the installation to complete and close the terminal

7. Reopen the terminal and type `python`
   -You should see something similar to:
```
bash-4.2$ python
Python 3.6.3 |Anaconda, Inc.| (default, DATE,TIME)
```
   -type `quit()` to leave this process

8. If you did not see Anaconda, Inc. and instead saw that was
   missing or perhaps python you have a few more steps to follow.

9. Locate and open your `.bash_profile`file

10. Near the end of the file you should see a line which says
       `export PATH`. Edit this line so that it is:
       ``` PATH="/home/YOURFILE/anaconda3/bin:$PATH"```

11. Save the file and exit. 

12. Try step (7.) again

8-12. EXPLAINED:
Essentially the installation of anaconda is supposed to add
this line to your profile on its own, and it does on some
linux servers. It does not on this one and thus we have to
do it manually.
        
## NPTDMS installation

1. Navigate to:
    https://github.com/adamreeve/npTDMS

2. Download the zip file which should show up as: `npTDMS-master.zip`

2.b. Unzip the file 

3. Move the unziped file to you `/home/YOURFILE` directory

4. Navigate into the `npTDMS-master` folder and type:
    `python setup.py install`

# Background

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

`graph.py  `
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
two_days_ago = Date(2)
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
 1 1 * * * [Home]/lrt_data/bashFiles/pullfiles.sh &> /home/akovachi/lrt_data/log/filetransfer.log

2 1 * * * [Home]/lrt_data/bashFiles/dataRoutines.sh

20 1 * * * [Home]/lrt_data/bashFiles/sendEmail.sh

0 */3 * * * [Home]/lrt_data/bashFiles/getLrtData.sh

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

