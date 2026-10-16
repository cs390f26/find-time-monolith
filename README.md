# Find-A-Time-Monolith

This is the Monolith of the Find A Time application. This means that Flask and DynamoDB are running on the same machine. 

## Description

The Find-A-Time application allows users to create events, and allows users to respond with when they are available for said event.


| Doc                                      | Contents                                                                                              |
| ---------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| [Development setup](docs/development.md) | Specifies how to run the program from scratch, such as on a personal laptop.                          |
| [Deploy](docs/deploy.md)                 | Specifies how to run the application from the AWS web interface, and how to troubleshoot the program. |


## Features

- Users can create an event, and set specific times that other users can choose from. 
- Other users can then choose the times they are available, and input their name. 
- The application then displays the number of votes for each time, and the names of the users who voted for that time. 

## Quick Start

- Clone the repository, create a virtual environment, and install the dependencies. 
- Create the .env using the example.env
- Download and start DynamoDB local
- Create the Find A Time table
- Launch the application

For a complete step-by-step walkthrough, see [Development setup](docs/development.md). 

## Contributors 

- Clannys Alvarez
- Finn Dempsey
- Joshua Jones
