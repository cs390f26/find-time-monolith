# Find a Time — Deployment

This document explains how Find a Time will be deployed to an AWS EC2 instance.

## Deployment Goal

The goal is to launch a new EC2 instance and have the application configure and start automatically with minimal manual setup.

The deployment will use:

- AWS EC2
- EC2 user data
- Python
- DynamoDB
- Gunicorn
- systemd

## EC2 Deployment Process

The planned deployment process is:

1. Create a new EC2 instance in the AWS web console.
2. Configure the required instance settings.
3. Provide the Find a Time user-data script.
4. Launch the instance.
5. Allow the user-data script to install and configure the application.
6. Allow systemd to start the application.
7. Open Find a Time in a web browser.

## User-Data Script

The `userdata.sh` script will automate the setup of a new EC2 instance.

It will eventually be responsible for tasks such as:

- installing required software
- installing Python dependencies
- obtaining the application code
- configuring the application
- preparing DynamoDB
- installing the systemd service
- starting the application

The script will be updated as the deployment process is implemented.

## systemd

Find a Time will use systemd to manage the application process on EC2.

The systemd service will allow the application to start automatically when the EC2 instance starts.

More details will be added once the service configuration is implemented.

## Deployment Verification

After deployment, we will verify that:

- the EC2 instance starts successfully
- the application starts automatically
- the database is available
- the Find a Time web interface can be opened in a browser
- the main application workflow works correctly
