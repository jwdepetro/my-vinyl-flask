# My Vinyl Full Stack

This is a simple, full stack application that can manage a user's record collection.

## [Live Demo](http://my-vinyl.us-east-2.elasticbeanstalk.com)

This application has been built off of the following technologies.

- [Python](https://www.python.org/) as the programming language.

- [Flask](http://flask.pocoo.org/) as the application framework.

- [Docker](https://www.docker.com/) for deployment.

- [PostgreSQL](https://www.postgresql.org/) as the database.

- [Nginx](https://www.nginx.com/) as a reverse proxy web server.

- [AWS](https://aws.amazon.com/) for hosting.

- [last.fm API](https://www.last.fm/api) for querying artsits and albums.

## Development Dependencies

Since all application dependencies are virtualized through [Docker](https://www.docker.com/get-started) containers, all you need to have is [Docker](https://www.docker.com/get-started) to get started!


## Installation
```
$ git clone https://github.com/jwdepetro/my-vinyl-flask.git
$ cd my-vinyl-api
$ cp .env-example .env
$ docker-compose up
```

Navigate to `http://localhost:8080` and see your environment working!