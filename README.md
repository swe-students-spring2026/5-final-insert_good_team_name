# Final Project

[![linting](https://github.com/swe-students-spring2026/5-final-insert_good_team_name/actions/workflows/lint.yml/badge.svg)](https://github.com/swe-students-spring2026/5-final-insert_good_team_name/actions/workflows/lint.yml)
[![webapp tests](https://github.com/swe-students-spring2026/5-final-insert_good_team_name/actions/workflows/test-webapp.yml/badge.svg)](https://github.com/swe-students-spring2026/5-final-insert_good_team_name/actions/workflows/test-webapp.yml)
[![matching service tests](https://github.com/swe-students-spring2026/5-final-insert_good_team_name/actions/workflows/test-matching-service.yml/badge.svg)](https://github.com/swe-students-spring2026/5-final-insert_good_team_name/actions/workflows/test-matching-service.yml)

An exercise to put to practice software development teamwork, subsystem communication, containers, deployment, and CI/CD pipelines. See [instructions](./instructions.md) for details.

## Run Locally

1. Create your env file:
   - `cp .env.example .env`
2. Edit `.env`
3. Build and start all containers:
   - `docker compose up --build -d`
4. Open:
   - Web app: [http://localhost:3000](http://localhost:3000)
5. Stop containers:
   - `docker compose down`
