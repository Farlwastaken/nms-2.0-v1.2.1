# Containerized Network Management System for O2Network IoT Box

## A fully functional project built on Docker using a Python script to continuously collect data from multiple IoT Boxes, pipeline it to InfluxDB, and display live metrics on a Grafana dashboard.

This project was built from the ground up by an OneSystems Technologies (OST) intern to create a software that collects and displays live sensor and GPS data from multiple IoT Boxes simultaneously on a web-based dashboard. Future direction of this project will be continued by another employee or intern of OST to develop features such as a user permissions system, a login page, and an interactible web interface to send specific commands to the IoT Box (reboot, set fan speed, change IP address, among others). The Network Management System (NMS) is containerized application and can be run using a Docker hub. The NMS performs the following:

* Create two custom dashboards using Grafana displaying 1. sensor data and 2. map view of boxes' GPS coordinates
* Create an EMQX MQTT Broker that handles incoming and outgoing MQTT messages from the IoT Box and the Python script
* Create an InfluxDB database that creates one measurement for GPS coordinates and one measurement for every connected IoT Box
* Interact with the Iot Box's custom API to automatically establish connection handshake with IoT Box using a Python script
* Send custom commands to every connected IoT Box to receive specififc monitoring data on a custom interval using a Python script
* Publish all data to the corresponding InfluxDB measurement on a custom interval using a Python script
* Pull latest data from from InfluxDB measurements to all Grafana dashboards on a fixed refresh interval

## Basic System Architecture of the NMS
![System_Architecture](nms2/documentation/extras/System_Architecture.png)
## Entity Relationship Diagram of NMS
![ERD](nms2/documentation/extras/ERD.png)
## Class Diagram of MQTT Messages and InfluxDB Measurements
![Class_Diagram](nms2/documentation/extras/Class_Diagram.png)
## Flowchart of app-to-IoT-Box Connection Handshake
![Flowchart](nms2/documentation/extras/Flowchart.png)

### Note: you can find demo videos about how to use the application inside this repository at nms2/documentation/Demo Videos 

## How to install and run the NMS using Docker Hub

The easiest way is to read the NMS 2.0 Documentation slides and follow the Demo Videos found in the "documentation" folder, but in short:

1. Clone this project
2. Install Docker Desktop - https://www.docker.com/products/docker-desktop/
3. cd to the nms2 folder and run `docker compose up -d --build` on a terminal (Windows)
4. Open Docker Desktop and navigate to the container titled 'python_app' to view logs

## How to tweak this project for your own use

If you are from OST continuing this project, I'd encourage you to fork this project, clone it to your computer, develop new features or changes to the project, then commit your changes to a new branch in your fork. 
Branch off from the latest version branch (not the main branch) and rename your new branch as the newest version to continue the chain of branches. 
* e.g. `main` -> `v1` -> `v2` -> `v3` -> ...
* For a step-by-step GitHub user guide to continue this project as an OST collaborator, see `CHAIN_GUIDE.md`

When you have added the new branch to your fork, submit a pull request to this base repository. This way, we may compile all versions from different collaborators in OST under a single GitHub repository.

Otherwise, if you are a regular user, I'd encourage you to clone and rename this project to suit your own purposes. This NMS is built to exclusively monitor O2Network IoT Boxes, but it may serve as a good starter boilerplate for a software that monitors different IoT devices that can communicate using MQTT Protocol.

## Find a bug?

For OST collaborators, since this project won't be actively maintained by this author aside from accepting pull requests, feel free to make your changes or fixes to the new branch in your fork before submitting the pull request.
