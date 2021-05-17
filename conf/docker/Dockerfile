FROM ubuntu:20.04
# Set environment variables
ENV \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONPATH=/var/www/src/ \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry'
# Add deadsnakes ppa
RUN apt update && \
    apt install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa
# System deps
RUN apt update && \
    apt install --no-install-recommends -y \
    # core
    curl \
    build-essential \
    g++-10 \
    git \
    locales \
    # python
    python3.7 \
    python3.7-dev \
    python3.7-distutils \
    python3.7-venv \
    # image processing
    libjpeg-dev \
    zlib1g-dev \
    # postgres
    postgresql-client \
    binutils \
    gdal-bin \
    libpq-dev \
    libproj-dev \
    libgeos-dev \
    postgis \
    # Cleaning cache:
    && apt autoremove -y && apt clean -y && rm -rf /var/lib/apt/lists/*
# Install Poetry
RUN python3.7 -mvenv /usr/local/include/poetry && \
    /usr/local/include/poetry/bin/pip install poetry && \
    ln -s /usr/local/include/poetry/bin/poetry /usr/local/bin/poetry
WORKDIR /var/www

# Copy only requirements, to cache them in docker layer
COPY ./poetry.lock ./pyproject.toml /var/www/

# Project initialization:
RUN python3.7 -mvenv /var/www/.venv && poetry install --no-interaction --no-ansi
