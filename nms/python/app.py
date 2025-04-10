import logging, json, time

### MQTT READ AND WRITE ###
from paho.mqtt import client as mqtt_client

# connect_mqtt()
CLIENT_ID = f'python-mqtt-tcp-client'
USERNAME = 'root'
PASSWORD = 'root1234'
BROKER = 'emqx'
PORT = 1883

# mqtt topics
SUB_TOPIC = "sys/device/#"
box_list = {} # Example key:value pair >> deviceId: [session, time]
connected_boxes = [] # Connected "deviceId"s

# on_disconnect()
FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60
FLAG_EXIT = False

### INFLUXDB WRITE ###
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.domain.write_precision import WritePrecision
from influxdb_client.client.write.point import Point

# on_message()
DEFAULT_WRITE_PRECISION = WritePrecision.S
url = "http://influxdb:8086"
org = "nms"
bucket = "logs"
token = "root1234"
database = InfluxDBClient(url=url, token=token, org=org)
write_api = database.write_api(write_options=SYNCHRONOUS)

# publish_command_loop()
PRESET_COMMANDS = {
    "fan_on": {
        # "name": "Fan On",
        "data": {
            "service": "slot7",
            "method": "fanConfig.set",
            "parms": {
                "autoControl": False,
                "tempThresholdOn": 40,
                "tempThresholdOff": 35,
                "fans": [{"id": 1, "speed": None, "sw": True}] # Set speed before publish
            }
        }
    },
    "fan_off": {
        # "name": "Fan Off",
        "data": {
            "service": "slot7",
            "method": "fanConfig.set",
            "parms": {
                "autoControl": False,
                "tempThresholdOn": 40,
                "tempThresholdOff": 35,
                "fans": [{"id": 1, "speed": 0, "sw": True}]
            }
        }
    },
    "fan_config": {
        # "name": "Fan Configuration",
        "data": {
            "service": "slot7",
            "method": "fanConfig.get",
            "parms": {}
        }
    },
    "slot7_state": {
        # "name": "Fan Real-time Speed",
        "data": {
            "service": "slot7", 
            "method": "state",
            "parms": {}
        }
    },
    "system_state": {
        # "name": "System State",
        "data": {
        "service": "system",
        "method": "state",
        "parms": {}
        }
    },
    "gps_config": {
        # "name": "GPS Config",
        "data": {
            "service": "netdmate",
            "method": "mobile.gpsGet",
            "parms": {"name": "lte1"}
        }
    },
    "reboot": {
        # "name": "Reboot Device",
        "data": {
            "service": "system",
            "method": "reboot",
            "parms": {}
        }
    },
    "flow_monitor": {
        # "name": "Switch Port Traffic Statistics",
        "data": {
            "service": "switch.port", 
            "method": "statistics", 
            "parms": { 
            } 
        }
    }
}

### THREADING ###
import threading
lock = threading.Lock() # Mutex


def on_connect(client, userdata, flags, rc, properties=None):
        if rc == 0 and client.is_connected():
            client.subscribe(SUB_TOPIC)
            print("Connected to MQTT Broker!")
        else:
            print(f'Failed to connect, return code {rc}')


def on_disconnect(client, userdata, rc, disconnect_flags, reason, properties=None):
    global FLAG_EXIT
    logging.info("Disconnected with result code: %s", rc)
    reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
    while reconnect_count < MAX_RECONNECT_COUNT:
        logging.info("Reconnecting in %d seconds...", reconnect_delay)
        time.sleep(reconnect_delay)

        try:
            client.reconnect()
            logging.info("Reconnected successfully!")
            return
        except Exception as err:
            logging.error("%s. Reconnect failed. Retrying...", err)

        reconnect_delay *= RECONNECT_RATE
        reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
        reconnect_count += 1

    logging.info("Reconnect failed after %s attempts. Exiting...", reconnect_count)
    with lock:
        FLAG_EXIT = True


def on_message(client, userdata, msg):
    global box_list
    try:
        message = json.loads(msg.payload.decode())
        print(f"\n\nReceived message: {message}\n\n")
        
        # Update box_list from connection request
        if message.get('type') == "connect":
            with lock:
                box_list.update({message.get('deviceId'): [message.get('session'), message.get('time')]})
            print(f"New connection request from deviceId: {message.get('deviceId')}, session: {message.get('session')}, time: {message.get('time')}")
        
        # Write all command reply to InfluxDB
        if message.get('type') == "command_reply":
            flattened_message = flatten_dict(message)
            flattened_response = {}
            flattened_data = {}
            
            if 'response' in message:
                if isinstance(message['response'], list):
                    for i, item in enumerate(message['response'], start=1):
                        flattened_response.update(flatten_dict(item, f'response_{i}'))
                else:
                    flattened_response = flatten_dict(message['response'], 'response')
                flattened_message.update(flattened_response)
            
            if 'data' in message:
                flattened_data = flatten_dict(message['data'], 'data')
                flattened_message.update(flattened_data)
            
            # If GPS message, send to device_locations measurement
            if 'response_latitude' in flattened_message:
                direction_lat = flattened_message['response_latitude_h']
                multiplier_lat = 1 if direction_lat == 'N' else -1
                flattened_message['response_latitude'] *= multiplier_lat
                del flattened_message['response_latitude_h']

                direction_lon = flattened_message['response_longitude_h']
                multiplier_lon = 1 if direction_lon == 'E' else -1
                flattened_message['response_longitude'] *= multiplier_lon
                del flattened_message['response_longitude_h']
                
                point = Point("device_locations") \
                        .tag("deviceId", flattened_message["deviceId"]) \
                        .field("latitude", flattened_message["response_latitude"]) \
                        .field("longitude", flattened_message["response_longitude"]) \
                        .time(flattened_message["time"], write_precision=DEFAULT_WRITE_PRECISION)
                
            else:
                tag_keys = set(flattened_message.keys()) - set(flattened_response.keys()) - set(flattened_data.keys()) - {"time"} - {"deviceId"}
                field_keys = set(flattened_response.keys()).union(set(flattened_data.keys()))

                point = Point.from_dict(flattened_message,
                        write_precision=DEFAULT_WRITE_PRECISION,
                        record_measurement_key="deviceId",
                        record_time_key="time",
                        record_tag_keys=list(tag_keys),
                        record_field_keys=list(field_keys))

            write_api.write(bucket=bucket, org=org, record=point)
            print(f"\n\nWriting to InfluxDB: {point.to_line_protocol()}\n\n")
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON payload: {e}")
    except Exception as e:
        print(f"An error occurred in on_message: {e}")


def publish_connect_reply(client):
    global box_list, connected_boxes, FLAG_EXIT
    msg_count = 0
    while True:
        with lock:
            if FLAG_EXIT:
                break

        boxes_to_process = []
        with lock:
            for box in list(box_list): 
                if box not in connected_boxes:
                    boxes_to_process.append(box)

        for box in boxes_to_process:
            if not client.is_connected():
                logging.error("publish_connect_reply: MQTT client is not connected!")
                time.sleep(1)
                continue  

            msg_dict = {
                "type": "connect_reply",
                "version": 1,
                "session": box_list[box][0],
                "deviceId": box,
                "time": box_list[box][1],
                "response": {
                    "code": 0,
                    "message": "success"
                },
                "data": {
                    "security": "none",  # Specify key mode
                }
            }
            msg = json.dumps(msg_dict)
            CONNECT_REPLY_TOPIC = f"sys/service/{box}/connect_reply"
            result = client.publish(CONNECT_REPLY_TOPIC, msg, qos=1)
            status = result[0] 
            if status == 0:
                logging.info(f"Sent connection reply to {box}.")
                with lock:
                    connected_boxes.append(box)
                time.sleep(2)
            else:
                logging.error(f"Failed to send connection reply to {box}. Retrying...")
            msg_count += 1
            if msg_count >= 5:
                logging.error("Failed to send connect reply message 5 times! Disconnecting...")
                with lock:
                    FLAG_EXIT = True
        time.sleep(2) # Refresh rate


def publish_command_loop(client):
    global box_list, connected_boxes, FLAG_EXIT
    while True:
        with lock:
            if FLAG_EXIT:
                break

        boxes_to_process = []
        with lock:
            boxes_to_process = {box: box_list[box] for box in box_list if box in connected_boxes}

        for box in boxes_to_process:
            COMMAND_TOPIC = f"sys/service/{box}/command"
            for dashboard_section in ["slot7_state", "system_state", "flow_monitor", "gps_config"]:
                command = {
                    "type": "command",
                    "version": 1,
                    "session": boxes_to_process[box][0],
                    "deviceId": box,
                    "time": int(time.time()),
                    "data": PRESET_COMMANDS[dashboard_section]["data"]
                }
                message = json.dumps(command)

                if not client.is_connected():
                    logging.error("publish_command_loop: MQTT client is not connected! Skipping this command loop.")
                    time.sleep(2)
                    continue

                result = client.publish(COMMAND_TOPIC, message, qos=1)
                status = result[0]
                if status == 0:
                    logging.info(f"Sent {dashboard_section} command to {box}.")
                else:
                    logging.error(f"Failed to send {dashboard_section} command to {box}.")
        time.sleep(2) # Refresh rate


# InfluxDB cannot handle nested dictionaries, need to flatten
def flatten_dict(d, parent_key='', sep='_'):
    items = []
    if isinstance(d, dict):
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                for i, item in enumerate(v, start=1):
                    if isinstance(item, dict):
                        items.extend(flatten_dict(item, f"{new_key}{sep}{i}", sep=sep).items())
                    else:
                        items.append((f"{new_key}{sep}{i}", item))
            else:
                items.append((new_key, v))
    else:
        items.append((parent_key, d))
    return dict(items)


def connect_mqtt():      
    client = mqtt_client.Client(client_id=CLIENT_ID, callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2, protocol=mqtt_client.MQTTv311)
    client.username_pw_set(USERNAME, PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, keepalive=120)
    client.on_disconnect = on_disconnect
    return client


def run():
    time.sleep(5)
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s',
                        level=logging.DEBUG)
    client = connect_mqtt()
    client.loop_start()

    connect_reply_thread = threading.Thread(target=publish_connect_reply, args=(client,))
    command_loop_thread = threading.Thread(target=publish_command_loop, args=(client,))

    connect_reply_thread.start()
    command_loop_thread.start()

    while True:
        with lock:
            if FLAG_EXIT:
                break

    connect_reply_thread.join()
    command_loop_thread.join()

    client.loop_stop()


if __name__ == '__main__':
    run()