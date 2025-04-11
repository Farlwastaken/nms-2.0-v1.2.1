app.py Logic Flow

1. Services Start Up (Grafana, InfluxDB, EMQX, app.py)

2. app.py start [run()]
3. app.py connects to mqtt broker [client.connect]
4. device(s) send connect request
5. app.py receive connect request [client.on_message]
6. app.py send connect_reply (handshake completed) [publish_connect_reply()]
7. app.py add device(s) to box_list [publish_connect_reply()]
8. app.py send command to every device in box_list [publish_command_loop()]
9. device(s) send command_reply
10. app.py receive command_reply [client.on_message]
11. app.py write command_reply data to InfluxDB [client.on_message]
12. app.py repeats 8-11 while FLAG_EXIT false
13. FLAG_EXIT set true due to disconnect [client.on_disconnect] or due to failed connect_reply [publish_connect_reply]
14. app.py stops looping [connect_reply_thread.join(), command_loop_thread.join(), client.loop_stop()]