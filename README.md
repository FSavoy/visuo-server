# Visuo server

This is the source code of a simplified version of the server developed for the VISUO project between the Nanyang Technological University, the Advanced Digital Sciences Center and the National Metrology Centre. It collects and stores data from sky imagers, weather stations and radiosondes, and provides a web interface for visualizing and downloading the data behind by a login mechanism. It is developed in python using the [django web framework](https://www.djangoproject.com/). Visualizations are coded in javascript using [d3.js](https://d3js.org/) and the [Google Maps JavaScript Api](https://developers.google.com/maps/documentation/javascript/).

A sample deployment is provided here (username: `demo`, password: `demodemo`): http://visuo.pythonanywhere.com/

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

The source code should be deployed as a standard django web app (including initializing the databse, creating the superuser, serving static and media files, ...). Please refer to the [official documentation](https://docs.djangoproject.com/en/1.11/howto/deployment/). Choose databases and media files storage strategies which scale with the amount of data that the app should store.

The following steps are also required:
- We use [django-bower](https://django-bower.readthedocs.io/en/latest/) to manage javascript packages. Run `./manage.py bower install` to download the dependencies.
- [Get a Google Maps Api key](https://developers.google.com/maps/documentation/javascript/get-api-key) and include it in the `visuo-open-source/settings.py` file.
- We use [Alligator](http://alligator.readthedocs.io/en/latest/index.html) to deal with offline tasks. Choose a queue backend and configure it according to http://alligator.readthedocs.io/en/latest/installing.html.

The superuser might use the django admin console at ([base url]/admin) to create multiple accounts for several users.

## Adding devices

### Sky imagers

[TODO]

### Weather stations

[TODO]

### Radiosondes

[TODO]

## License

This software is released under a 3-Clause BSD License. It is provided “as is” without any warranty. Users are required to obtain the licenses for the required dependencies.
