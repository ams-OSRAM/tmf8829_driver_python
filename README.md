# Python files for the tmf8829 device 

Python version 3.10.11 or high is required.

## Virtual environment

Recommendation is to set-up a virtual environment. Open you favorite Windows PowerShell, VisualStudio Code etc.
To install a virtual environment named env, and use it:   
python -m venv env    
./env/Scripts/Activate.ps1    

## Requirements

To run the scripts in this folder you need to install the packages in the requirements.txt file with:    
pip install -r requirements.txt

All needed python packages are located in the subdirectory packages.

## Folder and sub-folders:

### ./packages
Needed python packages.


### ./tmf8829
All python classes, files and functions, specific to the TMF8829.

##### tmf8829_application.py, tmf8829_application_common.py and tmf8829_bootloader.py:
The application and bootloader classes have the functionality to control the device hardware and the bootloader and also allows to download intel hex files to the device, measurements and the reading of result and histogram frames.

##### tmf8829_application defines.py:
Application specific defines and structures.

##### tmf8829_conv.py:
Contains convenience functions.

#### Python register files

##### tmf8829_host_regs.py 
The registers of the Tmf8829 which could be written over I2C or SPI.

##### tmf8829_application_registers.py:
Application specific registers.

##### tmf8829_config_page.py:
Application configuration register page.

### ./tmf8829/examples
Several examples that show the usage of how to:
- use the application printer to see results/frames in the terminal
- visualize pixel results or histograms 
- log data into a file with json format.

### ./tmf8829/utilities

##### tmf8829_application_printer.py:
The application printer class supports the printing of the results and histogram frames.

##### tmf8829_json_2_csv.py
Convert log files from json format to csv format

##### tmf8829_logger_service.py
Provides functionality to dump the data into a file with json format or to log data into a textfile.


##### tmf8829_visualisation.py
Functionality to visualize pixel data or histograms.

### ./tmf8829/zeromq

zeroMQ is an open source universal messaging library.
zeroMq server implementations for the tmf8829 EVMs are available and for host interaction a zeroMq client.

##### TMF8829_zeromq_protocol.md
The protocol description.

##### tmf8829_host_com_reg.py
The definition of the protocol header.

##### tmf8829_zeromq_common.py
Common functions for the client and server.

##### tmf8829_zeromq_client.py
Client that could be used as active or passive logger

##### tmf8829_zeromq_server_core.py
Common functions for the different server scripts.

##### tmf8829_zeromq_server.py
Server for the EVM shield board.

##### tmf8829_zeromq_server_linux.py
Server for the evm linux board.

##### tmf8829_zeromq_server_arduino.py
Server for the Arduino board.

##### cfg_client.json
TMF8829 configuration for active logging and general logging parameters.

##### cfg_server.json
TMF8829 configuration at startup of the server.