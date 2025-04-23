[TOC]

# Scodeno Smart Distribution Box Docking Agreement

The management platform deploys an MQTT server, where the smart box and the management platform interact through the MQTT subscription protocol to meet the management needs of the distribution box.

## Version Change Log

Revision No. | Description | Date
-- | -- | --
v1.0.0 | |
v1.1.0 | Merged remote configuration interface | 2022-12-01
v1.1.1 | Modified upgrade interface | 2023-01-01
v1.2.0 | Added serial port (battery and electricity meter) status reporting | 2023-01-05
v1.2.1 | Added box door photo status reporting on backplane | 2023-01-05
v1.2.2 | Improved box door photo status reporting on backplane | 2023-01-11
v1.3.0 | Reorganized format and added upgrade command response | 2023-02-13
v1.3.1 | Added pole number reporting and modification; Added device name modification | 2023-06-09
v1.3.2 | Deleted alarm ID | 2023-06-25
v1.3.3 | Fixed error in data reporting response format description | 2023-07-29
v1.4.0 | Added reporting interfaces: port traffic, switch MAC address, device binding list<br>Added command interfaces: get PSE status, set PSE switch, delete device binding | 2023-08-05
v1.4.1 | Added reporting interface: netdmate-wifiap-config | 2023-08-07 |
v1.4.2 | Added smart lock interface | 2023-08-14 |
v1.4.3 | Fixed alarm report format error <br> Removed specific alarm summary descriptions | 2023-08-15 |
v1.4.4 | Modified smart lock interface reporting subtopics and deleted redundant PSE switch setting | 2023-08-18 |
v1.4.5 | Fixed incorrect response field names for IO collection module heatConfig.get method | 2023-09-20 |
v1.4.6 | Added field "controlType" in data reporting for backboard-info topic | 2023-09-20 |
v1.4.7 | Added field description for netdmate-mobile-gps topic in data reporting | 2023-09-20 |
v1.4.8 | Added "uuid" field for unique device identifier in devicebind-list topic in data reporting | 2023-09-21 |
v1.4.9 | Added V1/backboard-state topic interface in data reporting | 2023-09-21 |
v1.4.10 | Added state device status, type device type, and command to add device binding in devicebind-list topic reporting | 2024-01-31 |
v1.4.11 | Added onvifconfig interface | 2024-03-22 |
v1.4.12 | Modified device binding interface | 2024-04-15 |
v1.4.13 | Changed scheduled reporting interface to status change reporting | 2024-08-05 |
2023-08-05

Version number explanation:
Increased functional modules change the second digit;
Increased/deleted/modified interfaces or corrected errors change the third digit;


## 1. Protocol Introduction
The standard docking protocol is based on the MQTT protocol and establishes data communication standards for the exchange of business data between the device side and the IoT platform.
Supports MQTT 3.1, MQTT 3.1.1 protocols, with data transmission format in JSON and UTF-8 string encoding.

## 2. Identity Authentication
The management platform must provide an identity authentication mechanism.
Devices can be identified using MAC addresses or the MQTT server's username and password.

Devices are only allowed to use the topic: sys/service/${deviceId}/#

## 3. Interaction Process

To clarify the interaction process between the device and the server, the following sequence diagram omits the details of the device publishing messages to MQTT, and MQTT forwarding device messages to the server.

```sequence 

participant DEV
participant SERVER
participant MQTT

SERVER->MQTT: login (subscribe sys/device/*)
DEV->MQTT: login (subscribe sys/service/${deviceId}/*)

DEV->SERVER: publish connect message 
SERVER->DEV: query device information and decide whether to allow connection 

Note right of DEV: If the server opts to use ECDH security, ECDH key negotiation is required

DEV->SERVER: publish ecdh_key message
SERVER->DEV: return ecdh_key_reply  

SERVER->DEV: issue command
DEV->SERVER: command response
 

Note right of DEV: Connection successful

```

Process description:
1. The server starts the MQTT server, connects to the MQTT server, and subscribes to all device connection requests.
2. The device logs in to the MQTT server.
3. The device publishes a connection request (connect), and the server queries the device information and decides whether to allow the device to connect,<br> then returns the connect_reply response.
4. If the device is allowed to connect, and ECDH key negotiation is chosen, the device starts the key negotiation with the server (ecdh_key) // negotiation can be omitted.

5. The device successfully connects and starts issuing commands to obtain the box's information and status (report).
6. When an alarm occurs, the device actively publishes alarm information (alarm) and reports the configuration status change when the box web operation is initiated.


## 4. Protocol Content

| Function Name | Type | Topic | Description |
| -- | -- | -- | -- |
| Connection Request | Device publishes | sys/device/${deviceId}/connect | Device initiates connection |
| Connection Response | Device subscribes | sys/service/${deviceId}/connect_reply | Server's response to device connection  |
| ECDH Key Negotiation | Device publishes | sys/device/${deviceId}/ecdh_key | None |
| ECDH Key Negotiation Response | Device subscribes | sys/service/${deviceId}/ecdh_key_reply | None |
| PROFILE Report | Device publishes | sys/device/${deviceId}/profile | None |
| PROFILE Response | Device subscribes | sys/service/${deviceId}/profile_reply | None |
| Data Reporting |  Device publishes | sys/device/${deviceId}/report/{subtopic} |  Issue commands, device reports data once  |
| Data Reporting |  Device publishes | sys/device/${deviceId}/report/configuration/{subtopic} |  Device configuration change data reporting  |
| Data Reporting Response |  Device subscribes | sys/service/${deviceId}/report_reply | Return data reporting processing result  |
| Alarm Report |  Device publishes | sys/device/${deviceId}/alarm | Device actively reports alarm event |
| Will Message |  Device publishes | sys/device/${deviceId}/will | Device unexpected offline event, default 30s heartbeat time t0, 1.5*t0 judged offline |
| Will Message |  Device subscribes | sys/service/equipment_management_platform/will | Platform unexpected offline event, device subscribes to platform will message, when the device receives the platform will message, it switches to request connection state|
| Command Reception | Device subscribes | sys/service/{deviceId}/command | Platform issues command |
| Command Execution Return | Device publishes | sys/device/{deviceId}/command_reply/{subtopic} | |

> Note: In the topic, deviceId is temporarily set as "device type_MAC address",
> Current device types:
> smartBox  // Smart box
> miniGW    // Mini gateway

## 5. Device Connection


*Connection Request*

```json
{
    "type" : "connect",
    "version": 1,
    "session" : "xxxxxxxxxxxxxxxxxxxxxx", // Session is a randomly generated code, the server must return the same session in its response
    "deviceId" : "xxxxxxxxxxxx",  
    "time" : 1234567890,
    // Request data to send
    "data" : {
        "securityMode" : ["ecdh", "static", "none"] // Supported key acquisition methods by the device
    }
}
```

*Connection Response*

```json
{
    "type" : "connect_reply",
    "version": 1,
    "session" : "xxxxxxxxxxxxxxxxxxxxxx",  // Same session as the box's connection request
    "deviceId" : "xxxxxxxxxxxx",// Same deviceId as the box's connection request
    "time" : 1234567890,// Same time as the box's connection request
    "response": {
        "code": 0,
        "message" : "success"
    },
    // Return connection data
    "data" : {
        "security" : "none", // Specify key mode
    }
}
```

## 6. Key Negotiation

If the server opts to use the ECDH key negotiation mechanism, this process needs to be executed to generate a shared key.

*ECDH Key Negotiation*

```json
{
    "type" : "ecdh_key",
    "version": 1,
    "session" : "xxxxxxxxxxxxxxxxxxxxxx",
    "deviceId" : "xxxxxxxxxxxx",
    "time" : 1234567890,
    // Request data to send
    "data" : {
        "ecdhKey" : "xxxxxxx" // Base64 encoded publish key
    }
}
```

*ECDH Key Negotiation Response*

```json
{
    "type" : "ecdh_key_reply",
    "version": 1,
    "session" : "xxxxxxxxxxxxxxxxxxxxxx",
    "deviceId" : "xxxxxxxxxxxx",
    "time" : 1234567890,
    "response": {
        "code": 0,
        "message" : "success"
    },
    // Return connection data
    "data" : {
        "ecdhKey" : "xxxxxxxx",  // Base64 encoded publish key
    }
}
```

## 7. PROFILE Reporting

## 8. Issue Configuration Status Change Reporting
*Data Reporting*

```json
{
    "type" : "report",
    "version": 1,
    "session" : "xxxxxxxxxxxxxxxxxxxxxx",
    "deviceId" : "xxxxxxxxxxxx",
    "time" : 1234567890,
    "data" : {}  // Specific data to be reported, refer to the table below
}
```

*Data Reporting Response*    // Response is optional

```json
{
    "type" : "report_reply",
    "version": 1,
    "session" : "xxxxxxxxxxxxxxxxxxxxxx",
    "deviceId" : "xxxxxxxxxxxx",
    "time" : 1234567890,
    "response": {
        "code": 0,
        "message" : "success"
    },
}
```

### 8.1 System Configuration
configuration/system/manageSet

Data Definition:
| Data | Type | Constraint |
| -- | -- | -- |
| Username | char | |
| Password | char | |

Modify Username and Password
```j
    {
        "adminUsername": "root",
        "adminPassword": "root"
    }
```
configuration/system/timeSet
Data Definition:
| Description | Data | Type | Constraint |
| -- | -- | -- | -- |
| Time Acquisition Method | timeEnable | string | "broker1" - Platform 1</br>"broker2" - Platform 2 // When setting the platform, it must match timeZoneEn on the same platform</br>"ntp" - NTP server</br>"manual" - manual setting</br> |
| NTP Server | ntpServers | string | |
| Time Zone Acquisition Method | timeZoneEn | string | "broker1" - Platform 1</br>"broker2" - Platform 2</br>"manual" - manual setting</br> |
| Time Zone | timeZone | string | |

Time Settings
```j
    {
        "timeZone": "America/New_York",
        "ntpServers": "ntp2.aliyun.com",
        "timeZoneEn": "manual",
        "timeEnable": "broker1"
    }
```
configuration/system/customizationSet
Pole Number Setting
```j
{
    "poleNumber": "hello" // Pole number
}
```
configuration/system/settingSet
Device Name Modification
```j
{
   "deviceName":"ZK618T-485338-485338"
}
```
### 8.2 Network Configuration
configuration/netdmate/manageSet
| Data | Type | Constraint |
| -- | -- | -- |
| Management Status | | |
| Local Management IP Address | | Default 192.168.1.249 |
| Local Management IP Subnet Mask | | Default 255.255.255.0 |
| DHCP Server Management | | Default 255.255.255.0 |
| DHCP Start IP | | Default 255.255.255.0 |
| DHCP End IP | | Default 255.255.255.0 |
| DHCP Lease Period | | Default 255.255.255.0 |

Management Interface Configuration
```j
    {
        "enabled": 1,
        "ip": "192.168.1.249",
        "netmask": "255.255.255.0",
        "dhcpdEnabled": 0,
        "dhcpdLeaseBegin": "192.168.1.100",
        "dhcpdLeaseEnd": "192.168.1.200",
        "dhcpdLeasePeriod": 12
    }
```
configuration/netdmate/ethernetSet
| Data | Type | Constraint |
| -- | -- | -- |
| Interface Name | | |
| Management Status | | Fixed as enabled, no setting available |
| DHCP Management Status | | Whether to enable DHCP client for the interface |
| VLAN | | |
| IPV4 Address | | |
| IPV4 Subnet Mask | | |
| IPV4 Gateway | | |
| IPV4 DNS1 | | |
| IPV4 DNS2 | | |

Ethernet Interface Configuration
```j
    {
        "name": "sw1",
        "enabled": 1,
        "dhcpEnabled": 0,
        "vlan": 1,
        "ipAddr": "192.168.3.1",
        "nmAddr": "255.255.255.0",
        "gwAddr": "0.0.0.0",
        "dns1Addr": "0.0.0.0",
        "dns2Addr": "0.0.0.0"
    }
```
configuration/netdmate/mobileSet
Data Definition:
| Data | Type | Constraint |
| -- | -- | -- |
| Data Management Status | | Whether to start the data connection |
| Custom APN | | Default false |
| APN Name | | |
| APN Username | | |
| APN Password | | |
| Enable GPS | | |

LTE Interface Configuration
```j
    {
        "name":"lte1",
        "dataEnabled": 1, 
        "customApn": 1, 
        "apnName": "897n", 
        "apnUsername": "9986", 
        "apnPassword": "9986",
        "gpsEnabled": 1
    }
```
configuration/netdmate/mobileGpsSet
```j
{
    "latitude" : 1.000000, //double Latitude
    "latitude_h": "N", //string Latitude Hemisphere    "N"/"S" // North or South Latitude
    "longitude": 1.000000, //double Longitude
    "longitude_h": "E", // string Longitude Hemisphere   "E"/"W" // East or West Longitude
    "altitude": 1.000000, // double Altitude
    "altitude_u": "M" // string Altitude Unit   "M" // Altitude unit in meters
}
```
configuration/netdmate/wifiapSet
Data Definition:
| Data | Description | Type | Constraint | Required/Optional |
| - | - | - | - | - |
| name | Name | string |  | Required |
| enabled | Switch | int |  | Required |
| channel | Channel | int |  | Required |
| ssid | Wi-Fi Name | string |  | Required |
| password | Password | string |  | Required |

Wi-Fi Interface Configuration
```j
    {
        "name":"wifi1",
        "enabled": 1, 
        "channel": 1, 
        "ssid": "897n", 
        "password": "9986"
    }
```
### 8.3 Alarm Configuration
configuration/alarmhub/configSet
Data Definition:
| Data | Type | Constraint |
| -- | -- | -- |
| Alarm Delay Time | int | Unit in seconds |
| Buzzer Switch | bool | true - On |

Alarm Configuration
```j
    {
        "timeout": 5,
        "buzzerEnable": true
    } 
```
### 8.4 PSE Configuration

configuration/switchPse/stateSet
Table 9-2: Data Type Description for Issuance
| Data | Secondary Data | Type | Constraint |
| -- | -- | -- | -- |
| Port Number | port | int | 1~Maximum number of ports |
| PSE On/Off Status | pseState | bool | true/false: On/Off |

PSE Switch Configuration
```j
    { 
        "port": 1, 
        "pseState": true 
    }
```
### 8.5 Device Binding Configuration
configuration/devicebind/add
Add Bound Device
```j
{
"name": "camera",
"switchPort": "NONE", // Switch board position
"location": 4,  // Power board position
"channel": 2,  // Power board hole number
"binded": true,    // Whether bound
"ip": "192.168.5.59",     // Device IP 
"uuid": "5201458a-c38d-465d-a53b-75f8d2184df0",  // Device Unique Identifier 
"type": "NONE",    // Type     Can only be "switch", "camera", "other"
"state": false,    // Online/Offline
"account": "NONE",  // Account
"password": "NONE"   // Password
}
```
configuration/devicebind/del
Delete Bound Device
```j
{
"name": "camera",
"switchPort": "NONE",
"location": 4,
"channel": 2,
"binded": true,
"ip": "192.168.5.59",
"uuid": "5201458a-c38d-465d-a53b-75f8d2184df0",  // Device Unique Identifier
"type": "NONE",
"state": false,
"account": "NONE",
"password": "NONE"
}
```

### 8.6 Switch Configuration
configuration/switchVlan/vlanAction 
VLAN Operation
```j
{
action: "remove"       //  add - Add, remove - Delete
vlans: "3,4,5,6,7,8"    // VLAN numbers
}
```
configuration/switchVlan/portSet
Port Settings
```j
{ 
    num:1                       // Number of ports
    ports: [
        {
            id: 1                       // Port ID
            mode: "access"              // trunk or access mode
            name: "port1"               // Port name
            pvid: 4                     // VLAN number
            tagged: ""                  // Tagged, available only for trunk mode
            trunkWithAll: false         // Whether can access all VLANs
            untagged: "4"
        }
    ]

}
```
configuration/switchVlan/vlanMgntSet 
Set Management VLAN (where to set the CPU in which VLAN group)
```j
{
"vlan":2                  // VLAN number
}
```
configuration/switchPort/configSet
Add Configuration
```j
{
adminStatus: false        
ethMode: "10H"
fiberMode: "Auto"
flowControl: false
id: 1
mtu: 10240
name: "port1"
portAlias: "jk"
}
```
configuration/switchPort/statisticsReset
Add Configuration
```j
{
      "statistics.reset":true   // true - Reset statistics
}
```
configuration/switchPlldp/globalSet
PLLD Global Settings
```j
{
"adminStatus": false,   // Whether to enable PLLDP
"txPeriod": 5           // Transmission period
}
```
configuration/switchPlldp/protsSet
Port Settings
```j
{
        "num": 4,       // Number of ports to set
        "enabledPorts": [   // Specific port settings
                {
                        "portId": 1,    // Port ID
                        "enable": true  // Whether to enable PLLDP
                },
                {
                        "portId": 2,
                        "enable": true
                },
                {
                        "portId": 7,
                        "enable": false
                },
                {
                        "portId": 8,
                        "enable": false
                }
        ]
}
// num defines the number of ports
```
configuration/switchWhitelist/globalSet
Whitelist Global Settings
```j
{
adminStatus: true   // Whether to enable whitelist
enabledPorts: [{"port":1},{"port":2},{"port":3},{"port":4},{"port":5},{"port":6}]    // Ports enabled for whitelist
}
```
configuration/switchWhitelist/action
Whitelist Operation
```j
{
action: "add",       // add - Add, remove - Delete
num: 1,              // Number of items to operate
items: [
{
port: 1,             // Port ID
  mac: "00163e-4a7b9f", // MAC address
  alias: "p1"           // Alias
}
]
}
```

### 8.7 Serial Port Configuration
Table 6-1-1: Serial Port Data Definition
| Data | Secondary Data | Type | Constraint |
| -- | -- | -- | -- |
| Serial Port Configuration Options | serialNum | int | Pass-through serial port number, only 0 and 1 (**no need to display in the web**) |
|  | function | char | "battery": Battery, other parameters can be omitted; </br>"serialNet": Pass-through </br>"powerMeter": Electricity Meter^Note 1^</br>"airConditioner": Air Conditioner |
|  | csType | char | Client \| Server |
|  | protocol | char | TCP \| UDP |
|  | remoteIp | char | Remote IP |
|  | localPort | int | Local port (1~65535) |
|  | remotePort | int | Remote port (1~65535) |
|  | reconnectTime | int | Reconnection time (1~99999) |
|  | serialBaud | char | Baud rate |
|  | serialSize | int | Data bits: 7 \| 8 |
|  | serialParity | char | Parity method: n \| o \| e |
|  | serialStop | char | Stop bits: 1 \| 2 |
|  | serialFlowControl | char | Flow control: NONE |
|  | powerMeterAddr | int | Electricity meter address: 1~247 |
|  | powerMeterBaudrate | int | Electricity meter baud rate: 1200 \| 2400 \| 4800 \| 9600 |

Note 1: For electricity meter functionality, only the following four parameters need to be configured:
serialNum, function, powerMeterAddr, powerMeterBaudrate

**Explanation**

> 1. Baud rate  
Available baud rates:
['200', '300', '600', '1200', '1800', '2400', '4800', '9600', '19200', '38400', '57600', '115200', '230400', '460800', '500000', '576000']  
<font color=red> Note: The baud rates above may change later. </font>

> 2. Flow control  
Currently, only NONE flow control is available.

> 3. csType/protocol/remoteIp/localPort/remotePort/reconnectTime  
In different modes, not all parameters can be configured. Please refer to Table 6-1-2 for details.

Table 6-1-2: <font color=red>Serial Port Parameter Dependencies</font>
| protocol | csType | remoteIp | localPort | remotePort | reconnectTime |
| --- | -- | -- | -- | -- | -- |
| TCP | Client | Valid | Invalid | Valid | Valid |
| TCP | Server | Invalid | Valid | Invalid | Invalid |
| UDP | Invalid | Valid | Valid | Valid | Invalid |

**Explanation:** "Invalid" means no user-configurable interface is provided. It is recommended to send data bits as 0 or NULL.
configuration/serial/serialConfigSet
Add Configuration
```j
{ 
        "serialNum": 0,
        "function": "serialNet",
        "csType": "Server",
        "protocol": "TCP",
        "remoteIp": "192.168.1.102",
        "localPort": 4000,
        "remotePort": 5000,
        "reconnectTime": 5,
        "serialBaud": "115200",
        "serialSize": 8,
        "serialParity": "n",
        "serialStop": "1",
        "serialFlowControl": "NONE",
        "powerMeterAddr": 1,
        "powerMeterBaudrate": 4800
}
```
configuration/serial/airConditionerSettimesection
Set Air Conditioner Automatic Operation Time Period
```j
{       
        "serialNum":0 ,
        "timeSections":
 // Three time periods can be set
        [
            {
                "enable": false, 
// Whether the time period is active, false - inactive, true - active
                "times": "01:02-03:04"
 // Time period format: hh:mm-hh:mm, it is recommended to select from a box instead of typing
            },
            {
                "enable": false,
                "times": "05:06-07:08"
            },
            {
                "enable": false,
                "times": "09:10-11:12"
            }
        ]
    }

```

configuration/serial/airConditionerSetcoldertemp
Set Air Conditioner Auto Turn-On/Turn-Off Temperature
```j
 {      
        "serialNum":1,
        "tempColdOn": 40, 
// Cooling turn-on temperature, valid range: 20~55
        "tempColdOff": 30
// Cooling turn-off temperature, valid range: 15~35
}
```

configuration/serial/airConditionerSetcoldertemp
Set Air Conditioner Operation Mode
```j
{          
        "serialNum",1
        "airRunMode": "Auto" 
// Auto - Automatic, OFF - Off
  }
```
configuration/serial/smartLockOpen
Open Smart Lock
```j
{       
        "serialNum":1,
        "lockstate": 1 // 0 Open, 1 Close
  }
```

configuration/serial/smartLockDelslot
Delete Smart Lock ID Card
```j
{   
    "serialNum":1,
	"idDecimal": "NONE",
	"name": "NONE"
}
```

configuration/serial/smartLockAddid
Add Smart Lock ID
```j
{   
    "serialNum":1,
	"idDecimal": "NONE",
	"name": "NONE"
}
```
configuration/serial/smartLockAddLastAdmin
Add the last scanned ID card to be the admin card for Smart Lock
```j
{   
    "serialNum":1,
	"idDecimal": "NONE",
	"name": "NONE"
}
```
configuration/serial/smartLockAddLastCard
Add the last scanned ID card to be the work card for Smart Lock
```j
{   
    "serialNum":1,
	"idDecimal": "NONE",
	"name": "NONE"
}
```

configuration/serial/smartLockLockLogClean
Delete the Record of Unlocking the Smart Lock
```j
{   
    "lockLogClean":true
}
```
### 8.8 Power Board Configuration
<font color=blue> Both opening and closing of power board channels trigger alarms </font>

### 8.9 I/O Board Configuration
configuration/ioboard/settingSet
Fan Automatic Settings
```j
{
        "autoControl": true,
        "tempThresholdOn": 40,
        "tempThresholdOff": 35,
        "fanNum": 2
}
```

configuration/ioboard/fansettingSet
Fan Manual Settings
```j
[
       "fan": [
            {
                 "id": 1,
                 "fanSwitch": true,
                 "speed": 2000
            },
            {
                 "id": 2,
                 "fanSwitch": true,
                 "speed": 2000
            }
   ]
]
```

configuration/ioboard/heatConfigSet
Heating Settings
```j
[
        "heatAuto": true,
        "heatTempOn": -20,
        "heatTempOff": -10,
        "heatingNum": 1,
        "heating": [
                {
                        "id": 1,
                        "htSwitch": true
                }
        ]
]
```
## 8. One-Time Data Reporting
After issuing the command for one-time data reporting, data will be reported under the sys/device/${deviceId}/report/{subtopic} topic.
*Command Reception*

```json
{
    "type" : "command",
    "version": 1,
    "session" : "xxxxxxxxxxxxxxxxxxxxxx",
    "deviceId" : "xxxxxxxxxxxx",
    "time" : 1234567890,
    "data" : {
        "service": "system", // Service
        "method": "reported", // Method
        "parms": {

        } // Parameters
    }
}
```

*Command Execution Response*

```json
{
    "type" : "command_reply",
    "version": 1,
    "session" : "xxxxxxxxxxxxxxxxxxxxxx",
    "deviceId" : "xxxxxxxxxxxx",
    "time" : 1234567890,
    "response": {
        "code": 0,
        "message": "success"
        // Returned content
    }
}
```
*Data Reporting*

```json
{
    "type" : "report",
    "version": 1,
    "session" : "xxxxxxxxxxxxxxxxxxxxxx",
    "deviceId" : "xxxxxxxxxxxx",
    "time" : 1234567890,
    "data" : {}  // Specific data to be reported, see the table below
}
```

*Data Reporting Response*    // Response is optional

```json
{
    "type" : "report_reply",
    "version": 1,
    "session" : "xxxxxxxxxxxxxxxxxxxxxx",
    "deviceId" : "xxxxxxxxxxxx",
    "time" : 1234567890,
    "response": {
        "code": 0,
        "message" : "success"
    },
}
```

**Supported Report Message Types**

1. backboard-info

   Backplane Information

    ```json
    {
        "id":0,
        "slotNum":7,
        "model":"G1",
        "slots":[{
            "id":1,
            "name": "slot1",// Slot name
            "used": true,// Whether in use
            "subBoardId":  -1,// Subboard ID
            "subBoardModel": "MainBoard-Switch" // Subboard model
            "controlType": "SingleControl" // Power board control type Default value "N/A", single control "SingleControl", main control "masterControl"
            },...]
        }
   
    ```

2.1 backboard-state

   Backplane information, if only one fan is configured, use fan 1

```json
    {
    
        "spdAlert": false, // Surge protector alarm
        "spdSurge": 0, // Lightning strikes
        "ardState": true, // Reclosing switch status
        "ardAlert": false,
        "ardVoltage": 232, // Reclosing switch voltage
        "ardCurrent": 0, // Reclosing switch current
        "autoLight": false, // Automatic light status
        "doorState": true, // Door status
        "lightState": true, // Light status
        "heaterState": false, // Heater status
        "fan1Alert": false, // Fan 1 alarm
        "fan1State": false,// Fan 1 status
        "fan1Speed": 0, // Fan 1 speed
        "fan2Alert": false, // Fan 2 alarm
        "fan2State": false, // Fan 2 status
        "fan2Speed": 0,     // Fan 2 speed
        "waterAlert": false // Water immersion alarm
    }
```

2.2 V1/backboard-state

Backplane information
This interface is the same as the backboard-state topic interface in data content, but the format of the returned content is optimized.

```json
    {
    
        "spdAlert": false, // Surge protector alarm
        "spdSurge": 0, // Lightning strikes
        "ardState": true, // Reclosing switch status
        "ardAlert": false,
        "ardVoltage": 232, // Reclosing switch voltage
        "ardCurrent": 0, // Reclosing switch current
        "autoLight": false, // Automatic light status
        "doorState": true, // Door status
        "lightState": true, // Light status
        "heaterState": false, // Heater status
        "waterAlert": false // Water immersion alarm
        "fan":[
            {
                "id":1, // Fan ID
                "fanSpeed": 0, // Fan speed
                "fanAlert": false, // Fan alarm
                "fanState": false,// Fan status
            }
            ...
        ]
    }
```

3. system-state

   System Status

    ```json
    {
        "dateTime": 32059, // System time
        "runTime": 3259,// Running time
        "cpuUsaged": 2156, // CPU usage
        "memTotalSize": 246452, // Total memory (kb)
        "memFreeSize": 191336, // Free memory (kb)
        "memUsaged": 2236, // Used memory (kb)
        "storageTotalSize": 1997240,// Flash capacity (kb)
        "storageFreeSize": 1917244,// Free flash capacity (kb)
        "storageUsaged": 400,// Used flash capacity (kb)
        "temperature": 34,// Temperature
        "humitidy": 32,// Humidity
        "poeRealPower": // POE real-time power
    }
    ```

4. system-info

   System Information

    ```json
    {
        "model": "zkiot.sw4e1f", // Product model
        "showModel": "zkiot.sw4e1f",// Display model
        "deviceName": "ZK618T-48D858",// Hardware version
        "description": "ZK618T-48D858",// Description
        "serialNumber": "ZK618T-48D858",// Serial number
        "swVersion": "V1.1.297 beta01",// Software version
        "swReleasedTime": 1639657200, // Release time
        "hwVersion": "1.3",// Hardware version
        "osVersion": "V1.0.297 beta00",// System version
        "kernelVersion": "Linux-4.19.94",// Kernel version
        "macAddress": "30E283-48D858",// MAC address
        "modelInfo": "8GT2GX_N_N_1_0_C_N_A", // Model encoding
        "mqttBroker":{
            "protocol":"",
            "host":"",
            "port":"",
        }
    }
    ```

5. switch-state
   
   Switch State
   ```json
   [{
           "id":	0,
           "name":	"cpu",// Interface name
           "capability":	"cpu,",// Port type information: Electrical port, Optical port, supported capability states
           "adminStatus":	true,// Port management status
           "linkUp":	false,// Port status
           "linkMedia":	"copper",// Port media
           "linkSpeed":	"10m",// Link speed
           "linkDuplex":	"half"// Duplex mode
   }			
   ]
           
   ```


6. netdmate-ethernet-state

   Network Interface Information

   ```json
   {
       "name":	"sw1", // Interface name
       "enabled":	1,// Activation status
       "dhcpEnabled":	0,// DHCP activation status
       "state":	2,// Connection state
       "vlan":	1,// Management VLAN
       "connectedTime":	8,//
       "disconnectedTime":	0,
       "leaseUpdatedTime":	0,//
       "address":	"192.168.3.1/24",// IP address
       "gateway":	"0.0.0.0 ",// Gateway
       "dns":	"0.0.0.0 0.0.0.0 "// DNS
   }
   ```

7. netdmate-manage-get

   Network Interface Information

   ```json
   {
       "enabled": 1,    // Enable management IP
       "ip": "192.168.1.249",    // Management IP
       "netmask": "255.255.255.0",  // Subnet mask
       "dhcpdEnabled": 0,  // Enable DHCP server
       "dhcpdLeaseBegin": "192.168.1.100",  // DHCP start address
       "dhcpdLeaseEnd": "192.168.1.200",  // DHCP end address
       "dhcpdLeasePeriod": 12,  // Lease period
   }
   ```

8. netdmate-mobile-gps  // GPS changes will be actively reported in this topic

   GPS Information

   ```json
   {
       "latitude" : 1.000000, //double  Latitude
       "latitude_h": "N", //string Latitude hemisphere    "N"/"S" // North or South Latitude
       "longitude": 1.000000, //double Longitude
       "longitude_h": "E", // string Longitude hemisphere   "E"/"W" // East or West Longitude
       "altitude": 1.000000, // double Altitude
       "altitude_u": "M" // string Altitude unit   "M" // Altitude unit in meters
   }
   ```

9. netdmate-mobile-state

   4G Information

| Data | Type | Constraint |
| -- | -- | -- |
| Interface Name | | lte1 |
| Firmware Information | | e.g., firmware version |
| IMEI | | |
| IMSI | | |
| ICCID | | |
| Data Management Status | | Whether to start the data connection |
| Connection Status | | {"UNKNOWN", "INIT", "SIM_NOTREADY", "SIM_READY",<br>"REGISTERED", "DATA_CONNECTED"} |
| Signal Level | | In dbm |
| Service Type  | | {"GPRS", "EDGE", "UMTS", "IS95A", "IS95B", "1xRTT",<br>"EVDO_0", "EVDO_A", "HSDPA", "HSUPA", "HSPA", "EVDO_B",<br>"EHRPD", "LTE", "HSPAP", "GSM"} |
| Operator | | |
| CELL Connection Time | | |
| CELL Disconnection Time | | |
| Data Connection Time | | |
| Data Disconnection Time | | |
| IPV4 Address | | |
| IPV4 Subnet Mask | | |
| IPV4 Gateway | | |
| IPV4 DNS1 | | |
| IPV4 DNS2 | | |

   ```json
   {
        "name": "lte1",
        "moduleVersion": "",
        "imei": "",
        "imsi": "",
        "iccid": "",
        "dataEnable": 0,
        "state": "UNKNOWN",
        "signalLevel": 0,
        "rssi": 0,
        "operator": "",
        "serviceTech": "N/A",
        "cellConnectedTime": 0,
        "cellDisconnectedTime": 0,
        "dataConnectedTime": 0,
        "dataDisconnectedTime": 0,
        "ipAddr": "0.0.0.0",
        "nmAddr": "0.0.0.0",
        "gwAddr": "0.0.0.0",
        "dns1Addr": "0.0.0.0",
        "dns2Addr": "0.0.0.0"
   }
   ```

10. netdmate-wifiap-config  

   Wi-Fi Configuration Information

   ```json
   {
        "name": "wifi1", // string Name
        "enabled": 1, // int On/Off
        "channel": 6, // int Channel
        "ssid": "ZKIOT_926486", // string Wi-Fi name
        "password": "12345678" // string Password
   }
   ```

11. powerboard-state-slotN  // N denotes the slot number, range: 2 - 6  // The reported content for this topic has been canceled

   Power Board Information, following keys vary depending on different boards,

   ```json
   {
       "voltage": 0, // int Voltage value
       "state": , //bool Main control switch state
       "type":, //string Power type AC/DC
       "channel":[
        {
            "id": // int Channel number
            "state": , // bool Channel switch state
            "current": , // int Current value
            "power": , // int Power value
        }
       ]
   }
   ```

11. refresh-powerboard-state  // Report all power boards

   Power Board Information, following keys vary depending on different boards,

```json
{"List":[
    {"slotId":2,"subBoardId":1,"voltage":0,"state":false,"type":"DC","controlType":"masterControl","channel":[
        {"id":1,"state":false},
        {"id":2,"state":false},
        {"id":3,"state":false},
        {"id":4,"state":false}]},
    {"slotId":3,"subBoardId":2,"voltage":0,"state":false,"type":"DC","controlType":"masterControl","channel":[
        {"id":1,"state":false},
        {"id":2,"state":false},
        {"id":3,"state":false},
        {"id":4,"state":false},
        {"id":5,"state":false},
        {"id":6,"state":false},
        {"id":7,"state":false},
        {"id":8,"state":false}]},
    {"slotId":4,"subBoardId":20,"voltage":9,"state":true,"type":"DC","Alert":true,"controlType":"SingleControl","Ccurrentvalue":"300","Wcurrentvalue":"150","channel":[
        {"id":1,"state":false,"current":1,"power":0},
        {"id":2,"state":false,"current":1,"power":0},
        {"id":3,"state":false,"current":1,"power":0},
        {"id":4,"state":false,"current":1,"power":0},
        {"id":5,"state":false,"current":0,"power":0},
        {"id":6,"state":false,"current":0,"power":0}]},
    {"slotId":5,"subBoardId":14,"voltage":0,"type":"AC","controlType":"SingleControl","channel":[
        {"id":1,"state":false,"current":0,"power":0},
        {"id":2,"state":false,"current":0,"power":0},
        {"id":3,"state":false,"current":0,"power":0},
        {"id":4,"state":false,"current":0,"power":0}]}]}
```

13. serial-battery-state 

Data Definition:
| Description | Data | Type | Constraint |
| -- | -- | -- | -- |
| Total Voltage | voltage | uint32_t | Value divided by 100, V, precision 10mV |
| Current | current | uint32_t | Value divided by 100, A, precision 10mA |
| Remaining Capacity | remainCapacity | uint32_t | Value multiplied by 10, mAH, precision 10mAH |
| Nominal Capacity | fullCapacity | uint32_t | Value multiplied by 10, mAH, precision 10mAH |
| Cycle Count | cycleIndex | uint32_t |  |
| Product Date | productDate | string |  |
| Cell Overvoltage Protection | cellOvervoltage | bool |  |
| Cell Undervoltage Protection | cellUndervoltage | bool |  |
| Group Overvoltage Protection | overvoltage | bool |  |
| Group Undervoltage Protection | undervoltage | bool |  |
| Charge Overtemperature Protection | chargeHighTemp | bool |  |
| Charge Low Temperature Protection | chargeLowTemp | bool |  |
| Discharge Overtemperature Protection | dischargeHighTemp | bool |  |
| Discharge Low Temperature Protection | dischargeLowTemp | bool |  |
| Charge Overcurrent Protection | chargeOvercurrent | bool |  |
| Discharge Overcurrent Protection | dischargeOvercurrent | bool |  |
| Short Circuit Protection | shortCurrent | uint32_t |  |
| IC Fault Detection | icFault | uint32_t |  |
| MOS Software Lock | mosLock | uint32_t |  |
| Software Version | swVersion | uint32_t | Hex |
| Remaining Capacity Percentage | rsoc | uint32_t | % |
| Charging MOS State | charging | bool | true - On, false - Off |
| Discharging MOS State | discharging | bool | true - On, false - Off |
| Battery String Count | batteryQty | uint32_t |  |
| Cell Voltage | voltageCell | array | mV, precision 1mV |
| Temperature Count | tempQty | uint32_t |  |
| Cell Temperature | temperatureCell | array | Value divided by 10, °C |
| Hardware Version | hwVersion | string |  |

   ```json
   {
        "voltage": 0,
        "current": 0,
        "remainCapacity": 0,
        "fullCapacity": 0,
        "cycleIndex": 0,
        "productDate": "",
        "cellOvervoltage": false,
        "cellUndervoltage": false,
        "overvoltage": false,
        "undervoltage": false,
        "chargeHighTemp": false,
        "chargeLowTemp": false,
        "dischargeHighTemp": false,
        "dischargeLowTemp": false,
        "chargeOvercurrent": false,
        "dischargeOvercurrent": false,
        "shortCurrent": false,
        "icFault": false,
        "mosLock": false,
        "swVersion": 0,
        "rsoc": 0,
        "charging": false,
        "discharging": false,
        "batteryQty": 0,
        "voltageCell": [

        ],
        "tempQty": 0,
        "temperatureCell": [

        ],
        "hwVersion": ""
   }
   ```

14. serial-powerMeter-state 

Data Definition:
| Description | Data | Type | Constraint |
| -- | -- | -- | -- |
| Total Active Energy Combined | energyCombined | string | -- |
| Total Active Forward Energy | energyPositive | string | -- |
| Total Active Reverse Energy | energyReverse | string | -- |
| Phase A Voltage | voltage | string | -- |
| Phase A Current | current | string | -- |
| Instantaneous Power of Phase A | powerInstant | string | -- |
| Power Factor of Phase A | powerFactor | string | -- |
| Frequency | frequence | string | -- |
| Communication Baudrate | baudrate | string | -- |
| Communication Address | devAddr | string | -- |
| Meter Constant | meterConst | uint32_t | -- |
| Read Meter Parameters Result | readFailed | uint32_t | 0 - Success, non-zero - Failure^Note 1^ |

   ```json
   {
        "energyCombined": "0.15kWh",
        "energyPositive": "0.15kWh",
        "energyReverse": "0.00kWh",
        "voltage": "231.4V",
        "current": "0.00A",
        "powerInstant": "0.00kW",
        "powerFactor": "0.000",
        "frequence": "50.01Hz",
        "baudrate": "4800",
        "devAddr": "1",
        "meterConst": 1600,
        "readFailed": 0
   }
   ```

15. platform-time-get
Description: Device fetches platform time, reporting period is every 1 hour.

*Data Reporting*
```
no data
```

*Reporting Response*
```json
{
    "time": "2022-07-23 10:10:10",   // Time, needs to follow this format
    "timeZone": "America/New_York"  // Time zone, keep this format
}
```

16. switch-ddmInfo

   Switch State
   ```json
   [{
           "num":	2,
		   "ddmData" : [
			{
				"port": 9,// Port number
				"name": "port9", // Port name
				"identifier": "SFP",// Physical type identifier
				"connector": "LC",// Connector type
				"transceiver": "100BASE-FX",// Transceiver 	
				"encoding": "8B/10B",// Encoding
				"vendorName": "OEM",// Vendor name
				"vendorOUI": "123456",// Vendor OUI
				"vendorPN": "XPTN-GS1D-13-LC",// Module model
				"vendorRev": "V2",// Module revision
				"vendorSN": "1705220081",// Module serial number
				"wavelength": "1310nm",// Wavelength
				"vendorDate": "2017052"// Production date
			},
		   ]
   }
   ]
           
   ```

17. switch-ddmMonitor

   Switch State
   ```json
   [{
        "num": 2,
        "ddmData": [
                {
                        "port": 9,
                        "name": "port9",
                        "temper": "72.019",// Temperature in °C
                        "voltage": "1.7",// Voltage in V
                        "current": "0.0",// Current in mA
                        "TxPower": "0.0",// Tx power in mW
                        "RxPower": "0.0",// Rx power in mW
                },
                {
                        "port": 10,
                        "name": "port10",
                        "temper": "72.019",
                        "voltage": "1.7",
                        "current": "0.0",
                        "TxPower": "0.0",
                        "RxPower": "0.0",
                }
        ]
    }			
   ]
           
   ```

18. system-customizationInfo

   Customer Customization Information

```json
{
    "poleNumber": "hello" // Pole number
}
```

19. switch-port-statistics

    Switch Port Traffic Statistics
    ```json
    [
        {
            "id":1, // int Port number
            "name":"port1", // string Port name
            "rxByte":0, // u64 Received bytes
            "txByte":0, // u64 Sent bytes
            "rxPacket":0, // u32 Received packets
            "txPacket":0, // u32 Sent packets
            "rxError":0, // u32 Received error packets
            "txError":0 // u32 Sent error packets
        },
        ...
    ]
    ```

20. switch-info-mac

    Switch MAC Address
    ```json
    {
        "switchMac":"30E283-489F33" // string Switch MAC address
    }
    ```

21. devicebind-list

    Existing Device Binding List
    ```json
    {
        "bindlist":[
            {
                "ip":"NONE", // string Bound device IP
                "name":"123", // string Bound device name
                "switchPort":1, // int Bound switch port
                "location":4, // int Power board slot number
                "channel":1, // int Power channel number
                "uuid":"00000000-0000-0000-0000-000000000000", // Device unique identifier
                "state" : true: Online, false: Offline // Status (bool)
                "type": “switch”，“camera” ,“other”// Device type (char)
                "account":"NONE",//
                "password": "NONE",//
            },
            ...
        ]
    }
    ```

## 9. Alarm Reporting

9.1 Alarm Reporting

```json
{
    "type" : "alarm",
    "version": 1,
    "session" : "xxxxxxxxxxxxxxxxxxxxxx",
    "deviceId" : "xxxxxxxxxxxx",
    "time" : 1234567890,
    "data" : {
        "time" : "",
        "group" : "",
        "instance": "",
        "level" : "",
        "message": "",
        "warningId": "" // Alarm ID 
    }  
}
```

```json
{
    "type" : "will",
    "version": 1,
    "session" : "xxxxxxxxxxxxxxxxxxxxxx",
    "deviceId" : "xxxxxxxxxxxx",
    "time" : 1234567890,
    "data" : {
        "event": "device down"
    }  
}
```
 Platform Will Format:
```json
{
    "type" : "will",
    "version": 1,
    "session" : "xxxxxxxxxxxxxxxxxxxxxx",  // Can be filled with any value
    "deviceId" : "xxxxxxxxxxxx",  // Can be filled with any value
    "time" : 1234567890,
    "data" : { 
        "event": "platform down"
    }  
}
```

9.2 Alarm Summary

Refer to the file "Scodeno Smart Distribution Box Alarm Statistics".

## 10. Platform Command Issuance

10.1 Platform Command Issuance

*Command Reception*

```json
{
    "type" : "command",
    "version": 1,
    "session" : "xxxxxxxxxxxxxxxxxxxxxx",
    "deviceId" : "xxxxxxxxxxxx",
    "time" : 1234567890,
    "data" : {
        "service": "", // Service
        "method": "", // Method
        "parms": {

        } // Parameters
    }
}
```

*Command Execution Response*

```json
{
    "type" : "command_reply",
    "version": 1,
    "session" : "xxxxxxxxxxxxxxxxxxxxxx",
    "deviceId" : "xxxxxxxxxxxx",
    "time" : 1234567890,
    "response": {
        "code": 0,
        "message": {

        } // Returned content
    }
}
```

10.2 Protocol Content

| Function Name | Type | Topic | Description |
| -- | -- | -- | -- |
| Command Reception | Device subscribes | sys/service/{deviceId}/command | Platform issues command |
| Command Execution Response | Device publishes | sys/device/{deviceId}/command_reply/{subTopic} | |

> Note: In the topic, deviceId is temporarily set as "device type_MAC address",
> Current device types:
> smartBox  // Smart box
> miniGW    // Mini gateway

*Command Reception*

```json
{
    "type" : "command",
    "version": 1,
    "session" : "xxxxxxxxxxxxxxxxxxxxxx",
    "deviceId" : "xxxxxxxxxxxx",
    "time" : 1234567890,
    "data" : {
        "service": "", // Service
        "method": "", // Method
        "parms": {

        } // Parameters
    }
}
```

*Command Execution Response*

```json
{
    "type" : "command_reply",
    "version": 1,
    "session" : "xxxxxxxxxxxxxxxxxxxxxx",
    "deviceId" : "xxxxxxxxxxxx",
    "time" : 1234567890,
    "response": {
        "code": 0,
        "message": {

        } // Returned content
    }
}
```

### System Modules

#### System State
Data Definition:
| Data | Type | Constraint |
| -- | -- | -- |
| Device Date and Time | | |
| Power On Runtime | | |
| CPU Usage | | |
| Total Memory Size (KB) | | |
| Available Memory Size (KB) | | |
| Memory Usage | | |
| Total Storage Space (KB) | | |
| Available Storage Space (KB) | | |
| Device Temperature | | |
| Device Humidity | | |
| POE Real-Time Total Power (for POE devices) || |
| Alarm Sound State | bool | Buzzer is configured to be ON + Buzzer manual switch ON + Alarm occurs = true (currently buzzing) |

1. Get Configuration

*Command Reception*
```
{
    "data": {
        "service": "system", // Service
        "method": "state", // Method
        "parms": {
        } // Parameters
    }
}
```

*Command Execution Response*

system-state

```
{
    "response": {
        "code": 0,
        "message": {
            "dateTime": 1732284924,
            "runTime": 16481,
            "cpuUsaged": 10000,
            "memTotalSize": 246452,
            "memFreeSize": 172084,
            "memUsaged": 3017,
            "storageTotalSize": 1997240,
            "storageFreeSize": 1990632,
            "storageUsaged": 33,
            "temperature": 30,
            "humitidy": 38,
            "poeRealPower": 0,
            "buzzerState": false
        }
    }
}
```


#### Time Configuration

Data Definition:

| Data | Description | Type | Constraint | Required/Optional |
| - | - | - | - | - |
| timeEnable | Time acquisition method | string | "ntp"</br>"broker1"</br>"broker2"</br>"manual" | Optional |
| time_c | Manual time setting | string | Sent to the device, ISO 8601 format "2021-12-31T23:59:59+08:00" | Optional |
| time_i | Time | string | Uploaded to the platform, ISO 8601 format "2021-12-31T23:59:59+08:00" | Optional |
| ntpServers | NTP servers | string |  | Optional |
| timeZoneEn | Time zone acquisition method | string | "broker1"</br>"broker2"</br>"manual" | Optional |
| timeZone | Manual time zone setting | string |  | Optional |

1. Get Configuration

*Command Reception*
```
{
    "data": {
        "service": "system", // Service
        "method": "time.get", // Method
        "parms": {
        } // Parameters
    }
}
```

*Command Execution Response*

system-time-get

```
{
    "response": {
        "code": 0,
        "message": {
            "timeEnable": "broker1",
            "time_i": "2021-12-31T23:59:59+08:00",
            "ntpServers": "ntp2.aliyun.com",
            "timeZoneEn": "broker1",
            "timeZone": "America/New_York"
        }
    }
}
```

2. Set Configuration

*Command Reception*
```
{
    "data": {
        "service": "system", // Service
        "method": "time.set", // Method
        "parms": {
            "timeEnable": "broker1",
            "time_c": "2021-12-31T23:59:59+08:00",
            "ntpServers": "ntp2.aliyun.com",
            "timeZoneEn": "manual",
            "timeZone": "America/New_York"
        } // Parameters
    }
}
```

*Command Execution Response*

system-time-set


```
{
    "response": {
        "code": 0,
        "message":  "success"
    }
}
```

#### Remote Reboot

*Command Reception*

```
{
    "data": {
        "service": "system", // Service
        "method": "reboot", // Method
        "parms": {
        } // Parameters
    }
}
```

*Command Execution Response*

system-reboot

```
{
    "response": {
        "code": 0,
        "message": {
            "status": "success"
        }
    }
}
```

### Firmware Upgrade
```sequence 

participant DEV
participant MQTT
participant USER

USER->MQTT: Upload firmware package
USER->MQTT: Issue upgrade task
MQTT->MQTT: Check if the device is online
DEV->MQTT: Device reports firmware version
MQTT->DEV: Provide "download URL and token"
DEV->MQTT: Download package via curl tool
DEV->DEV: Verify downloaded package
MQTT->DEV: Issue upgrade command
DEV->MQTT: Return upgrade command response

NOTE left of MQTT: Wait for device to reconnect
DEV->MQTT: Report upgrade result

MQTT->USER: Notify upgrade status
```

Process Description:
1~2. The user logs into the platform, enters the device management interface, uploads the firmware package, and creates the firmware upgrade task in the console.

3. The platform detects if the device is online. If the device is online, it immediately triggers the upgrade negotiation process. If the device is offline, it waits for the device to come online and subscribe to the upgrade topic. Once the platform detects the device is online, it triggers the upgrade negotiation process (waiting for the device to come online for up to 25 hours).
5. After the platform receives the firmware version reported by the device, the IoT platform determines if the device needs an upgrade based on the target version for the upgrade (timeout for Step 5 is 3 minutes).  
If the reported firmware version matches the target version, the upgrade process ends, and the upgrade task is marked as successful.  
If the reported firmware version is different from the target version and supports upgrading, the process continues to the next step.

6~7. The IoT platform sends the device upgrade package download guidance, token, and related package information. The user downloads the software package using the provided download URL and token via curl. The token expires after 24 hours (the timeout for downloading the package and reporting upgrade status is 60 minutes).

8. The terminal device performs the download package upgrade operation and reports the upgrade result back to the IoT platform after completion (status reported once the device upgrade is complete).

9. The IoT platform notifies the console/application server of the upgrade result.

> In case the package download is interrupted, does the platform support resuming from where it left off?  
>> The device does not support power-off resume.

*Command Reception*
```
{
    "data": {
        "service": "system", // Service
        "method": "update.upload", // Method
        "parms": {
            "url": "",  // The URL from which the device can fetch the file
            "fileAttributes": {
                "hash": "",  // MD5 hash of the firmware package
                "alias": "" // The file name for the firmware, e.g., "update.all" -> os.zip, "update.app" -> app.zip
            }
            ... // Do you need file size, token, expiration time, etc.?
        } // Parameters
    }
}
```

*Command Execution Response*

subTopic: system-update-upload

```
{
    "response": {
        "code": 3, // 0-unknown, 1-uploading, 2-upload failed, 3-upload successful, 4-upgrading, 5-upgrade failed, 6-upgrade successful
        "message": "success" // Response content
    }
}
```

*Command Reception*
```
{
    "data": {
        "service": "system", // Service
        "method": "update.all", // Method
        "parms": {

            }
        } // Parameters
    }
}
```

*Command Execution Response*

subTopic: system-update-all

```
{
    "response": {
        "code": 0, 
        "message": "success" // Response content
    }
}
```

#### Configuration File Upload/Download
```sequence 

participant DEV
participant MQTT
participant USER

MQTT->DEV: Send upload configuration file command
DEV->MQTT: Upload configuration file to platform using curl

MQTT->USER: Download configuration file to local???

MQTT->DEV: Send download configuration file command
DEV->MQTT: Download configuration file to device using curl
DEV->DEV: Device reboot

MQTT->USER: Configuration file uploaded to device???
```

*Command Reception*
```
{
    "data": {
        "service": "system", // Service
        "method": "configFile.upload", // Method
        "parms": {
            "url": "",
            "fileAttributes": {
                "hash": "" // MD5 hash of the file
            }
        } // Parameters
    }
}
```

*Command Execution Response*

system-configFile-upload

```
{
    "response": {
        "code": 0,
        "message": "success" // Response content
    }
}
```

*Command Reception*
```
{
    "data": {
        "service": "system", // Service
        "method": "configFile.download", // Method
        "parms": {
            "url": ""
        } // Parameters
    }
}
```

*Command Execution Response*

system-configFile-download

```
{
    "response": {
        "code": 0,
        "message": {
            "hash" : "" // MD5 hash of the file
        } // Response content
    }
}
```

#### Factory Reset

*Command Reception*

```
{
    "data": {
        "service": "system", // Service
        "method": "restore", // Method
        "parms": {} // Parameters
    }
}
```

*Command Execution Response*

system-restore

```
{
    "response": {
        "code": 0,
        "message": {
            "status": "success"
        }
    }
}
```

#### MQTT Broker Information Retrieval

*Command Reception*

```
{
    "data": {
        "service": "system", // Service
        "method": "mqttBrokerAddr.get", // Method
        "parms": {} // Parameters
    }
}
```

*Command Execution Response*

system-restore

```
{
    "response": {
        "code": 0,
        "message": {
            "brokerAddrs":[
                {
                    "id":1,
                    "brokerAddr":"tcp://192.168.1.252:60022",
                    "username":"r",
                    "password":"r"
                }
            ]
        }
    }
}
```

#### Modify Pole Number

*Platform Issues Command*

```
{
    "data": {
        "service": "system", // Service
        "method": "customization.set", // Method
        "parms": { // Parameters
            "poleNumber": "hello" // Pole number
        }
    }
}
```

*Device Executes Command Response*

system-customizationInfo-set

```
{
    "response": {
        "code": 0,
        "message": "success"
    }
}
```

#### Modify Device Name

*Platform Issues Command*

```
{
    "data": {
        "service": "system", // Service
        "method": "setting.set", // Method
        "parms": { // Parameters
            "deviceName": "device-scodeno" // Device name
        }
    }
}
```

*Device Executes Command Response*

system-setting-set

```
{
    "response": {
        "code": 0,
        "message":  "success"
    }
}
```

### IO Collection Module

#### Status Retrieval

Data Definition:
| Data | Description | Type | Constraint |
| -- | -- | -- | -- |
| Surge Protector Status | | bool | |
| Surge Count | | u32 | |
| Reclosure Alarm | | bool | |
| Reclosure Voltage | | u32 | |
| Reclosure Current | | u32 | |
| Light Strip Inversion Status | | bool | |
| Box Door Status | | bool | |
| Light Strip Status | | bool | |
| Heating Status | | bool | |
| Fan Status | | bool | |
| Fan Alarm | | bool | |
| Fan Real-time Speed | | u32 | |
| Water Immersion Alarm | | bool | |
```

{
    "data": {
        "service": "slot7", // Service
        "method": "state", // Method
        "parms": {} // Parameters
    }
}
```

*Command Response*  
slot7-state

```
{
    "response": {
    "code": 0,
    "message": {
        "spdAlert": false,
        "spdSurge": 0,
        "ardState": false,
        "ardAlert": false,
        "ardVoltage": 0,
        "ardCurrent": 0,
        "autoLight": true,
        "doorState": true,
        "lightState": true,
        "heaterState": false,
        "waterAlert": false,
        "fan":[
        {
            "id":1, // Fan ID
            "fanSpeed": 0, // Fan real-time speed
            "fanAlert": false, // Fan alarm
            "fanState": false, // Fan status
        }
            ...
        ]
    }
    }
}
```

#### Fan Control

Data Definition:

| Data | Description | Type | Constraint | Required/Optional |
| -- | -- | -- | -- | -- |
| autoControl | Fan auto control | bool |  | Optional |
| tempThresholdOn | Fan temperature on threshold | int |  | Optional, exists with off threshold |
| tempThresholdOff | Fan temperature off threshold | int |  | Optional |
| fanNum | Number of fans | int |  | Optional |
| fans | Fan switch | Array | | Optional |
Fans List:
| Data | Description | Type | Constraint | Required/Optional |
| -- | -- | -- | -- | -- |
| id | Fan ID | int |  | Required |
| speed | Fan speed | int | | Optional |
| sw | Fan switch | bool |  | Optional |

1. Get Configuration

*Command Reception*
```
{
    "data": {
        "service": "slot7", // Service
        "method": "fanConfig.get", // Method
        "parms": { } // Parameters
    }
}
```

*Command Execution Response*

slot7-fanConfig-get

```
{
    "response": {
        "code": 0,
        "message": {
            "autoControl": true,
            "tempThresholdOn": 40,
            "tempThresholdOff": 35,
            "fanNum": 2,
            "fans" : [
                {
                    "id": 1,
                    "speed": 2000,
                    "sw": true
                }
            ]
        } // Returned content
    }
}
```

2. Set Configuration

*Command Reception*
```
{
    "data": {
        "service": "slot7", // Service
        "method": "fanConfig.set", // Method
        "parms": { 
            "autoControl": true,
            "tempThresholdOn": 40, 
            "tempThresholdOff": 35,
            "fans" : [
                {
                    "id": 1, // Use the id from get
                    "speed": 2000,
                    "sw": true
                }
            ]
        } // Parameters
    }
}
```

*Command Execution Response*

slotN-fanConfig-set

```
{
    "response": {
        "code": 0,
        "message": "success" // Returned content
    }
}
```

#### Heater Control

Data Definition:

| Data | Description | Type | Constraint | Required/Optional |
| -- | -- | -- | -- | -- |
| heatAuto | Heater auto control | bool |  | Optional |
| heatTempOn | Heater temperature on threshold | int |  | Optional, exists with off threshold |
| heatTempOff | Heater temperature off threshold | int |  | Optional |
| heatingNum | Number of heaters | int |  | Optional |
| heating | Heater switch | Array | | Optional |
Heating List:
| Data | Description | Type | Constraint | Required/Optional |
| -- | -- | -- | -- | -- |
| id | Heater ID | int |  | Required |
| htSwitch | Heater switch | bool |  | Required |

1. Get Configuration

*Command Reception*

```
{
    "data": {
        "service": "slot7", // Service
        "method": "heatConfig.get", // Method
        "parms": { } // Parameters
    }
}
```

*Command Execution Response*

slot7-heatConfig-get

```
{
    "heatAuto": true,
    "heatTempOn": -20,
    "heatTempOff": -10,
    "heatingNum": 1,
    "heating" : [
        {
            "id": 1,
            "sw": true
        }
    ]
}
```

2. Set Configuration

*Command Reception*
```
{
    "data": {
        "service": "slot7", // Service
        "method": "heatConfig.set", // Method
        "parms": { 
            "heatAuto": true,
            "heatTempOn": -20,
            "heatTempOff": -10,
            "heating" : [
                {
                    "id": 1,  // Use the id from get
                    "sw": true
                }
            ]
        } // Parameters
    }
}
```

*Command Execution Response*

slot7-heatConfig-set

```
{
    "response": {
        "code": 0,
        "message": "success" // Returned content
    }
}
```

#### Recloser Restart

*Command Reception*
```
{
    "data": {
        "service": "slot7", // Service
        "method": "ard.restart", // Method
        "parms": { 

        } // Parameters
    }
}
```

*Command Execution Response*

slotN-ard-restart

```
{
    "response": {
        "code": 0,
        "message": "success" // Returned content
    }
}
```

### Power Module

#### Get All Power Board Information
*Command Reception*
```
{
    "data": {
        "service": "system", // Service
        "method": "powerBoardInfo.get", // Method
        "parms": { 
        } // Parameters
    }
}
```
*Command Execution Response*
powerboard-state-list
```
{"List":[
    {"slotId":3,"state":false,"channel":[
        {"id":1,"state":false},
        {"id":2,"state":false},
        {"id":3,"state":false},
        {"id":4,"state":false}]},
    {"slotId":4,"voltage":4762,"state":true,"type":"DC","channel":[
        {"id":1,"state":true,"current":11,"power":557},
        {"id":2,"state":true,"current":0,"power":43},
        {"id":3,"state":true,"current":0,"power":39},
        {"id":4,"state":true,"current":0,"power":38},
        {"id":5,"state":true,"current":0,"power":24},
        {"id":6,"state":true,"current":0,"power":38}]},
    {"slotId":5,"voltage":2532,"state":true,"type":"AC","channel":[
        {"id":1,"state":false,"current":0,"power":0},
        {"id":2,"state":false,"current":0,"power":0},
        {"id":3,"state":true,"current":0,"power":0},
        {"id":4,"state":true,"current":0,"power":0},
        {"id":5,"state":true,"current":0,"power":0},
        {"id":6,"state":false,"current":0,"power":0}]},
    {"slotId":6,"voltage":23394,"state":true,"type":"AC","channel":[
        {"id":1,"state":true,"current":0,"power":0},
        {"id":2,"state":true,"current":0,"power":0},
        {"id":3,"state":true,"current":0,"power":0},
        {"id":4,"state":true,"current":0,"power":0},
        {"id":5,"state":true,"current":0,"power":0}]}]}
```
> Single switch and master control switch use the same interface.

#### Single Switch

Data Definition:

| Data | Description | Type | Constraint | Required/Optional |
| -- | -- | -- | -- | -- |
| channel | Channel | Array |  | Required |

Channel List:
| Data | Description | Type | Constraint | Required/Optional |
| -- | -- | -- | -- | -- |
| id | Port number | int |  | Required |
| name | Name | string |  | Required |
| sw | Switch | bool |  | Required |

1. Get Configuration

*Command Reception*
```
{
    "data": {
        "service": "slotN", // Service "slotN": Slot number
        "method": "setting.get", // Method
        "parms": { 
        } // Parameters
    }
}
```

*Command Execution Response*

slotN-setting-get

```
{
    "response": {
        "code": 0,
        "message": {
            // No "num" : 2,
            "channel" : [
                {
                    "id" : 1,
                    "name" : "channel1",
                    "sw" : true		
                },
                {
                    "id" : 2,
                    "name" : "channel2",
                    "sw" : true		
                },
                ...
            ]
        }
    }
}
```
2. Set Configuration

*Command Reception*
```
{
    "data": {
        "service": "slotN", // Service "slotN": Slot number
        "method": "setting.set", // Method
        "parms": { 
            "channel" ：[
                {
                    "id": 1,
                    "name" : "channel6",
                    "sw": true
                }
                ...
            ]
        } // Parameters
    }
}
```

*Command Execution Response*

slotN-setting-set

```
{
    "response": {
        "code": 0,
        "message":  "success"
    }
}
```

#### Master Control Switch

Data Definition:

| Data | Description | Type | Constraint | Required/Optional |
| -- | -- | -- | -- | -- |
| powerAssyControl | Master control switch | bool |  | Required |
| channel | Channel | Array |  | Not required |

1. Get Configuration

*Command Reception*
```
{
    "data": {
        "service": "slotN", // Service "slotN": Slot number
        "method": "setting.get", // Method
        "parms": { 
        } // Parameters
    }
}
```

*Command Execution Response*

slotN-setting-get

```
{
    "response": {
        "code": 0,
        "message": {
            "powerAssyControl": true
        }
    }
}
```

2. Set Configuration

*Command Reception*
```
{
    "data": {
        "service": "slotN", // Service "slotN": Slot number
        "method": "setting.set", // Method
        "parms": { 
            "powerAssyControl": true
        } // Parameters
    }
}
```

*Command Execution Response*

slotN-setting-set

```
{
    "response": {
        "code": 0,
        "message":  "success"
    }
}
```

#### AC24M4 Power Board Alarm Current Threshold and Warning Current Threshold Settings

"parms"
| Data | Description | Type | Constraint | Required/Optional |
| -- | -- | -- | -- | -- |
| Ccurrentvalue | Alarm current threshold | char, no more than 8 characters |  | Optional |
| Wcurrentvalue | Warning current threshold | char, no more than 8 characters |  | Optional |

*Command Reception*
```
{
    "data": {
        "service": "slotN", // Service "slotN": Slot number
        "method": "setting.currentvalue", // Method
        "parms": { 
            "Ccurrentvalue": "3" ,//3A
            "Wcurrentvalue": "3" //3A
        } // Parameters
    }
}
```

*Command Execution Response*

slotN-setting-currentvalue

```
{
    "response": {
        "code": 0,
        "message": "success"
    }
}
```

### Switch Module
#### Interface UP/DOWN

Data Definition:

| Data | Description | Type | Constraint | Required/Optional |
| -- | -- | -- | -- | -- |
| port | Port number | int |  | Required |
| adminStatus | Switch | bool |  | Required |

1. Get Configuration

*Command Reception*
```
{
    "data": {
        "service": "switch.port", // Service
        "method": "setting.get", // Method
        "parms": { 
        } // Parameters
    }
}
```

*Command Execution Response*

switch-port-setting-get

```
{
    "response": {
        "code": 0,
        "message": {
            "num" : 2,
            "ports" : [
                {
                    "id" : 1,
                    "adminStatus" : true		
                },
                {
                    "id" : 2,
                    "adminStatus" : true		
                },
                ...
            ]
        }
    }
}
```

2. Set Configuration

*Command Reception*
```
{
    "data": {
        "service": "switch.port", // Service
        "method": "setting.set", // Method
        "parms": { 
            "ports" : [
                {
                    "id" : 1,
                    "adminStatus" : true		
                },
                ...
            ]
        } // Parameters
    }
}
```

*Command Execution Response*

switch-port-setting-set

```
{
    "response": {
        "code": 0,
        "message":  "success"
    }
}
```


#### Switch Port Traffic Statistics


*Command Reception*
```
{
    "data": {
        "service": "switch.port", // Service
        "method": "statistics", // Method
        "parms": { 
        } // Parameters
    }
}
```

*Command Execution Response*

switch-port-statistics

```json
    [
        {
            "id":1, // int Port number
            "name":"port1", // string Port name
            "rxByte":"0", // string Received bytes, maximum up to u64 size
            "txByte":"0", // string Sent bytes, maximum up to u64 size
            "rxPacket":0, // u32 Received packets
            "txPacket":0, // u32 Sent packets
            "rxError":0, // u32 Received error packets
            "txError":0 // u32 Sent error packets
        },
        ...
    ]
```

### Network Module
#### Wifi Configuration

Data Definition:

| Data | Description | Type | Constraint | Required/Optional |
| -- | -- | -- | -- | -- |
| name | Name | string |  | Required |
| enabled | Switch | int |  | Required |
| channel | Channel | int |  | Required |
| ssid | Wifi Name | string |  | Required |
| password | Password | string |  | Required |

1. Get Configuration

*Command Reception*
```
{
    "data": {
        "service": "netdmate", // Service
        "method": "wifiap.get", // Method
        "parms": {
        } // Parameters
    }
}
```

*Command Execution Response*

netdmate-wifiap-get

```
{
    "response": {
        "code": 0,
        "message": {
            "name":
            "enabled":
            "channel":
            "ssid":
            "password":
        }
    }
}
```

2. Set Configuration

*Command Reception*
```
{
    "data": {
        "service": "netdmate", // Service
        "method": "wifiap.set", // Method
        "parms": {
            "name":
            "enabled":
            "channel":
            "ssid":
            "password":
        } // Parameters
    }
}
```

*Command Execution Response*

netdmate-wifiap-set

```
{
    "response": {
        "code": 0,
        "message": "success"
    }
}
```

#### Ethernet Configuration

Data Definition:

| Data | Description | Type | Constraint | Required/Optional |
| -- | -- | -- | -- | -- |
| name | Ethernet Name | string | "eth1" - without switch</br>"sw1" - with switch | Required |
| enabled | Management Status | int |  | Fixed as enabled, no setting allowed |
| dhcpEnabled | DHCP Management Status | int |  | Fixed as disabled, no setting allowed |
| vlan | VLAN | int |  | Required |
| ipAddr | IPV4 Address | string |  | Required |
| nmAddr | IPV4 Subnet Mask | string |  | Required |
| gwAddr | IPV4 Gateway | string |  | Required |
| dns1Addr | IPV4 DNS1 | string |  | Required |
| dns2Addr | IPV4 DNS2 | string |  | Required |

1. Get Configuration

*Command Reception*
```json
{
    "data": {
        "service": "netdmate", // Service
        "method": "ethernet.get", // Method
        "parms": {
            "name": "sw1" // Must include Ethernet name
        } // Parameters
    }
}
```

*Command Execution Response*

netdmate-ethernet-get

```json
{
    "response": {
        "code": 0,
        "message": {
            "name": "sw1",
            "enabled": 1,
            "dhcpEnabled": 0,
            "vlan": 1,
            "ipAddr": "192.168.3.1",
            "nmAddr": "255.255.255.0",
            "gwAddr": "0.0.0.0",
            "dns1Addr": "0.0.0.0",
            "dns2Addr": "0.0.0.0"
        }
    }
}
```

2. Set Configuration

*Command Reception*
```
{
    "data": {
        "service": "netdmate", // Service
        "method": "ethernet.set", // Method
        "parms": {
            "name": "sw1",
            "enabled": 1,
            "dhcpEnabled": 0,
            "vlan": 1,
            "ipAddr": "192.168.3.1",
            "nmAddr": "255.255.255.0",
            "gwAddr": "0.0.0.0",
            "dns1Addr": "0.0.0.0",
            "dns2Addr": "0.0.0.0"
        } // Parameters
    }
}
```

*Command Execution Response*

netdmate-ethernet-set

```
{
    "response": {
        "code": 0,
        "message":  "success"
    }
}
```

#### GPS Configuration

1. Get Configuration

*Command Reception*
```json
{
    "data": {
        "service": "netdmate", // Service
        "method": "mobile.gpsGet", // Method
        "parms": {
            "name": "lte1"
        } // Parameters
    }
}
```

*Command Execution Response*

netdmate-mobileGps-get

```json
{
    "response": {
        "code": 0,
        "message": {
                "latitude" : 1.000000, //double Latitude
                "latitude_h": "N", //string Latitude Hemisphere    "N"/"S" for North/South
                "longitude": 1.000000, //double Longitude
                "longitude_h": "E", // string Longitude Hemisphere   "E"/"W" for East/West
                "altitude": 1.000000, // double Altitude
                "altitude_u": "M" // string Altitude Unit   "M" for meters
        }
    }
}
```

2. Set Configuration

*Command Reception* GPS can only be set when GPS is not already configured
```
{
    "data": {
        "service": "netdmate", // Service
        "method": "mobile.gpsSet", // Method
        "parms": {
                "latitude" : "1.000000", //string  Latitude
                "latitude_h": "N", //string Latitude Hemisphere    "N"/"S" for North/South
                "longitude":"1.000000", //string Longitude
                "longitude_h": "E", // string Longitude Hemisphere   "E"/"W" for East/West
                "altitude": "1.000000", //string Altitude
                "altitude_u": "M" // string Altitude Unit   "M" for meters
        } // Parameters
    }
}
```

*Command Execution Response*

netdmate-mobileGps-set

```
{
    "response": {
        "code": 0,
        "message": "success"
    }
}
```

### Alarms
#### Operation Mode

Data Definition:

| Data | Description | Type | Constraint | Required/Optional |
| -- | -- | -- | -- | -- |
| buzzerEnable | Buzzer switch | bool |  | Required |
| timeout | Box open timeout prohibiting entry into maintenance mode | int |  | Required |

1. Get Configuration

*Command Reception*
```
{
    "data": {
        "service": "alarmhub", // Service
        "method": "config.get", // Method
        "parms": {
        } // Parameters
    }
}
```

*Command Execution Response*

alarmhub-config-get

```
{
    "response": {
        "code": 0,
        "message": {
            "buzzerEnable":false,
            "timeout":30
        }
    }
}
```

2. Set Configuration

*Command Reception*
```
{
    "data": {
        "service": "alarmhub", // Service
        "method": "config.set", // Method
        "parms": {
            "buzzerEnable":false,
            "timeout":30
        } // Parameters
    }
}
```

*Command Execution Response*

alarmhub-config-set

```
{
    "response": {
        "code": 0,
        "message":  "success"
    }
}
```

### Device Binding
#### Delete Device Binding

*Command Reception*
```json
{
    "data": {
        "service": "devicebind", // Service
        "method": "del", // Method
        "parms": {
            "ip":"NONE", // string Device IP
            "name":"123", // string Device name
            "switchPort":1, // int Switch port 
            "location":4, // int Power board slot number
            "channel":1 // int Power channel number
        } // Parameters
    }
}
or:
{
    "data": {
        "service": "devicebind", // Service
        "method": "delv1", // Method
        "parms": {
            "uuid":"00000000-0000-0000-0000-000000000000" // Unique device identifier
        } // Parameters
    }
}
```

*Command Execution Response*

devicebind-del

```json
{
    "response": {
        "code": 0,
        "message": "success"
    }
}
```

#### Add Device Binding
*Command Reception*
```json
{
    "data": {
        "service": "devicebind", // Service
        "method": "add", // Method
        "parms": {
            "ip":"NONE", // string Device IP, “switchport” is 0, “IP” is “NONE”
            "name":"123", // string Device name
            "switchPort":1, // int Switch port 
            "location":4, // int Power board slot number
            "channel":1, // int Power channel number
            "type" : “switch”，“camera” ,“other” // Device type (char)
            "account":"NONE", // "NONE" means no
            "password": "NONE" // "NONE" means no
        } // Parameters
    }
}
```

*Command Execution Response*

devicebind-add

```json
{
    "response": {
        "code": 0,
        "message": "success"
    }
}
```

#### These two interfaces are used for Camera-type devices in device binding

*Command Reception: onvif Status Get*
```json
{
    "data": {
        "service": "onvifconfig", // Service
        "method": "onvifconfig.get", // Method
        "parms": {
        } // Parameters
    }
}
```

*Command Execution Response*

onvifconfig-get

```json
{
    "response": {
        "code": 0,
        "message": {
        "state":true, // true: On, false: Off
        }
    }
}
```

*Command Reception: onvif Status Set*
```json
{
    "data": {
        "service": "onvifconfig", // Service
        "method": "onvifconfig.set", // Method
        "parms": {
            "state":true, // true: On, false: Off
        } // Parameters
    }
}
```

*Command Execution Response*

onvifconfig-set

```json
{
    "response": {
        "code": 0,
        "message": "success"
    }
}
```

### PSE Module
#### Get PSE Status

*Command Reception*
```json
{
    "data": {
        "service": "switch.pse", // Service
        "method": "info.get", // Method
        "parms": {
        } // Parameters
    }
}
```

*Command Execution Response*

switch-pse-info-get

```json
{
    "response": {
        "code": 0,
        "message": {
            "pseInfo":[
                {
                    "port":1, // int Port number
                    "class":-1, // int Class level
                    "current":0, // int Current, in 0.1mA
                    "power":0, // int Power, in mW
                    "sw":false, // bool On/Off
                    "status":false // bool Connection status to PD (Powered Device)
                },
                ...
            ]
        }
    }
}
```

#### Set PSE Switch

*Command Reception*
```json
{
    "data": {
        "service": "switch.pse", // Service
        "method": "state.set", // Method
        "parms": {
            "port": 2, // int Port number
            "sw": true // bool On/Off
        } // Parameters
    }
}
```

*Command Execution Response*

switch-pse-state-set

```json
{
    "response": {
        "code": 0,
        "message": "success"
    }
}
```

### Smart Lock Module
#### Get Smart Lock Status

*Command Reception*
```json
{
    "data": {
        "service": "serial", // Service
        "method": "smartLock.state", // Method
        "parms": {
            "uart": N  // N=1: Serial Port 1, N=2: Serial Port 2, each serial port corresponds to one smart lock
        } // Parameters
    }
}
```

*Command Execution Response*

smartLock-state-answer

```json
{
    "response": {
        "code": 0,
        "message": {
            "status": 0  // Smart Lock status: 1: Closed, 0: Open, -1: Error
        } // Return content
    }
}
```

#### Open Smart Lock

*Command Reception*
```json
{
    "data": {
        "service": "serial", // Service
        "method": "smartLock.open", // Method
        "parms": {
            "uart": N  // N=1: Serial Port 1, N=2: Serial Port 2, each serial port corresponds to one smart lock
        } // Parameters
    }
}
```

*Command Execution Response*

smartLock-open-answer

```json
{
    "response": {
        "code": 0,
        "message": {
            "status": 0  // 0: Success, -1: Error
        } // Return content
    }
}
```

#### Read Smart Lock Slot ID

*Command Reception*
```json
{
    "data": {
        "service": "serial", // Service
        "method": "smartLock.readslot", // Method
        "parms": {
            "uart": N,  // N=1: Serial Port 1, N=2: Serial Port 2, each serial port corresponds to one smart lock
            "slot": n   // n = 1~8 Slot number
        } // Parameters
    }
}
```

*Command Execution Response*

smartLock-readslot-answer

```json
{
    "response": {
        "code": 0,
        "message": {
            "idDecimal": "0005437476",  // Card ID
            "name": "jame"  // Username
        } // Return content
    }
}
```

#### Read Last Card ID for Smart Lock

*Command Reception*
```json
{
    "data": {
        "service": "serial", // Service
        "method": "smartLock.lastid", // Method
        "parms": {
            "uart": N  // N=1: Serial Port 1, N=2: Serial Port 2, each serial port corresponds to one smart lock
        } // Parameters
    }
}
```

*Command Execution Response*

smartLock-lastid-answer

```json
{
    "response": {
        "code": 0,
        "message": {
            "idDecimal": "0005437476",    // Card ID
            "name": "jame"  // Username
        } // Return content
    }
}
```

#### Add Smart Lock ID

*Command Reception*
```json
{
    "data": {
        "service": "serial", // Service
        "method": "smartLock.addid", // Method
        "parms": {
            "uart": N,  // N=1: Serial Port 1, N=2: Serial Port 2, each serial port corresponds to one smart lock
            "cardid":"0005437476",  // Card ID
            "name":"jame",    // Custom username, string up to 15 characters
            "slot": n  // n = 1~8 Slot number
        } // Parameters
    }
}
```

*Command Execution Response*

smartLock-addid-answer

```json
{
    "response": {
        "code": 0,
        "message": {
            "idDecimal": "0005437476",  // Card ID
            "name": "jame"  // Username
        } // Return content
    }
}
```

#### Get Smart Lock Unlock Log

*Command Reception*
```json
{
    "data": {
        "service": "serial", // Service
        "method": "smartLock.getlocklog", // Method
        "parms": {
            "pageNum": N,   // Page number, starting from 1
            "pageSize": N,  // Number of records per page
            "filter":""     // Filter criteria, only supports level filtering, can pass an empty string
        } // Parameters
    }
}
```

*Command Execution Response*

smartLock-getlocklog-answer

```json
{
    "response": {
        "code": 0,
        "message": {
            "lineNum": 43,  // Number of unlock log entries
            "content": [
                {
                    "ttime": "2023-07-10 15:44:37",  // Unlock time
                    "name": "niko",   // Username
                    "cardid": "0005874808"  // Card ID
                },
                ...
            ]
        } // Return content
    }
}
```

#### Delete Smart Lock Card ID

*Command Reception*
```json
{
    "data": {
        "service": "serial", // Service
        "method": "smartLock.delslot", // Method
        "parms": {
            "uart": N,  // N=1: Serial Port 1, N=2: Serial Port 2, each serial port corresponds to one smart lock
            "slot": n   // n = 1~8 Slot number
        } // Parameters
    }
}
```

*Command Execution Response*

smartLock-delslot-answer

```json
{
    "response": {
        "code": 0,
        "message": {
            "idDecimal": "0", 
            "name": "NONE"   
        } // Return content
    }
}
```

#### Delete Smart Lock Unlock Log

*Command Reception*
```json
{
    "data": {
        "service": "serial", // Service
        "method": "smartLock.cleanlocklog", // Method
        "parms": {
        } // Parameters
    }
}
```

*Command Execution Response*

smartLock-cleanlocklog-answer

```json
{
    "response": {
        "code": 0,
        "message": {
            "status": 0  // 0: Deletion Successful, -1: Error
        } // Return content
    }
}
```

#### Add Last Card ID as Work Card for Smart Lock

*Command Reception*
```json
{
    "data": {
        "service": "serial", // Service
        "method": "smartLock.addlastcard", // Method
        "parms": {
            "uart": N,    // N=1: Serial Port 1, N=2: Serial Port 2, each serial port corresponds to one smart lock
            "name":"jame",  // Custom username, string up to 15 characters
            "slot": n   // n = 1~8 Slot number
        } // Parameters
    }
}
```

*Command Execution Response*

smartLock-addlastcard-answer

```json
{
    "response": {
        "code": 0,
        "message": {
            "idDecimal": "0005437476",  // Card ID
            "name": "jame"  // Username
        } // Return content
    }
}
```

#### Add Last Card ID as Admin Card for Smart Lock

*Command Reception*
```json
{
    "data": {
        "service": "serial", // Service
        "method": "smartLock.addlastadmin", // Method
        "parms": {
            "uart": N,   // N=1: Serial Port 1, N=2: Serial Port 2, each serial port corresponds to one smart lock
            "

name":"admin"  // Admin username
        } // Parameters
    }
}
```

*Command Execution Response*

smartLock-addlastadmin-answer

```json
{
    "response": {
        "code": 0,
        "message": {
            "idDecimal": "0013196394",  // Card ID
            "name": "admin"  // Username
        } // Return content
    }
}
```

### Other
#### Box Door Photo Upload
```sequence
participant DEV
participant MQTT

MQTT->DEV: Register file server URL, support for retrieval and deletion
DEV->MQTT: Door open alarm

MQTT->DEV: Request image list
DEV->MQTT: Return image list
MQTT->DEV: Request image
DEV->MQTT: Upload image to file server
```

*Command Reception*
```
{
    "data": {
        "service": "backboard", // Service
        "method": "picture.get", // Method
        "parms": {
            "pageNumber": "",
            "pageSize": ""
        } // Parameters
    }
}
```

*Command Response*

backboard-picture-get

```
{
    "response": {
        "code": 0,
        "message": {
            "number" : 1,
            "fileName" : [
                "",
                ...
            ]
        }
    }
}
```

*Command Reception*
```
{
    "data": {
        "service": "backboard", // Service
        "method": "picture.download", // Method
        "parms": {
            "fileName": [
                "",
                ...
            ]
        } // Parameters
    }
}
```

*Command Response*

backboard-picture-download

```
{
    "response": {
        "code": 0,
        "message": "success" // Return content
    }
}
```

*Command Reception*
```
{
    "data": {
        "service": "picture", // Service
        "method": "url.set", // Method
        "parms": {
            "url": ""
        } // Parameters
    }
}
```

*Command Response*

picture-url-set

```
{
    "response": {
        "code": 0,
        "message": "success" // Return content
    }
}
```

*Command Reception*
```
{
    "data": {
        "service": "picture", // Service
        "method": "url.get", // Method
    }
}
```

*Command Response*

picture-url-get

```
{
    "response": {
        "code": 0,
        "message": {
            "url" : ""
        }
    }
}
```

*Command Reception*
```
{
    "data": {
        "service": "picture", // Service
        "method": "url.del", // Method
    }
}
```

*Command Response*

picture-url-del

```
{
    "response": {
        "code": 0,
        "message": "success" // Return content
    }
}
```
