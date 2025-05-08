import logging, json, time, threading
from paho.mqtt import client as mqtt_client
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.domain.write_precision import WritePrecision
from influxdb_client.client.write.point import Point

### GLOBAL VARIABLES, PARAMETERS, OBJECTS AND SETTINGS ###

lock = threading.Lock() # Mutex
stop_event = threading.Event()  # Global stop event

box_list = {} # Example key:value pair >> deviceId: [session, time]
connected_boxes = [] # Connected "deviceId"s

# connect_mqtt()
CLIENT_ID = f'python-mqtt-tcp-client'
USERNAME = 'root'
PASSWORD = 'root1234'
BROKER = 'emqx'
PORT = 1883
SUB_TOPIC = "sys/device/#"

# on_disconnect()
first_reconnect_delay = 1
reconnect_rate = 2 
max_reconnect_count = 12
max_reconnect_delay = 60   

# on_message()
default_write_precision = WritePrecision.S
url = "http://influxdb:8086"
org = "nms"
bucket = "logs"
token = "root1234"
database = InfluxDBClient(url=url, token=token, org=org)
write_api = database.write_api(write_options=SYNCHRONOUS)

# publish_command_loop()
PRESET_COMMANDS = {
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

### METHODS ###

def on_connect(client, userdata, flags, rc, properties=None):
        if rc == 0 and client.is_connected():
            client.subscribe(SUB_TOPIC)
            logging.info("Connected to MQTT Broker!")
        else:
            logging.error(f'Failed to connect, return code {rc}')


def on_disconnect(client, userdata, rc, disconnect_flags, reason, properties=None):
    logging.info("Disconnected with result code: %s", rc) 

    reconnect_count = 0
    reconnect_delay = first_reconnect_delay
    
    while reconnect_count < max_reconnect_count and not stop_event.is_set():
        logging.info("Reconnecting in %d seconds...", reconnect_delay)
        time.sleep(reconnect_delay)

        try:
            client.reconnect()
            logging.info("Reconnected successfully!")
            return
        except Exception as err:
            logging.error("%s. Reconnect failed. Retrying...", err)

        reconnect_delay *= reconnect_rate
        reconnect_delay = min(reconnect_delay, max_reconnect_delay)
        reconnect_count += 1

    logging.info("Reconnect failed after %s attempts. Exiting...", reconnect_count)
    stop_event.set()


def on_message(client, userdata, msg):
    global box_list
    try:
        message = json.loads(msg.payload.decode())
        logging.debug(f"Received message: {message}")
        
        # Print data types of all fields in the received JSON message
        logging.debug("Data types of fields in the received JSON message:")
        for key, value in message.items():
            logging.debug(f"Field: {key}, Type: {type(value).__name__}")

        # Update box_list from connection request
        if message.get('type') == "connect":
            with lock:
                box_list.update({message.get('deviceId'): [message.get('session'), message.get('time')]})
            logging.info(f"New connection request from deviceId: {message.get('deviceId')}, session: {message.get('session')}, time: {message.get('time')}")
        
        # Write all command_reply messages to InfluxDB
        if message.get('type') == "command_reply":
            # Flatten the message and track keys from 'response'
            flattened_message, field_keys = flatten_dict(message)

            # Print data types of all fields in the flattened dictionary
            logging.debug("Data types of fields in the flattened dictionary:")
            for key, value in flattened_message.items():
                logging.debug(f"Field: {key}, Type: {type(value).__name__}")

            # If GPS message, send to device_locations measurement
            if 'latitude' in flattened_message:
                direction_lat = flattened_message['latitude_h']
                multiplier_lat = 1 if direction_lat == 'N' else -1
                flattened_message['latitude'] = float(flattened_message['latitude']) * multiplier_lat
                
                direction_lon = flattened_message['longitude_h']
                multiplier_lon = 1 if direction_lon == 'E' else -1
                flattened_message['longitude'] = float(flattened_message['longitude']) * multiplier_lon
                
                # Measurement name: "device_locations"
                point = Point("device_locations") \
                        .tag("deviceId", flattened_message["deviceId"]) \
                        .field("latitude", flattened_message["latitude"]) \
                        .field("longitude", flattened_message["longitude"]) \
                        .time(flattened_message["time"], write_precision=default_write_precision)
            
            else:
                # Separate tags and fields
                field_keys = field_keys - {"code"}
                tag_keys = set(flattened_message.keys()) - field_keys - {"time", "deviceId"}

                # Measurement name: ${deviceId} - each device has its own measurement
                point = Point.from_dict(flattened_message,
                                        write_precision=default_write_precision,
                                        record_measurement_key="deviceId",
                                        record_time_key="time",
                                        record_tag_keys=list(tag_keys),
                                        record_field_keys=list(field_keys))

            write_api.write(bucket=bucket, org=org, record=point)
            logging.info(f"\nWriting to InfluxDB: {point.to_line_protocol()}\n")

    except json.JSONDecodeError as e:
        logging.error(f"Failed to decode JSON payload: {e}")
    except Exception as e:
        logging.error(f"An error occurred in on_message: {e}")


def publish_connect_reply(client):
    global box_list, connected_boxes
    msg_count = 0
    while not stop_event.is_set(): 
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
                stop_event.set()
        time.sleep(2)  # Publish data to InfluxDB refresh rate

def publish_command_loop(client):
    global box_list, connected_boxes
    while not stop_event.is_set(): 
        boxes_to_process = []
        with lock:
            boxes_to_process = {box: box_list[box] for box in connected_boxes}

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
        time.sleep(2)  # Refresh rate


# InfluxDB cannot handle dictionary or list data types, need to flatten
def flatten_dict(d, parent_key='', tracked_keys=None, under_response=False):
    sep = '_'
    strip_keys = ['response', 'message']

    if tracked_keys is None:
        tracked_keys = []

    items = []

    if isinstance(d, dict):
        for key, value in d.items():
            next_under_response = under_response or key == 'response'

            for prefix in strip_keys:
                if key.startswith(f"{prefix}{sep}"):
                    key = key[len(prefix) + len(sep):]
                elif key == prefix:
                    key = ''
            new_key = f"{parent_key}{sep}{key}" if parent_key else key

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

def connect_mqtt():      
    client = mqtt_client.Client(client_id=CLIENT_ID, callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2, protocol=mqtt_client.MQTTv311)
    client.username_pw_set(USERNAME, PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    max_retries = 10
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            client.connect(BROKER, PORT, keepalive=120)
            logging.info("Connected to MQTT Broker!")
            return client
        except ConnectionRefusedError as e:
            logging.warning(f"Connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                logging.error("Max retries reached. Exiting...")
                raise
    
    return client


def run():
    time.sleep(10) # Wait for emqx to start
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s',
                        level=logging.DEBUG)
    client = connect_mqtt()
    client.loop_start()

    connect_reply_thread = threading.Thread(target=publish_connect_reply, args=(client,))
    command_loop_thread = threading.Thread(target=publish_command_loop, args=(client,))

    connect_reply_thread.start()
    command_loop_thread.start()

    try:
        while not stop_event.is_set():  # Main thread waits for stop signal
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt received. Stopping threads...")
        stop_event.set()

    connect_reply_thread.join()
    command_loop_thread.join()

    client.loop_stop()


if __name__ == '__main__':
    run()