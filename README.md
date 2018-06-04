# MudShark Energy Meter Manager
A client built specifically around the ElectroIndustries Shark 200 and Shark 200S digital energy submeters. It connects to the meters via ModbusTCP, and allows the user to either retrieve log data from one of the meter's several logs, or reprogram one of the three historical logs. There is both a bare-bones implementation that can be used in the python interpreter or in a script, and a graphical interface. 

## Overview

The core functionality of this program (i.e. everything that actually talks to the meter) is located in mudshark_client.py. mudshark_gui.py is the main graphical interface, which utilizes the methods in mudshark_client.py. connectWindow.py, programLogView.py, and retrieveLogView.py are all pyqt widgets used in gui.py. 

## Usage
### GUI wrapper
**NOTE: retrieving and viewing log data via the GUI wrapper has not been implemented yet! Only programming the historical logs is currently supported via the GUI.**
To start the GUI, at the command line enter:
```
python gui.py
```

You will be presented with this view:
![initial view](readme-img/initialview.png "initial view")

Hit Alt+C or use the icon on the toolbar or File->Connect to connect to a meter. This must be done before anything else is possible. Once this occurs, a popup will appear:

![connect popup](readme-img/connectwindow.png "connect window")

Enter the host and port of the meter you wish to communicate with, along with the log you wish to interact with and the desired mode. There are two modes: program log, and retrieve log. Program log only works with the historical logs (1, 2, and 3), and allows you to set which values and at what intervals those values are recorded. Retrieve log mode allows you to poll the meter, retrieve the records stored for that particular log, and view them or export them from the menu.

**NOTE: Retrieve Log is not yet implemented in the GUI wrapper!**

#### Program Log via GUI
When program log is selected and the user clicks "Submit", the program will attempt to connect to the meter on the entered IP and port. If it is a successful connection, the main window's view will change:

![program log](readme-img/programlogview.png "Program Log View")

On the right is a list of meter values you can log. On the left are two dropdown boxes. Interval determines the time interval at which the values selected on the right are recorded to the log. The sector dropdown box allows you to select the number of flash sectors allocated to this log. Each sector is 64kb, minus a sector header of 20 bytes. 15 sectors are available for allocation between all three historical logs. The sum of all sectors used by the three historical logs may be less than 15, but it cannot be greater. If the value is 0, that means that the log will be DISABLED.

#### Retrieve Log via GUI
**Retrieving the log via the GUI has not been implemented yet!**

### Bare-Bones Implementation

To get started using MudShark in a python script, first import the client, and define the host and port of the meter. Then call the connect() method with the host and port. The connect method returns the ModbusTCP client, so be sure to assign it to something. **(Note: Connect raises an Exception if the connection was not successful)**:

```python
from mudshark_client import *

host = "0.0.0.0"
port = 502

client = connect(host, port)
```

#### Programming a Log
To program the log, first you have to get the log number of the log you want to program. The client has a dictionary **logs** that will return the appropriate log number for the log name key:

```python
logs = {'System': 0,
        'Alarm': 1,
        'Hist. Log 1': 2,
        'Hist. Log 2': 3,
        'Hist. Log 3': 4,
        'I/O Changes': 5}
```

Only the Historical Logs 1, 2, and 3 are programmable (which confusingly have log numbers 2, 3, and 4).  There is also a method get_hist_log_num() that takes a number 1,2, or 3 and returns the correct log number, in case you don't want to keep track (although you can just add 1 to it). 

```python
log_num = get_hist_log_num(1)
```

We also have to get the interval at which we want the log to record the values. It supports logging at 1, 3, 5, 10, 15, 30, and 60 minute intervals, and another option for End Of Interval Pulse. The client has a method get_interval() that takes a number and returns the interval closest to it, rounding down. So if its less than 3, it will return the code for 1 minute, less than 5 returns the code for 3 minutes, etc. 60 and above defaults to 60 minutes, and 0 is the End of Interval Pulse.

```python
interval = get_interval(15)  # returns the hex code for 15 minutes
```

**OPTIONAL** You can also set the number of sectors (0-15), or leave it blank to default to 5. There are 15 flash sectors divided among all three of the historical logs. Setting the sectors to 0 will disable the log.

The only other thing left to configure before we program the log is the registers the meter will record in that log. There are numerous values, and some values occupy a single register, while others occupy more than one. The program_log function takes a list of register addresses. If a value uses more than one register, both register addresses must be added to the list. 

mudshark_client.py contains a list of all the measured values:

```python
values = ["Volts A-N",
          "Volts B-N",
          "Volts C-N",
          "Amps A",
          "Amps B",
          "Amps C",
          "Watts 3-Ph Total",
          "VARs 3-Ph Total",
          "VAs 3-Ph Total",
          "Power Factor 3-Ph total",
          "Frequency",
          "Neutral Current",
          "W-Hours Received",
          "W-Hours Delivered",
          "W-Hours Net",
          "VAR-hours Net",
          "VAR-hours Total",
          "VA-hours Total",
          "Amps A Average",
          "Amps B Average",
          "Amps C Average",
          "Watts 3-Ph Average",
          "VARs 3-Ph Average",
          "VAs 3-Ph Average",
          "Neutral Current Average",
          "W-Hours Total"]
```

and a dictionary that contains the registers associated with those values:

```python
registers = {"Volts A-N": [0x116],
             "Volts B-N": [0x117],
             "Volts C-N": [0x118],
             "Amps A": [0x11c],
             "Amps B": [0x3F3, 0x3f4],
             "Amps C": [0x03f7, 0x03f8],
             "Watts 3-Ph Total": [0x03f9, 0x03fa],
             "VARs 3-Ph Total": [0x03fb, 0x03fc],
             "VAs 3-Ph Total": [0x03fd, 0x03fe],
             "Power Factor 3-Ph total": [0x03ff, 0x0400],
             "Frequency": [0x0401, 0x0402],
             "Neutral Current": [0x0403, 0x0404],
             "W-Hours Received": [0x05db, 0x05dc],
             "W-Hours Delivered": [0x05dd, 0x05de],
             "W-Hours Net": [0x05df, 0x05e0],
             "VAR-hours Net": [0x05e7, 0x05e8],
             "VAR-hours Total": [0x05e9, 0x05ea],
             "VA-hours Total": [0x05eb, 0x05ec],
             "Amps A Average": [0x07cf, 0x07ce],
             "Amps B Average": [0x07d1, 0x07d2],
             "Amps C Average": [0x07d3, 0x07d4],
             "Watts 3-Ph Average": [0x07d5, 0x07d6],
             "VARs 3-Ph Average": [0x07d7, 0x07d8],
             "VAs 3-Ph Average": [0x07dd, 0x07de],
             "Neutral Current Average": [0x07e3, 0x07e4],
             "W-Hours Total": [0x0bdd, 0x0bde]}
```

The key is to look in the values list, get the keys you want, and then look up the associated list of register(s) in the registers dictionary. For example, if you wanted to log "W-Hours Total" and "Amps C Average":

```python
my_values = ["W-Hours Total", "Amps C Average"]
my_registers = []
for val in my_values:
    my_registers.append(registers.get(val))
```

Now that we have all the requisite fields, we are free to program the log with the program_log method, like so:

```python
program_log(client, log_num, my_registers, interval, sectors)  # remember, sectors is optional
```

And you've successfully programmed the log! The full script:

```python
from mudshark_client import *

host = "0.0.0.0"
port = 502

client = connect(host, port)
log_num = get_hist_log_num(1)
# Or, get the log num by its string name:
# log_num = logs.get('Hist. Log 1')
interval = get_interval(15)
my_values = ["W-Hours Total", "Amps C Average"]
my_registers = []
for val in my_values:
    my_registers.append(registers.get(val))

program_log(client, log_num, my_registers, interval)
```

#### Retrieving a Log
The easiest way to retrieve records from a log is the get_log() method, which takes the client and a log_number, and returns a list of the records.

```python
from mudshark_client import *
host = "0.0.0.0"
port = 502

client = connect(host, port)
log_num = 2  # historical log 1

records = get_log(client, log_num)
```

However, this will not give you access to some information about the log itself that may be important, depending on what you are doing. Luckily, doing what this function does manually is not terribly difficult either.

There are three steps involved in retrieving log data from the Shark 200 meters:
1. Engage the Log
2. Retrieve the Records
3. Disengage the Log

the method to engage the log is engage_log(). It takes as parameters the client, the log number of the log to engage, and an option flag indicating the type of log to retrieve. There are three log types: 0 is a normal record, 1 is timestamp only, and 2 is a complete memory image. If this is not given, it defaults to 0. engage_log returns a namedtuple that contains the log's name, number, status, record size, records per window, and the total number of records in the log.

So the first step is to get our log number. A dictionary containing the logs and their respective numbers are included:

```
logs = {'System': 0,
        'Alarm': 1,
        'Hist. Log 1': 2,
        'Hist. Log 2': 3,
        'Hist. Log 3': 4,
        'I/O Changes': 5}
```

Unlike programming the log, we can retrieve from any of the 6 logs on the device. So to engage the log, we write:

```python
from mudshark_client import *

host = "0.0.0.0"
port = 502

client = connect(host, port)
log_num = 2  # historical log 1

log_status_info = engage_log(client, log_num)  # left off the optional log type, so it defaults to 0
```

Next, we must retrieve the records. This is done with the retrieve_records method. This takes the client, the records per window, the total number of records, and the size of each record as parameters. It returns a list containing all the records. The log_status_info named tuple above contains all the info we need to retrieve the records:

```python
recs_per_window = log_status_info.records_per_window
total_records = log_status_info.max_records
record_size = log_status_info.record_size

records = retrieve_records(client, recs_per_window, total_records, record_size)
```

Now that we have retrieved our records, we can disengage the log. We do this with the disengage_log method. All we have to do is provide it the client and the log number of the log we connected to, and it handles the rest:

```python
disengage_log(client, log_num)
```

And you've successfully retrieved the records and disengaged the log. You are now free to use the records however you please, be that export them to another format, or do your own modeling of the data!

Full script:

```python
from mudshark_client import *

host = "0.0.0.0"
port = 502

client = connect(host, port)
log_num = 2  # historical log 1

log_status_info = engage_log(client, log_num)

recs_per_window = log_status_info.records_per_window
total_records = log_status_info.max_records
record_size = log_status_info.record_size

records = retrieve_records(client, recs_per_window, total_records, record_size)

disengage_log(client, log_num)
```