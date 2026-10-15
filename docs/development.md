# Find a Time — Development Setup

This document explains how to set up and run the Find a Time application in a local development environment.

## Prerequisites

Before starting, make sure the following are installed:

- Python 3
- pip
- Git

## Clone the Repository

Clone the project repository:

    git clone https://github.com/cs390f26/find-time-monolith.git

Move into the project directory:

    cd find-time-monolith

## Install the Project

Create a virtual environment: 

    python3 -m venv .venv

Run the virtual environment: 

    source .venv/bin/activate

Install the required dependencies:

    pip install -r requirements.txt

Install the project as an editable Python package:

    pip install -e .

The editable install allows changes made in the source code to be used without reinstalling the package after every edit.

## Run Tests

Run the automated tests with:

    pytest

## Application Setup

Set up the .env file 

    cp config/example.env .env

## DynamoDB Setup 

Make the folder for the database: 

    mkdir -p db

Install DynamoDB: 

    curl -o db/dynamodb_local_latest.zip https://s3.us-west-2.amazonaws.com/dynamodb-local/v2.x/dynamodb_local_latest.zip

Unzip the ZIP file

    unzip db/dynamodb_local_latest.zip -d db

Enter the folder: 

    cd db

Activate the database: 

    java --enable-native-access=ALL-UNNAMED -jar DynamoDBLocal.jar -sharedDb -inMemory

If you have a program running on port 8000, this will not work. 

## Create The Find A Time Table

Before doing the next steps, make sure to keep the terminal window with the database open. 
Open a second terminal window, and navigate into the find-time-monolith repo. 
Finally, reactivate the virtual environment with the same command as before. 

Create the table: 

    python scripts/create_table.py

Seed the data (This is optional, and just shows sample data):

    python scripts/seed_data.py

## Activate The Application

Activate the application:

    python -m find_a_time.app
