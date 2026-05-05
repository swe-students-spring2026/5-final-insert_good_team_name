# Final Project

[![linting](https://github.com/swe-students-spring2026/5-final-insert_good_team_name/actions/workflows/lint.yml/badge.svg)](https://github.com/swe-students-spring2026/5-final-insert_good_team_name/actions/workflows/lint.yml)
[![webapp tests](https://github.com/swe-students-spring2026/5-final-insert_good_team_name/actions/workflows/test-webapp.yml/badge.svg)](https://github.com/swe-students-spring2026/5-final-insert_good_team_name/actions/workflows/test-webapp.yml)
[![matching service tests](https://github.com/swe-students-spring2026/5-final-insert_good_team_name/actions/workflows/test-matching-service.yml/badge.svg)](https://github.com/swe-students-spring2026/5-final-insert_good_team_name/actions/workflows/test-matching-service.yml)

An exercise to put to practice software development teamwork, subsystem communication, containers, deployment, and CI/CD pipelines. See [instructions](./instructions.md) for details.

**Deployed app:** [http://137.184.194.187:3000/](http://137.184.194.187:3000/)

## Team Members
- [Lily](https://github.com/lilylorand)
- [Sunil](https://github.com/SunilParab)
- [Calvin](https://github.com/CalvinPun)
- [Sean](https://github.com/seankimh)
- [Sara](https://github.com/SaraD-666)

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
