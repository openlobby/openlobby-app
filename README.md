# Open Lobby App

Web based application for Open Lobby - register of lobby meetings.

This application comunicates with Open Lobby Server over
[GraphQL API](http://graphql.org). The server is available in repository
[openlobby/openlobby-server](https://github.com/openlobby/openlobby-server).

## Configuration

Configuration is done by environment variables:
 - `DEBUG` - Set to any value to turn on debug mode. Don't use in production!
 - `SECRET_KEY` - long random secret string (required if not in debug mode)
 - `OPENLOBBY_SERVER_DSN` - Open Lobby Server DSN (default: `http://localhost:8010`)
 - `APP_URL` - URL where you run application (default: `http://localhost:8020`)

## Docker

Docker image is at Docker Hub
[openlobby/openlobby-app](https://hub.docker.com/r/openlobby/openlobby-app/).
It exposes web application on port 8020. You should provide it environment
variables for configuration (at least `SECRET_KEY`).

## Demo

Demo of Open Lobby with instructions is in repository
[openlobby/demo](https://github.com/openlobby/demo).

## Local run and development

You need to have Python 3 installed. Clone this repository and run:

1. `make init-env` - prepares Python virtualenv in dir `.env`
2. `source .env/bin/activate` - activates virtualenv
3. `make install` - installs requirements and application in development mode
4. `make run` - runs development server on port `8020`

Now you can use web interface at `http://localhost:8020`

Next time you can just do steps 2 and 4.

Application development server assumes that you have
[openlobby/openlobby-server](https://github.com/openlobby/openlobby-server).
running on `http://localhost:8010`. You can override this address in environment
variable `OPENLOBBY_SERVER_DSN`. E.g.
`OPENLOBBY_SERVER_DSN=http://my-server:8010 make run`

### Testing

Run: `pytest`
