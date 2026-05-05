# DinnerMeet
Making friends as an adult is hard!

DinnerMeet is a web app that connects users with local, user-hosted events, making it easy to build friendships and meaningful connections in a low-pressure, welcoming environment. 

[![Lint](https://github.com/swe-students-spring2026/5-final-insert_good_team_name/actions/workflows/lint.yml/badge.svg)](https://github.com/swe-students-spring2026/5-final-insert_good_team_name/actions/workflows/lint.yml)
[![Webapp Tests](https://github.com/swe-students-spring2026/5-final-insert_good_team_name/actions/workflows/test-webapp.yml/badge.svg)](https://github.com/swe-students-spring2026/5-final-insert_good_team_name/actions/workflows/test-webapp.yml)
[![Matching-Service Tests](https://github.com/swe-students-spring2026/5-final-insert_good_team_name/actions/workflows/test-matching-service.yml/badge.svg)](https://github.com/swe-students-spring2026/5-final-insert_good_team_name/actions/workflows/test-matching-service.yml)
[![Deploy](https://github.com/swe-students-spring2026/5-final-insert_good_team_name/actions/workflows/deploy.yml/badge.svg)](https://github.com/swe-students-spring2026/5-final-insert_good_team_name/actions/workflows/deploy.yml)


- Live app: [http://137.184.194.187:3000/](http://137.184.194.187:3000/)

## Team Members

- [Lily](https://github.com/lilylorand)
- [Sunil](https://github.com/SunilParab)
- [Calvin](https://github.com/CalvinPun)
- [Sean](https://github.com/seankimh)
- [Sara](https://github.com/SaraD-666)

## Container Images (DockerHub)



- Webapp image: [link](https://hub.docker.com/r/calvinpun/dinnermeet-webapp)
- Matching-service image: [link](https://hub.docker.com/r/calvinpun/dinnermeet-matching-service)
- MongoDB image: [link](https://hub.docker.com/_/mongo)

## System Architecture (Subsystems)

- `webapp`: Flask web UI + API + SocketIO
- `matching-service`: Flask microservice for event ranking/matching logic
- `mongodb`: MongoDB persistence layer

All services run together with Docker Compose.

## Environment Configuration

1. Copy the example file:
   - `cp .env.example .env`
2. Edit `.env` and set real values:
   - `MONGO_URI=...` (your MongoDB Atlas URI or local Mongo URI)
   - `SECRET_KEY=...` (long random secret for Flask sessions)
   - `MATCHING_SERVICE_URL=http://matching-service:5001` (keep this value when using Docker Compose)

Important:
- Use `MONGO_URI` exactly (not `MONGODB_URI`).
- Do not add spaces around `=` in `.env`.
- Keep `.env` out of version control.

## Run the Project Locally

1. Build and start all services:
   - `docker compose up --build -d`
2. Verify running containers:
   - `docker compose ps`
3. Open the app:
   - [http://localhost:3000](http://localhost:3000)
5. Stop the containers:
   - `docker compose down`

## CI/CD

- Lint workflow: checks Compose config, Black, Pylint, and syntax
- Subsystem test workflows:
  - Webapp tests
  - Matching-service tests
- Deploy workflow:
  - Runs on push to `main` (and manual trigger)
  - SSHes into the DigitalOcean droplet
  - Pulls latest `main` and runs `docker compose up -d --build`

## Notes

- Example secret configuration file is included as `.env.example` with dummy values.
- Deployment secrets for GitHub Actions are configured in repository secrets (`DO_HOST`, `DO_USER`, `DO_SSH_KEY`).
