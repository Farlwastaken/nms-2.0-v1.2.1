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
SUB_TOPIC = "sys/device/smartBox_ea3778399e77eeb4b1de318552b18d24/#"
CONNECT_REPLY_TOPIC = "sys/service/smartBox_ea3778399e77eeb4b1de318552b18d24/connect_reply"
COMMAND_TOPIC = "sys/service/smartBox_ea3778399e77eeb4b1de318552b18d24/command"

def new_connection():
    global SESSION_ID
    while True:
        query = input("Do you want to start 1. a new connection or 2. connect to a previous session_ID? (1,2)\n")
        if query == "1":
            return
        elif query == "2":
            SESSION_ID = input("Enter the session_ID to connect to: ")
            return
        else:
            print("Invalid input! Please enter 1 or 2.")

def on_connect(client, userdata, flags, rc, properties=None):
        if rc == 0 and client.is_connected():
            client.subscribe(SUB_TOPIC)
            print("Connected to MQTT Broker!")
        else:
            print(f'Failed to connect, return code {rc}')

# on_disconnect()
FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60
FLAG_EXIT = False

def on_disconnect(client, userdata, rc, disconnect_flags, reason, properties=None):
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
        global FLAG_EXIT
        FLAG_EXIT = True

# on_message()
SESSION_ID= None 
SESSION_START_TIME = None

def on_message(client, userdata, msg):
    global SESSION_ID, SESSION_START_TIME
    message = json.loads(msg.payload.decode())
    message["topic"] = msg.topic
    print(f"\n\nReceived message: {message}\n\n")
    # Check if the message is a connection request
    if message.get("type") == "connect" and SESSION_ID is None:
        SESSION_ID = message.get("session")
        SESSION_START_TIME = message.get("time")
    
    if message.get("type") == "command_reply":
        flattened_message = flatten_dict(message)
        flattened_response = {}
        flattened_data = {}
        if 'response' in message:
            flattened_response = flatten_dict(message['response'], 'response')
            flattened_message.update(flattened_response)
        if 'data' in message:
            flattened_data = flatten_dict(message['data'], 'data')
            flattened_message.update(flattened_data)

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

# publish_command()
EXIT_COMMAND_LOOP = False
COMMAND_TEMPLATE = {
    "type": "command",
    "version": 1,
    "session": None, # Add dynamically
    "deviceId": "smartBox_ea3778399e77eeb4b1de318552b18d24",
    "time": None, # Add dynamically
    "data": None # Add dynamically
}
PRESET_COMMANDS = {
    "1": {
        "name": "Fan On",
        "data": {
            "service": "slot7",
            "method": "fanConfig.set",
            "parms": {
                "autoControl": False,
                "tempThresholdOn": 40,
                "tempThresholdOff": 35,
                "fans": [{"id": 1, "speed": None, "sw": True}]
            }
        }
    },
    "2": {
        "name": "Fan Off",
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
    "3": {
        "name": "Fan Configuration",
        "data": {
            "service": "slot7",
            "method": "fanConfig.get",
            "parms": {}
        }
    },
    "4": {
        "name": "Fan Real-time Speed",
        "data": {
            "service": "slot7", 
            "method": "state",
            "parms": {}
        }
    },
    "5": {
        "name": "GPS Config",
        "data": {
            "service": "netdmate",
            "method": "mobile.gpsGet",
            "parms": {"name": "ltel"}
        }
    },
    "6": {
        "name": "Reboot Device",
        "data": {
            "service": "system",
            "method": "reboot",
            "parms": {}
        }
    }
}

def publish_connect_reply(client):
    global SESSION_ID, SESSION_START_TIME
    msg_count = 0
    while not FLAG_EXIT:
        while SESSION_ID is None:
            time.sleep(3)
            print("Waiting for connection request...")
            time.sleep(3)
        msg_dict = {
            "type" : "connect_reply",
            "version": 1,
            "session" : SESSION_ID,  # Same session as the box's connection request
            "deviceId" : "smartBox_ea3778399e77eeb4b1de318552b18d24", # Same deviceId as the box's connection request
            "time" : SESSION_START_TIME, # Same time as the box's connection request
            "response" :
            {
                "code": 0,
                "message" : "success"
            },
            # Return connection data
            "data" :
            {
            "security" : "none", # Specify key mode
            }
        }
        msg = json.dumps(msg_dict)
        if not client.is_connected():
            logging.error("publish: MQTT client is not connected!")
            time.sleep(1)
            continue

        result = client.publish(CONNECT_REPLY_TOPIC, msg, qos=1)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f'Sending connection reply...\n')
            time.sleep(2)
            break # to send one message and done
        else:
            print(f'Failed to send connection reply! Retrying...\n')
        msg_count += 1
        time.sleep(5)
        if msg_count >= 5:
            print("Failed to send connect reply message 5 times! Disconnecting...\n")
            break

def publish_command(client):
    global EXIT_COMMAND_LOOP
    while not FLAG_EXIT:
        command = COMMAND_TEMPLATE.copy()
        command["session"] = SESSION_ID
        command["time"] = int(time.time())
        command["data"] = PRESET_COMMANDS["4"]["data"].copy()
        msg = json.dumps(command)

        if not client.is_connected():
            logging.error("publish: MQTT client is not connected!")
            time.sleep(2)
            continue

        result = client.publish(COMMAND_TOPIC, msg, qos=1)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f'\nSending command to device...\n')
        else:
            print(f'\nFailed to send message to device! Please try again!\n')
        
        time.sleep(4)

### INFLUXDB WRITE ###
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.domain.write_precision import WritePrecision
from influxdb_client.client.write.point import Point

DEFAULT_WRITE_PRECISION = WritePrecision.S
url = "http://influxdb:8086"
org = "nms"
bucket = "logs"
token = "root1234"
database = InfluxDBClient(url=url, token=token, org=org)
write_api = database.write_api(write_options=SYNCHRONOUS)


# flatten_dict() function to flatten nested dictionaries for InfluxDB
def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    items.extend(flatten_dict(item, f"{new_key}{sep}{i}", sep=sep).items())
                else:
                    items.append((f"{new_key}{sep}{i}", item))
        else:
            items.append((new_key, v))
    return dict(items)

### FLASK READ FROM GRAFANA ###
from flask import Flask, request, jsonify

app = Flask(__name__)
@app.route('/grafana-command', methods=['POST'])
# Have Grafana send JSON payload to http://python:5000/grafana-command

def grafana_command():
    # message = request.get_json()
    # mqtt_client.publish(COMMAND_TOPIC, message, qos=1)
    # return jsonify({"status": "success", "message": message})

    try:
        # Get JSON payload from request
        data = request.get_json()
        
        # Check if data is received
        if not data:
            return jsonify({"error": "No JSON payload received"}), 400
        
        # Process the data (Publish to MQTT, then respond with a success message)
        mqtt_client.publish(COMMAND_TOPIC, data, qos=1)
        print("Received JSON data:", data)
        return jsonify({"message": "JSON payload received successfully", "data": data}), 200
    
    except Exception as e:
        # Handle any exceptions that occur
        return jsonify({"error": str(e)}), 500

def connect_mqtt():      
    client = mqtt_client.Client(client_id=CLIENT_ID, callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2, protocol=mqtt_client.MQTTv311)
    client.username_pw_set(USERNAME, PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, keepalive=120)
    client.on_disconnect = on_disconnect
    return client

def run():
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s',
                        level=logging.DEBUG)
    new_connection()
    client = connect_mqtt()
    client.loop_start()
    publish_connect_reply(client)
    publish_command(client)
    client.loop_stop()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    run()
