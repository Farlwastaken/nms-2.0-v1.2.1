# Network Management System for O2Network's IoT Powerlink Smart Box With Docker

## A fully functional project using a script written in Python that collects data from multiple Smart Boxes, pipelines it to InfluxDB, and displays it on a Grafana dashboard.

This project was built from the ground up by an OneSystems Technologies (OST) intern to create a software that collects and displays live sensor and gps data from multiple Smart Boxes simultaneously on a web-based dashboard. Future direction of this project will be continued by another employee of OST to develop features such as a user permissions system, a login page, and an interactible web interface to send specific commands to the Smart Box (reboot, set fan speed, change IP address, among others). The application containerized and can be run using a Docker hub. The application performs the following:

* Create two custom dashboards using Grafana displaying 1. sensor data and 2. map view of boxes' GPS coordinates
* Create an EMQX MQTT Broker that handles incoming and outgoing MQTT messages from the Smart Box and the Python script
* Create an InfluxDB database that creates one measurement for GPS coordinates and one measurement for every connected Smart Box
* Automatically establish connection handshake with Smart Box using a Python script
* Automatically send custom commands to every connected Smart Box to receive specififc data and publish all data to the corresponding InfluxDB measurement on a custom refresh interval of 2 seconds using a Python Script

## Entity Relationship Diagram of 

## Class Diagram of MQTT Messages and InfluxDB Measurements

## Flowchart of app-to-smart-box Connection Handshake

## How to install and run this Network Management Software (NMS) using Docker Hub

The easiest way is to read the NMS 2.0 Documentation slides and follow the Demo Videos found in the "documentation" folder, but in short:

1. Clone this project
2. Install Docker Desktop - https://www.docker.com/products/docker-desktop/
3. cd to the nms2 folder and run 'docker compose up -d --build' on a terminal (Windows)
4. Open Docker Desktop and navigate to the container titled 'python_app' to view logs

## How to tweak this project for your own use

If you are from OST continuing this project, I'd encourage you to fork this project, clone it to your computer, develop new features or changes to the project, then commit your changes to a new branch in your fork. 
Build off the latest branch's version and rename your new branch as the new version to continue the chain of branches. (e.g. main -> v1 -> v2 -> v-> -> ...)
When you have added the new branch to your fork, submit a pull request to this base repository. This way, we may compile all versions from different collaborators in OST under a single GitHub repository.

Otherwise, if you are a regular user, I'd encourage you to clone and rename this project to suit your own purposes. This NMS is built for monitoring IoT Powerlink Smart Boxes and not other IoT devices, but it may serve as a good starter boilerplate for a software that monitors a different set of devices that use MQTT Protocol.

## Find a bug?

For OST collaborators, since this project won't be actively maintained by this author besides accepting pull requests, feel free to make your changes or fixes to the new branch in your fork before submitting the pull request.
