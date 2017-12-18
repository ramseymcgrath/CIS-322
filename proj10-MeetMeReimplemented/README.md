# proj10-MeetMe
CIS 322 Final Project

## Introduction
Uses Google's API for auth, and calendar handling, also supports sending invites via Gcal. 
Has a small SQLite server to save some user and meeting info for quick info

## Recent changes
Updated imports to make sure it runs accross all platforms, there were issues with this during testings

## Possible issues
The friends configuration isn't completely finished yet. Inviting users to meetings should work, but the request for calendar access and the viewing of calendars for other users is not completely tested. The DB tables and methods exist, but the UI flow isn't fully working. 2 test accounts are also needed which makes verification harder.

## Running
Make sure your port (if you decide to change it) is added to your client_secrets file, and that you've included https in your callback URLs. Don't worry, its only a built in cert for running flask locally! You can disable it by just unselecting the TRANSPORT_SECURE option in the configs

## Thanks to
Thanks to patterns established in the flask examples, and the google API documentation and examples. 

## Dockerfile
To run the dockerfile, just be sure to change python to python3
