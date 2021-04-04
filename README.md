# The books database (with sockets)

## About
Classroom project meant to understand how to work with websockets.
This project is composed by a mysql database, a client and a server. The server connects to the database and exposes it to the client. The client can request CRUD operations, such as query for a boook, update, delete, or create a new one.

## Setup info:
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
### Python version:
3.9.2

### Dependencies:
- mysql-connector-python

## How to use:
- Make sure you have installed all dependencies
- Replace the dummy credentials in server.py for your MySQL credentials
- Import the database
- Make sure `IP` and `PORT` global variables match between server.py and client.py
- Start both scripts in separate terminals

## Authors:
- [rafasilveira](https://github.com/rafasilveira)
- [lucaswmolin](https://github.com/lucaswmolin)