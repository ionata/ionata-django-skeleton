# Ionata Django Skeleton


## Manual steps after cloning the skeleton repo
* Address all the points in this section then delete it from this file
* Rename the heading at the top of this file to be the name of the project
* Address any `TODO`s in `src/webapp/settings.py`
* Address any `TODO`s in `example.env`
* Address any `TODO`s in `pyproject.toml`


## Base Django project

Docker image for the backend is from https://gitlab.com/ionata/django-images

If you don't have access, it's basically:

* ubuntu 16.04
* install build tools:  
  `build-essential`, `g++-5`, `gettext`, `git`, `libjpeg-dev`, `locales`, `zlib1g-dev`
* install postgis requirements  
  `binutils`, `gdal-bin`, `libpq-dev`, `libproj-dev`, `libgeos-dev`, `postgis`, `postgresql-client`
* install mssql requirements  
  `msodbcsql`, `mssql-tools`, `unixodbc-dev`
* install wkhtmltopdf+libfontconfig
* install python3.7+poetry
* install nginx


## Dotenv
* Copy example.env to .env:
  - `cp example.env .env`
* Settings which will likely need to be set manually:
  - For Development:
    - `DEBUG` - set it to true
    - `SITE_URL`
    - `ADMIN_USER` - this is a development only setting
    - `AWS_S3_SECURE_URLS` - set to false if not using https during development
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
* **Important note:** Docker Compose reads `.env` files poorly. You will need to
  remove the double quotes from around the values being assigned. For example,
  - replace: `DJANGO_SETTINGS_MODULE="webapp.settings"`
  - with: `DJANGO_SETTINGS_MODULE=webapp.settings`


## Getting the project running for development
* Ensure you have Docker, docker-compose, and the above Docker image on your system.
* See the Dotenv section above and follow the steps
* From within the project start up a shell inside the backend container:
  - `docker-compose run --rm backend /bin/bash`
* While in the backend container from within `/var/www/` create the venv:
  - `python3.7 -mvenv .venv`
* Activate the venv:
  - `source /var/www/venv/bin/activate`
* Install the project requirements:
  - `poetry install`
* Run collectstatic:
  - `poetry run python /var/www/src/manage.py collectstatic --no-input`
* Migrate the database:
  - `poetry run python /var/www/src/manage.py migrate`
* Run setup_skeletons management command:
  - `poetry run python /var/www/src/manage.py setup_skeletons`
* Exit the backend Docker container:
  - `exit`
* Start the Docker containers
  - `docker-compose up -d`
* Log into minio in the browser by visiting `localhost:8000/minio`
  - username: `djangos3`
  - password: `djangos3`
* Click on the overflow menu (the three dots) next to the bucket called `django`
* Select `Edit policy` and add a policy (either `Read Only` or `Read and Write`)
