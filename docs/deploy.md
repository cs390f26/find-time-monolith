# Find a Time — Deployment

This document explains how to deploy and debug the Find a Time application on an AWS EC2 instance.

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

This is a step-by-step guide to successfully deploying the application. 

1. Navigate to the Amazon EC2 home page
2. In the left navigation pane, select "Security Groups", then "Create Security Group" 
3. Provide it the name "FindATimeGroup" and description "Allows access to port 5000" 
4. Add an inbound rule, and configure the following settings: 
    - Type = Custom TCP 
    - Port range = 5000 
    - Source type = Anywhere-IPv4
5. Create the security group 
6. Navigate to the EC2 instance panel and select "Launch Instance" 
7. Give it the name "FindATime", and under Key Pair select vockey
8. Under Network Settings, choose "Select existing security group"
9. Select "FindATimeGroup"
10. Copy the userdata.sh file, and paste it in the "User data" section under Advanced Details
11. Launch the instance
12. Navigate to the Elastic IPs panel, and select your Elastic IP
13. Under actions, select "Associate Elastic IP Address" 
14. Under Instances, select the FindATime instance, then associate it 
15. Open a new browser window, type in `YOUR_USERNAME_HERE`.moraviancs.click:5000

NOTE: It may take several minutes before the application is fully up and running. If it does not work after 5 minutes, refer to the Troubleshooting section. 

## Troubleshooting

These are the steps to check if the application has any issues while launching or running. 

Firstly, confirm the instance is running. 
    - This can be checked on the "Instances" panel in the AWS EC2 space
    - If it is not running, wait, and periodically refresh the instnce information until it is

To check if the webpage is accessible, use: 
    - `curl 'YOUR USERNAME HERE'.moraviancs.click:5000`
    - If this is successful, but you cannot access the application from your browser, the issue is most likely with your browser 
    - If this does not work, it is most likely an issue with your security group configuration 

To use the following commands, you must SSH to your EC2 instance. Type `ssh -i ~/.ssh/labsuser.pem ec2-user@'YOUR URL/INSTANCE IP ADDRESS'` into a terminal window. 

To view the output logs from the userdata.sh file, use: 
    - `sudo less /var/log/cloud-init-output.log`
    - This will tell you if/where the userdata failed during launch 

To confirm the database is running, use: 
    - `sudo systemctl status find-a-time-db.service`
    - If it is not running, attempt to manually restart it
    - `sudo systemctl restart find-a-time-db.service`

To view the logs for the database, use: 
    - `sudo journalctl -u find-a-time-db.service` 
    - If the database is having an issue, this will help you with correcting the issue

To confirm the web server is running, use: 
    - `sudo systemctl status find-a-time-web.service`
    - If it is not running, attempt to manually restart it
    - `sudo systemctl restart find-a-time-web.service`

To view the logs for the web application, use: 
    - `sudo journalctl -u find-a-time-web.service` 
    - If the application is having an issue, this will help you with correcting the issue


## Userdata Script

The `userdata.sh` script automates the deployment of the new EC2 instance. 

It is responsible for the following tasks:

- installing git, python 3.12, pip, Java 17, and DynamoDB local
- obtaining the application code from GitHub
- installing Python dependencies in a .venv
- preparing and running DynamoDB 
- configuring the application
- installing the systemd service files for the application and DynamoDB
- starting the application

## Systemd

Find a Time uses systemd to manage the application process on EC2.

The systemd service allows the application to start automatically when the EC2 instance starts.

find-a-time-db.service is for the database 
find-a-time-web.service is for the web applicaton

## Deployment Verification

After deployment, you can use the following commands to verify the application is running. 

- To verify the web page is accessible, use: `curl 'YOUR USERNAME HERE'.moraviancs.click:5000`
- To verify the database is running, use: `sudo systemctl status find-a-time-db.service` when connected to your EC2 instance
- To verify the web application is running, use: `sudo systemctl status find-a-time-web.service`
