# Find a Time — Development Setup

This document explains how to set up and run the Find a Time application in a local development environment.

## Prerequisites

Before starting, make sure the following are installed:

- Python 3
- pip
- Git

Additional AWS and DynamoDB requirements will be documented as the project is implemented.

## Clone the Repository

Clone the project repository:

    git clone https://github.com/cs390f26/find-time-monolith.git

Move into the project directory:

    cd find-time-monolith

## Install the Project

Install the required dependencies:

    pip install -r requirements.txt

Install the project as an editable Python package:

    pip install -e .

The editable install allows changes made in the source code to be used without reinstalling the package after every edit.

## Run Tests

Run the automated tests with:

    pytest

## Application Setup

Instructions for configuring DynamoDB, loading sample data, and starting the application will be added as those parts of the implementation are completed.
