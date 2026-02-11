"""
# CI-Server for DD2480 Group 10

A simple CI-server using GitHub webhooks to build and test this project.

The project is builds on [Flask](https://flask.palletsprojects.com/en/stable/) and uses
[Gihub commit statuses](https://docs.github.com/en/rest/commits/statuses?apiVersion=2022-11-28)
for notifications. The server is designed respond to events from a [GitHub App](https://docs.github.com/en/apps/overview)
but is also compatible with a normal webhook setup.

**Module overview**
- [main]: The main entry point of the server, responsible for setting up the Flask app and routing.
- [builder]: Contains the logic for building and testing the project.
- [models]: Defines data models for build reports and statuses.
- [input_validation]: Contains functions for validating incoming webhook payloads.
- [auth]: Handles auth construction depending on server setup.
- [ports]: Defines generic contracts for external interactions (e.g for notifications).
- [adapters]: Contains implementations of the ports defined in `ports` (e.g. GitHub notifications).
- [infra]: Contains infrastructure-related code, anything that touches the outside world should reside here.
"""
