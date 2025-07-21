import json
from pprint import pprint

def flatten_dict(d, parent_key='', tracked_keys=None, under_response=False):
  """
  Flattens a nested dictionary into a single-level dictionary and tracks keys that are descendants of specific parent keys (e.g., 'response').

  The function:
  1. Strips prefixes from keys if they match specific values (e.g., 'response', 'message').
  2. Flattens nested dictionaries and lists into a single-level dictionary using a separator ('_').
  3. Tracks keys that are descendants of the 'response' key or similar.

  Args:
      d (dict): The nested dictionary to flatten.
      parent_key (str, optional): The base key for recursion (used internally). Defaults to ''.
      tracked_keys (list, optional): A list to store tracked keys (used internally). Defaults to None.
      under_response (bool, optional): A flag to indicate if the current key is under a 'response' key (used internally). Defaults to False.

  Returns:
      tuple: A tuple containing:
          - A flattened dictionary (dict) with all nested keys flattened into a single level.
          - A set of tracked keys (set) that are descendants of specific parent keys (e.g., 'response').
  """
  sep = '_'
  strip_keys = ['response', 'message']

  if tracked_keys is None:
      tracked_keys = []

  items = []

  if isinstance(d, dict):
      for key, value in d.items():
          # Determine whether we are now under a 'response' key
          next_under_response = under_response or key == 'response'

          # Strip prefixes
          for prefix in strip_keys:
              if key.startswith(f"{prefix}{sep}"):
                  key = key[len(prefix) + len(sep):]
              elif key == prefix:
                  key = ''
          new_key = f"{parent_key}{sep}{key}" if parent_key else key

          # Recursively flatten
          if isinstance(value, dict):
              sub_dict, _ = flatten_dict(value, new_key, tracked_keys, next_under_response)
              items.extend(sub_dict.items())
          elif isinstance(value, list):
              for i, item in enumerate(value, start=1):
                  list_key = f"{new_key}{sep}{i}" if new_key else str(i)
                  sub_dict, _ = flatten_dict(item, list_key, tracked_keys, next_under_response)
                  items.extend(sub_dict.items())
          else:
              items.append((new_key, value))
              if next_under_response:
                  tracked_keys.append(new_key)

  else:
      items.append((parent_key, d))
      if under_response:
          tracked_keys.append(parent_key)

  return dict(items), set(tracked_keys)

## TESTING ##
# The following JSON strings are examples of the data provided by the IoT Box.

d1 = '''{
  "type": "command_reply",
  "version": 1,
  "session": "8ae05cc8-dee3-45c9-a72d-4a82bef84765",
  "deviceId": "smartBox_56b6440c6e7421e397737893aeb2a36f",
  "time": 1744777012,
  "response": {
    "code": 0,
    "message": {
      "spdAlert": false,
      "spdSurge": 0,
      "ardState": true,
      "ardAlert": false,
      "ardVoltage": 242,
      "ardCurrent": 160,
      "autoLight": false,
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
}'''

d2 = '''{
  "type": "command_reply",
  "version": 1,
  "session": "ec21db29-1e96-4ef7-ac7c-b59c75830cb5",
  "deviceId": "smartBox_dcbbfa35c8e5fcd179f84118a2d00254",
  "time": 1744777012,
  "response": [
    {
      "id": 1,
      "name": "port1",
      "rxByte": "363829",
      "txByte": "563446",
      "rxPacket": 1222,
      "txPacket": 1523,
      "rxError": 0,
      "txError": 0
    },
    {
      "id": 2,
      "name": "port2",
      "rxByte": "6603229",
      "txByte": "22849802",
      "rxPacket": 48755,
      "txPacket": 36213,
      "rxError": 0,
      "txError": 0
    },
    {
      "id": 3,
      "name": "port3",
      "rxByte": "0",
      "txByte": "0",
      "rxPacket": 0,
      "txPacket": 0,
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
      "rxByte": "0",
      "txByte": "0",
      "rxPacket": 0,
      "txPacket": 0,
      "rxError": 0,
      "txError": 0
    },
    {
      "id": 6,
      "name": "port6",
      "rxByte": "0",
      "txByte": "0",
      "rxPacket": 0,
      "txPacket": 0,
      "rxError": 0,
      "txError": 0
    },
    {
      "id": 7,
      "name": "port7",
      "rxByte": "0",
      "txByte": "0",
      "rxPacket": 0,
      "txPacket": 0,
      "rxError": 0,
      "txError": 0
    },
    {
      "id": 8,
      "name": "port8",
      "rxByte": "0",
      "txByte": "0",
      "rxPacket": 0,
      "txPacket": 0,
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
}'''

d3 = '''{
  "type": "command_reply",
  "version": 1,
  "session": "ec21db29-1e96-4ef7-ac7c-b59c75830cb5",
  "deviceId": "smartBox_dcbbfa35c8e5fcd179f84118a2d00254",
  "time": 1744777012,
  "response": {
    "code": 0,
    "message": {
      "dateTime": 1744805812,
      "runTime": 7925,
      "cpuUsaged": 9797,
      "memTotalSize": 246452,
      "memFreeSize": 173616,
      "memUsaged": 2955,
      "storageTotalSize": 1997240,
      "storageFreeSize": 1990896,
      "storageUsaged": 31,
      "temperature": 29,
      "humitidy": 51,
      "poeRealPower": 0
    }
  }
}'''

d4 = '''{
  "type": "command_reply",
  "version": 1,
  "session": "ec21db29-1e96-4ef7-ac7c-b59c75830cb5",
  "deviceId": "smartBox_dcbbfa35c8e5fcd179f84118a2d00254",
  "time": 1744777012,
  "response": {
    "latitude": 1.4531,
    "latitude_h": "N",
    "longitude": 103.792291,
    "longitude_h": "E",
    "altitude": 62.6,
    "altitude_u": "M"
  }
}'''

e1 = flatten_dict(json.loads(d1))
e2 = flatten_dict(json.loads(d2))
e3 = flatten_dict(json.loads(d3))
e4 = flatten_dict(json.loads(d4))

print_list = [e1, e2, e3, e4]
for i, e in enumerate(print_list, start=1):
    print(f"e{i}:")
    pprint(e[0], sort_dicts=False)
    print(f"{e[1]}\n")

