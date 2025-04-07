FLOW CHART

ENTITY RELATIONSHIP

https://www.geeksforgeeks.org/how-to-draw-entity-relationship-diagrams/


connect_reply:
{
  "type": "connect_reply",
  "version": 1,
  "session": "b8d98354-ef5f-41ce-ad6c-8942adb8d6fe",
  "deviceId": "smartBox_ea3778399e77eeb4b1de318552b18d24",
  "time": null,
  "response": {
    "code": 0,
    "message": "success"
  },
  "data": {
    "security": "none"
  }
}

slot7-state:
{
  "type": "command_reply",
  "version": 1,
  "session": "b8d98354-ef5f-41ce-ad6c-8942adb8d6fe",
  "deviceId": "smartBox_ea3778399e77eeb4b1de318552b18d24",
  "time": 1743144688,
  "response": {
    "code": 0,
    "message": {
      "spdAlert": false,
      "spdSurge": 0,
      "ardState": true,
      "ardAlert": false,
      "ardVoltage": 242,
      "ardCurrent": 120,
      "autoLight": true,
      "doorState": true,
      "lightState": true,
      "heaterState": false,
      "waterAlert": false,
      "fan": [
        {
          "id": 1,
          "fanSpeed": 30,
          "fanAlert": false,
          "fanState": false
        }
      ]
    }
  }
}

system-state:
{
  "type": "command_reply",
  "version": 1,
  "session": "b8d98354-ef5f-41ce-ad6c-8942adb8d6fe",
  "deviceId": "smartBox_ea3778399e77eeb4b1de318552b18d24",
  "time": 1743144688,
  "response": {
    "code": 0,
    "message": {
      "dateTime": 1743173488,
      "runTime": 17636,
      "cpuUsaged": 4693,
      "memTotalSize": 246452,
      "memFreeSize": 156708,
      "memUsaged": 3641,
      "storageTotalSize": 1997240,
      "storageFreeSize": 1988400,
      "storageUsaged": 44,
      "temperature": 33,
      "humitidy": 40,
      "poeRealPower": 0
    }
  }
}

flow_monitor:
{
  "type": "command_reply",
  "version": 1,
  "session": "b8d98354-ef5f-41ce-ad6c-8942adb8d6fe",
  "deviceId": "smartBox_ea3778399e77eeb4b1de318552b18d24",
  "time": 1743144685,
  "response": [
    {
      "id": 1,
      "name": "port1",
      "rxByte": "0",
      "txByte": "0",
      "rxPacket": 0,
      "txPacket": 0,
      "rxError": 0,
      "txError": 0
    },
    {
      "id": 2,
      "name": "port2",
      "rxByte": "0",
      "txByte": "0",
      "rxPacket": 0,
      "txPacket": 0,
      "rxError": 0,
      "txError": 0
    },
    {
      "id": 3,
      "name": "port3",
      "rxByte": "714",
      "txByte": "1073703",
      "rxPacket": 11,
      "txPacket": 7917,
      "rxError": 0,
      "txError": 0
    },
    {
      "id": 4,
      "name": "port4",
      "rxByte": "0",
      "txByte": "0",
      "rxPacket": 0,
      "txPacket": 0,
      "rxError": 0,
      "txError": 0
    },
    {
      "id": 5,
      "name": "port5",
      "rxByte": "141296",
      "txByte": "933121",
      "rxPacket": 764,
      "txPacket": 7164,
      "rxError": 0,
      "txError": 0
    },
    {
      "id": 6,
      "name": "port6",
      "rxByte": "35212",
      "txByte": "1041637",
      "rxPacket": 185,
      "txPacket": 7781,
      "rxError": 0,
      "txError": 0
    },
    {
      "id": 7,
      "name": "port7",
      "rxByte": "27279",
      "txByte": "1046498",
      "rxPacket": 129,
      "txPacket": 7789,
      "rxError": 0,
      "txError": 0
    },
    {
      "id": 8,
      "name": "port8",
      "rxByte": "1156111",
      "txByte": "3288459",
      "rxPacket": 8957,
      "txPacket": 8459,
      "rxError": 0,
      "txError": 0
    },
    {
      "id": 9,
      "name": "port9",
      "rxByte": "0",
      "txByte": "0",
      "rxPacket": 0,
      "txPacket": 0,
      "rxError": 0,
      "txError": 0
    },
    {
      "id": 10,
      "name": "port10",
      "rxByte": "0",
      "txByte": "0",
      "rxPacket": 0,
      "txPacket": 0,
      "rxError": 0,
      "txError": 0
    }
  ]
}

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
sys/device/smartBox_ea3778399e77eeb4b1de318552b18d24/profile

{
    "type" : "report",
    "version": 1,
    "session" : "77913627-50a4-4cf7-8f84-09563991d625",
    "deviceId" : "smartBox_ea3778399e77eeb4b1de318552b18d24",
    "time" : 1743479900,
    "data" : {}
}
