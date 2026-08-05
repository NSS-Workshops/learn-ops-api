# Learning Platform API

## About

This project is the API for the Learning Platform. It is a Django project using the Django REST Framework application. It integrates with the Github OAuth platform to create accounts and perform authorizations.

## Setup

Setup is handled by the automated script in the infrastructure repo learn-ops-infrastructure
Refer to the Learning Platform Infrastructure project for instructions.

## Debugging

See [DEBUG_README.md](DEBUG_README.md) for the full guide.

## Running Tests

Make sure the project is running first.

Then run tests from the `learn-ops-api` directory:

**Run all tests:**
```bash
docker compose exec api pytest
```

**Run a single test file:**
```bash
docker compose exec api pytest LearningAPI/tests/test_student_update.py

```

## Resources

- [Learning Platform API database diagram](https://dbdiagram.io/d/6005cc1080d742080a36d6d8)
