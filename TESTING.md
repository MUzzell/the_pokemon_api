There are 5 containers overall in the docker-compose file. 4 main containers (messenger, redis, frontend, backend) and a 5th one for testing.

To run the code as it stands: $> docker-compose run frontend (frontend will bind to http://localhost:5000)
To run the integration testing container: docker-compose run testing

To run the unit tests for the backend: docker-compose run --entrypoint pytest backend
