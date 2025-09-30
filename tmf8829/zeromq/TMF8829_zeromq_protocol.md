
# Revision History

Revision | Date        | Originator          | Description
---------|-------------|---------------------|---------------------------------------
0-10     | 11-Jun-2024 | Rene Eggerstorfer   | Initial Version
0-20     | 04-Oct-2024 | Monika Arpa         | Singleton pattern implemented for clients (there can only be 1 client that is active)
0-30     | 22-Oct-2024 | Monika Arpa         | Added zeroMQ header definition, FP mode is only in frame header now. 
0-31     | 23-Oct-2024 | Monika Arpa         | More details about publish port data frames
0-40     | 04-Feb-2024 | Rene Eggerstorfer   | Set Preconfig command added

# Introduction

This document describes the protocol for the TMF8829 EVM GUI, the TMF8829 zeromq logger and other possible zeromq clients.

The EVM GUI is a zeromq client (TCP/IP) to one of the servers provided by the TMF8829 software stacks (RaspberryPi, FTDI, Arduino Uno UART STM32H5).

These zeromq servers provide a request/response (REQ/REP) socket on the assigned IP address of the EVM controller board.
Use port 5557 to connect to e.g. 169.254.0.2 for a RaspberryPi controller.

In addition this server publishes measurement data and status information via a zeromq publishing (PUB) socket.
Use port 5558 to connect to e.g. 169.254.0.2 for a RaspberryPi controller.


# Control port (5557) - Request / Response Message Structure

## General structure of a Request

Byte | Name               | Meaning 
-----|--------------------|---------------------------------
0    | Identifier         | 
1:4  | Client ID          | if already assigned, for initial request set it to 0
5..n | Payload (optional) | depending on request different size of payload

## General structure of a Response

Byte | Name               | Value       | Meaning
-----|--------------------|-------------|-------------------------------
0    | Error Code         | 0x00        | Active client, all ok, payload added
0    |                    | 0x01        | Passive client, all ok, payload added
0    |                    | 0xFE        | Unknown request
0    |                    | 0xFF        | Failed
1:4  | Client ID          | <unique-id> | assigned client-id (or same as requested if already had a <>0 client id)
5..m | Payload (optional) |             | depending on response different size of payload

zeromq servers always send responses to requests to avoid blocking the clients.


## List of Requests

Here's the list of valid request identifiers:

 Name of request                                | Identifier 
------------------------------------------------|--------------------
 RESERVED                                       | 0x00
 Identify                                       | 0x01
 Power Device                                   | 0x02
 Leave                                          | 0x03
 Measure                                        | 0x10
 Stop Measurements                              | 0x11
 Get Configuration                              | 0x20
 Set Configuration                              | 0x21
 Get Diagnostics                                | 0x22
 Set Diagnostics                                | 0x23
 Set Preconfiguration                           | 0x24
 Update Target Binaries (Raspberry Pi only)     | 0xA0
 RESERVED                                       | 0xFE
 RESERVED                                       | 0xFF 


## Identify

Identify the EVM controller and the target sensor. **Has to be the first request issued by a client.** 
Command is used to not only request information about the sensor, but also to "register" the client at
the server. Each client gets assigned a unique 4-byte ID. This id has to be provided for all further 
requests to the server. If the client is the first client at the server the server will note down that
only this client can re-configure, start/stop measurements. Reading of configuration is possible for all
clients.

### Request

Byte | Name               | Value       | Meaning 
-----|--------------------|-------------|---------------------------------
0    | Command Identifier | 0x01        |
1:4  | Client ID          | <unique-id> | if already assigned, for initial request set it to 0

### Response

Byte | Name               | Value       | Meaning
-----|--------------------|-------------|-------------------------------
0    | Error Code         | 0x00        | Active client, all ok, payload added
0    |                    | 0x01        | Passive client, all ok, payload added
0    |                    | 0xFF        | Failed, no payload added
1:4  | Client ID          | <unique-id> | assigned client-id (or same as requested if already had a <>0 client id)

### Payload
Offset | Length in Bytes | Field Description
-------|-----------------|-----------------------------------------------------------------------------
   0   |    1            | protocol version
   1   |    1            | host type (0 = undefined, FTDI_BOARD = 1, ARDUINO_BOARD = 2, RASPBERRY_BOARD = 3, EVM_H5_BOARD = 4 )
   2   |    2            | host software version
   4   |    4            | serial number of the ToF chip (little-endian)
   8   |    4            | version number of the firmware application (little endian)
   12  |    64           | info (reserved for future use)


## Power Device

For enabling or disabling the Device the Enable Pin of the TMF8829 is set to high or to low.

### Request

Byte | Name               | Value       | Meaning 
-----|--------------------|-------------|---------------------------------
0    | Command Identifier | 0x02        |
1:4  | Client ID          | <unique-id> | assigned client id
5    | Power on / off     | 0x00        | power off device
5    |                    | 0x01        | power on device

### Response

Byte | Name               | Value       | Meaning
-----|--------------------|-------------|-------------------------------
0    | Error Code         | 0x00        | Active client, all ok, payload added
0    |                    | 0x01        | Passive client, all ok, payload added
1:4  | Client ID          | <unique-id> | assigned client-id
5    | State of power     | 0x00        | device is powered off
5    |                    | 0x01        | device is powered


## Leave

Whenever a client is disconnecting from the server it should issue a leave request. This will allow other clients
to become the active client (if the disconnecting client was the active client).

### Request

Byte | Name               | Value       | Meaning 
-----|--------------------|-------------|---------------------------------
0    | Command Identifier | 0x03        |
1:4  | Client ID          | <unique-id> | assigned client id 

### Response

Byte | Name               | Value       | Meaning
-----|--------------------|-------------|-------------------------------
0    | Error Code         | 0x00        | Active client removed
0    |                    | 0x01        | Passive client removed
1:4  | Client ID          | <unique-id> | previously assigned client id 
5    | Was active client  | 0x00        | client was not the active client
5    |                    | 0x01        | client was the active client



## Measure Command (Measure, Calibration)

Start a measurement if client is the active client. If the client is a passive client, only the status
of the device is checked and returned (whether the device is running measurements or not). A passive
client cannot change the measurement state of a device.

### Request

Byte | Name               | Value       | Meaning 
-----|--------------------|-------------|---------------------------------
0    | Command Identifier | 0x10        |
1:4  | Client ID          | <unique-id> | assigned client id 

### Response

Byte | Name               | Value       | Meaning
-----|--------------------|-------------|-------------------------------
0    | Error Code         | 0x00        | Active client (start executed)
0    |                    | 0x01        | Passive client (start not executed)
1:4  | Client ID          | <unique-id> | assigned client id
5    | measure status     | 0x01        | measurement started (or ongoing - if passive client)
5    |                    | 0x00        | measurement not started (or not ongoing - if passive client)


## Stop Measurements

Stop a measurement if client is the active client. If the client is a passive client, only the status
of the device is checked and returned (whether the device is running measurements or not). A passive
client cannot change the measurement state of a device.

### Request

Byte | Name               | Value       | Meaning 
-----|--------------------|-------------|---------------------------------
0    | Command Identifier | 0x11        |
1:4  | Client ID          | <unique-id> | assigned client id 

### Response

Byte | Name               | Value       | Meaning
-----|--------------------|-------------|-------------------------------
0    | Error Code         | 0x00        | Active client (stop executed)
0    |                    | 0x01        | Passive client (no stop executed)
1:4  | Client ID          | <unique-id> | assigned client id 
5    | measure status     | 0x01        | measurement ongoing (stop could not be done e.g. if passive client)
5    |                    | 0x00        | measurement stopped (or not ongoing - if passive client)


## Get Configuration

Get the configuration parameters of the tmf8829 device. All clients can read a configuration.

### Request

Byte | Name               | Value       | Meaning 
-----|--------------------|-------------|---------------------------------
0    | Command Identifier | 0x20        |
1:4  | Client ID          | <unique-id> | assigned client id 

### Response

Byte | Name               | Value       | Meaning
-----|--------------------|-------------|-------------------------------
0    | Error Code         | 0x00        | Active client 
0    |                    | 0x01        | Passive client 
1:4  | Client ID          | <unique-id> | assigned client id 
5:99 | configuration page |             | the 95 bytes of a complete configuration page


## Set Configuration

Set the configuration parameters of the tmf8829 device. Only active clients can write a configuration

### Request

Byte | Name               | Value       | Meaning 
-----|--------------------|-------------|---------------------------------
0    | Command Identifier | 0x21        |
1:4  | Client ID          | <unique-id> | assigned client id 
5:m  | configuration page |             | the complete <m-5> bytes of a configuration page

### Response

Byte | Name               | Value       | Meaning
-----|--------------------|-------------|-------------------------------
0    | Error Code         | 0x00        | Active client 
0    |                    | 0x01        | Passive client 
1:4  | Client ID          | <unique-id> | assigned client id 
5    | written            | 0x01        | Active client could write the configuration
5    |                    | 0x00        | Passive client cannot write a configuration

## Set Preconfiguration

Send the preconfiguration command to the tmf8829 device.

### Request

Byte | Name               | Value       | Meaning 
-----|--------------------|-------------|---------------------------------
0    | Command Identifier | 0x24        |
1:4  | Client ID          | <unique-id> | assigned client id 
5    | cmd                |             | see application registers, register TMF8829_CMD_STAT commands CMD_LOAD_CFG_8X8 - CMD_LOAD_CFG_48X32_HIGH_ACCURACY

### Response

Byte | Name               | Value       | Meaning
-----|--------------------|-------------|-------------------------------
0    | Error Code         | 0x00        | Active client 
0    |                    | 0x01        | Passive client 
1:4  | Client ID          | <unique-id> | assigned client id 
5    | written            | 0x01        | Active client could write the configuration
5    |                    | 0x00        | Passive client cannot write a configuration


## Update Target Binaries

Update the binaries on the target controller. Only works for the RaspberryPi software stack.

TBD


# Publish port 5558 - Measurement Data And Status Information

The zeromq servers provide measurement data and status information via a separate port - the publishing port (5558). 

## zeroMQ Publish port header  (also called tmf8829ContainerFrameHeader)

Byte | Name               | Value       | Meaning 
-----|--------------------|-------------|---------------------------------
0:3  | magicNumber        | 0xFE5E1234  | identifier to sync on byte stream
4    | protocolVersion    | 2           | current protocol version
5:7  | reserved           |             |
8:11 | payload            |             | size of this frame minus 8 previous bytes
12   | hostType           | 0..4        | ID for type of host FTDI, H5, etc.
13:15| reserved2          |             |
16:19| deviceSerialNumber |             | unique ID of device
20:83| info               |             | 64 bytes info (reserved for future use)


## zeroMQ Publish port payload (=data)

The zeroMQ payload data consists of a series of frames. Each frame has a 16-byte Frame header. The frame header is defined below

### Frame header

Every Data frame has an Frame Header consisting of 16 bytes. The header has the following format:

Byte Number | Content
------------| ----------
 0          | upper nibble (bits[7:4]) is the frame ID, lower nibble (bits[3:0]) is the focal plane mode
 1          | result frames: bit[7] set=full-noise, cleared=averaged-noise, 
 1          |                bit[6] = sub-frame, 
 1          |                bit[5] = xtalk reported,
 1          |                bit[4] = noise reported,
 1          |                bit[3] = signal strength reported,
 1          |                bit[2:0] = number of peaks reported
 1          | histogram frames: bit[7..0] sub-frame number (0..1, or 0..7, or 0..11)
 2:3        | Payload in little endian format (excluding these 2 bytes and 2 previous)
 4:7        | frame number in little endian format
 7:10       | temperature in celsius from the 3 temp sensors on device
 11         | BDV value
 12:13      | optical reference peak from 1st measurement of this frame
 14:15      | optical reference peak from last measurement of this frame

Frame ID | Description
---------|------------
0x10     | Result Frame
0x20     | Histogram Frame
0x30     | Ref Spad Frame

### Frame footer

Every Data frame has an Frame Footer consisting of 12 bytes. The footer has the following format:

Byte Number | Content
------------| ----------
 0:3        | t0Integration is the TMF8829's internal timestamp when t0 integration started 
 4:7        | t1Integration is the TMF8829's internal timestamp when t-last integration started 
 8          | frame status: 
 8          |      bit[0] set == frame is valid, 
 8          |      bit[3] set = HV-CP overload, 
 8          |      bit[4] set = VCDRV overload, 
 8          |      bit[5] set = VCSEL burst limit exceeded
 8          |      bit[7:6] set == frame was aborted, 
 9          | reserved
 10:11      | end-of-frame marker = 0xE0F0


Note that t-last means for:
- 8x8 or 16x16 focal plane mode: the t1 integration
- 32x32 focal plane mode: the t7 integration
- 48x32 focal plane mode: the t11 integration


### Frame data - Result Frames

The published result frame data structure depends on the Focal Plane Mode and the result format.

- for 8x8 and 16x16 mode there is only 1 result frame.
- for 32x32 and 48x32 mode there are 2 result frames. The sub-frame bit shall be used to identify to which half the result belongs.


### Frame data - Reference Spad Result Frames

These frames cannot be read via the FIFO but only at the register addresses 0x20 and following.
The reference SPAD result frame has the same 16-header bytes and 12-footer bytes as all frames.

The ref spad payload is:
- 2x4 32-bit values 

The first 4x 32-bit values are the sum of all hits in the corresponding reference MPs histograms during t0 integration.

The second 4x 32-bit values are the sum of all hits in the corresponding reference MPs histograms during t-last integration.

Note that t-last means for:
- 8x8 or 16x16 focal plane mode: the t1 integration
- 32x32 focal plane mode: the t7 integration
- 48x32 focal plane mode: the t11 integration

### Frame data - Histogram Frames

Histogram Frames have these formats, note that each bin has 24-bits of data (in little endian):

#### 8x8 mode histograms

Data is 24-bits for each bin, there are 2 histogram frames each has:
- 4 reference pixel histograms a 64 bins (reference histograms always have 64 bins)
- 4 columns * 8 rows a 256 bins per macro-pixel

- T0 contains: r[0..3]b[0..63] and x[0..3]|y[0..7]b[0..255],
- T1 contains: r[0..3]b[0..63] and x[4..7]|y[0..7]b[0..255],

#### 16x16 mode histograms

Data is 24-bits for each bin, there are 2 histogram frames each has:
- 4 reference pixel histograms a 64 bins (reference histograms always have 64 bins)
- 8 columns * 16 rows a 64 bins per macro-pixel

- T0 contains: r[0..3]b[0..63] and  x[0..7]|y[0..15]b[0..63],
- T1 contains: r[0..3]b[0..63] and  x[8..15]|y[0..15]b[0..63],

#### 32x32 mode histograms

Data is 24-bits for each bin, there are 8 histogram frames each has:
- 4 reference pixel histograms a 64 bins (reference histograms always have 64 bins)
- 8 columns * 16 rows a 64 bins per macro-pixel

- T0 contains: r[0..3]b[0..63] and  x[0,2,4,6,8,10,12,14]     |y[0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30]b[0..63],
- T1 contains: r[0..3]b[0..63] and  x[16,18,20,22,24,26,28,30]|y[0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30]b[0..63],
- T2 contains: r[0..3]b[0..63] and  x[1,3,5,7,9,11,13,15]     |y[0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30]b[0..63],
- T3 contains: r[0..3]b[0..63] and  x[17,19,21,23,25,27,29,31]|y[0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30]b[0..63],

- T4 contains: r[0..3]b[0..63] and  x[0,2,4,6,8,10,12,14]     |y[1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31]b[0..63],
- T5 contains: r[0..3]b[0..63] and  x[16,18,20,22,24,26,28,30]|y[1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31]b[0..63],
- T6 contains: r[0..3]b[0..63] and  x[1,3,5,7,9,11,13,15]     |y[1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31]b[0..63],
- T7 contains: r[0..3]b[0..63] and  x[17,19,21,23,25,27,29,31]|y[1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31]b[0..63],

#### 48x32 mode histograms

Data is 24-bits for each bin, there are 12 histogram frames each has:
- 4 reference pixel histograms a 64 bins (reference histograms always have 64 bins)
- 8 columns * 16 rows a 64 bins per macro-pixel

- T0 contains: r[0..3]b[0..63] and  x[0,3,6,9,12,15,18,21]     |y[0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30]b[0..63],
- T1 contains: r[0..3]b[0..63] and  x[24,27,30,33,36,39,42,45] |y[0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30]b[0..63],
- T2 contains: r[0..3]b[0..63] and  x[1,4,7,10,13,16,19,22]    |y[0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30]b[0..63],
- T3 contains: r[0..3]b[0..63] and  x[25,28,31,34,37,40,43,46] |y[0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30]b[0..63],
- T4 contains: r[0..3]b[0..63] and  x[2,5,8,11,14,17,20,23]    |y[0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30]b[0..63],
- T5 contains: r[0..3]b[0..63] and  x[26,29,32,35,38,41,44,47] |y[0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30]b[0..63],

- T6 contains: r[0..3]b[0..63] and  x[0,3,6,9,12,15,18,21]     |y[1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31]b[0..63],
- T7 contains: r[0..3]b[0..63] and  x[24,27,30,33,36,39,42,45] |y[1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31]b[0..63],
- T8 contains: r[0..3]b[0..63] and  x[1,4,7,10,13,16,19,22]    |y[1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31]b[0..63],
- T9 contains: r[0..3]b[0..63] and  x[25,28,31,34,37,40,43,46] |y[1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31]b[0..63],
- T10contains: r[0..3]b[0..63] and  x[2,5,8,11,14,17,20,23]    |y[1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31]b[0..63],
- T11contains: r[0..3]b[0..63] and  x[26,29,32,35,38,41,44,47] |y[1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31]b[0..63],
