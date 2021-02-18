# Ionata Django Skeleton


## Manual steps after cloning the skeleton repo
* Address all the points in this section then delete it from this file
* Rename the heading at the top of this file to be the name of the project
* Address any `TODO`s in `src/webapp/settings.py`
* Address any `TODO`s in `example.env`
* Address any `TODO`s in `pyproject.toml`


## Dotenv
* Copy example.env to .env:
  - `cp example.env .env`
* Settings which will likely need to be set manually:
  - For both:
    - `DJANGO_SETTINGS_MODULE` - usually `webapp.settings`
    - `ADMIN_USER`
  - For Development:
    - `DEBUG` - set it to true
    - `SITE_URL`
  - For production:
    - `DEBUG` - set it to false
    - `SECRET_KEY`
    - `SITE_URL`
    - `DEFAULT_FROM_EMAIL`
    - `AWS_STORAGE_BUCKET_NAME`
    - `DATABASE_URL`
    - `CELERY_BROKER_URL`
    - `MAILGUN_API_KEY`
    - `CELERY_TASK_DEFAULT_QUEUE`
    - `AXES_REDIS_URL`
    - `AXES_KEY_PREFIX`
    - `AXES_META_PRECEDENCE_ORDER`
    - `SENTRY_DSN`
* **Important note:** Docker Compose reads `.env` files poorly. You will need to
  remove the double quotes from around the values being assigned. For example,
  - replace: `DJANGO_SETTINGS_MODULE="webapp.settings"`
  - with: `DJANGO_SETTINGS_MODULE=webapp.settings`


## Getting the project running for development
* Ensure you have Docker, docker-compose on your system.
* See the Dotenv section above and follow the steps
* In the project folder, run make within the backend container:
  - `docker-compose run --rm backend make install`
* Start the Docker containers
  - `docker-compose up -d`


## Development
* Be sure to maintain and regularly run the tests within the project.
  - `docker-compose run --rm backend make test`
* Be sure to format all code before committing.
  - Ensure the pre-commit git hook is installed
    (within the environment from where git is run):
    - `pre-commit install`
  - Running `git commit` will now cause the pre-commit hook to run
    before committing is possible.
