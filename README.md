# Learning Platform API

## About

This project is the API for the Learning Platform. It is a Django project using the Django REST Framework application. It integrates with the Github OAuth platform to create accounts and perform authorizations.

## Prerequisite: Github Organization

Your instructor needs to create a Github Organization and add you as an owner. You will then need the URL to that organization. If that hasn't been done yet, ask your instructor for the URL.

🧨 You must accept the invitation to this organization before continuing.

## Prerequisite: Personal Access Token

1. Log into your Github account
2. Go to your **Settings**
3. Click on the last item on the left navigation labeled **Developer Settings**
4. Click **Peronal access tokens**
5. Click **Tokens (classic)**
6. Click **Generate new token** dropdown
7. Choose **Generate new token (classic)**
8. In the **Note** field, enter `Learning Platform Token`
9. Set expiration to 90 days
10. Choose the following permissions
    1. `admin:org` 
    2. `admin:org_hook`
    3. `repo`
11. Click **Generate Token** button at the bottom and don't close the window as you will need the generated token below


## Getting Started

### Environment Variables Setup

1. Make sure you are in the `learningplatform` directory
2. Clone this repository
3. `cd learn-ops-api`
4. Copy the environment variable template: 
    ```shell
    cp .env.template .env
    ```
5. Open the project in VS Code and open the `.env` file
6. Set the values of the following environment variables. Do not change the values of the others.

| Key | Value |
| -- | -- |
|  LEARN_OPS_CLIENT_ID | Your instructor will share this value with you  |
|  LEARN_OPS_SECRET_KEY | Your instructor will share this value with you  |
|  LEARN_OPS_DJANGO_SECRET_KEY | Create a random string of 20-30 alphanumerical characters (*no special characters such as $%@-*)  |
|  LEARN_OPS_SUPERUSER_NAME | Create a simple username _(e.g. admin)_  |
| LEARN_OPS_SUPERUSER_PASSWORD  | Create a simple password _(e.g. password123)_  |
| SLACK_TOKEN  |  Your instructor will share this value with you |

## PAUSE: Set Up Infrastructure

🧨 Do not continue with these instructions until you have cloned and followed the instructions for the Learning Platform Client and Learning Platform Infrastructure projects. Once those are complete, and the monolith container is running, you can come back here and continue.

## Setup Continued...

### 1. Access Django Admin

1. Visit [http://localhost:8000/admin](http://localhost:8000/admin)
1. Authenticate with the superuser credentials you specified in your environment variables above.

### 2. Access the Learning Platform UI

1. Open a new browser tab
2. Visit http://localhost:8000/auth/github/url?cohort=13&v=1
3. Authorize with Github

### 3. Add yourself to Instructor role

1. Go back to the Django Admin browser tab
2. Click on **Users** in the left navigation
3. Search for your Github handle
4. Click on your user account
5. Toggle **Staff status** to be on
6. In the **Group** sections, double click **Instructor** so that it moves to the _Chosen groups_ list

### 4. Verify that you are an instructor

1. Close the browser tab that is running the Learning Platform
2. Open a new tab and visit http://localhost:3000 again
3. You should now see the instructor interface


## Resources

- [Learning Platform API database diagram](https://dbdiagram.io/d/6005cc1080d742080a36d6d8)
