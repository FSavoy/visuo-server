# Visuo server

This is the source code of a simplified version of the server developed for the VISUO project between the Nanyang Technological University, the Advanced Digital Sciences Center and the National Metrology Centre. It collects and stores data from sky imagers, weather stations and radiosondes, and provides a web interface for visualizing and downloading the data. It is developed in python using the django web framework.

A sample deployment is provided here (username: demo, password: demodemo): http://visuo.pythonanywhere.com/

![alt text](https://github.com/FSavoy/visuo-server/raw/master/common-static/img/screenshot.png "Interface screenshot")

## Web interface

The interface is composed of three pages:
- **Data visualization**: plots graphs of weather and radiosonde data on a daily basis and interactively plots the sky pictures captured throughout that day on a map.
- **Sky pictures**: used to filter and list images captured by the sky imagers.
- **Data downloads**: used to filter and download weather or radiosonde data in excel or matlab formats.

The django admin console ([base url]/admin) is also available for the admin user to manage users and the database.

## Organization of the source code

The source code is organized in several django apps:
- **accounts**: extends the djando admin login system to provides login pages for the web application
- **api**: REST apis for uploading data (sky pictures and weather measurements)
- **data**: contains the models for creating the database for all devices and measurements
- **downloads**: generates the download page
- **picture_browser**: generates the sky images browsing page
- **visualization**: generates the interactive data visualization page

The required packages are listed under `requirements.txt`.

## Installation

[TODO]

## Adding devices

[TODO]
