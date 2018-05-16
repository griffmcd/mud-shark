# mud-shark
A client built specifically around the ElectroIndustries Shark 200 and Shark 200S digital energy submeters. It connects to the meters via ModbusTCP, and allows the user to either retrieve log data from one of the meter's several logs, or reprogram one of the three historical logs. Currently it is mostly a command line program, but is being refactored into a graphical application.

Most of the stuff that actually interacts with the meter directly is in "client.py." old-client.py is the standalone program, and client.py is the one that I am refactoring to work with the graphical interface. pop-server.py is a collection of methods for populating my test modbus server with junk data, and can be pretty much ignored.
