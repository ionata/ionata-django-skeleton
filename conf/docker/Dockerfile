FROM ubuntu:16.04
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
    python3.7 \
    python3.7-dev \
    python3.7-venv \
    build-essential \
    gettext \
    libpq-dev \
    postgresql-client \
    mysql-client \
    curl \
    # Cleaning cache:
    && apt autoremove -y && apt clean -y && rm -rf /var/lib/apt/lists/*
# Install WKHTMLTOPDF
RUN curl --show-error --location \
    https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.xenial_amd64.deb \
    --output /tmp/wkhtmltox_0.12.6-1.xenial_amd64.deb && \
    apt update && \
    apt install -y --no-install-recommends \
    /tmp/wkhtmltox_0.12.6-1.xenial_amd64.deb && \
    # Cleaning cache:
    apt autoremove -y && apt clean -y && rm -rf /var/lib/apt/lists/* && \
    rm /tmp/wkhtmltox_0.12.6-1.xenial_amd64.deb
# Install Poetry
RUN python3.7 -mvenv /usr/local/include/poetry && \
    /usr/local/include/poetry/bin/pip install poetry && \
    ln -s /usr/local/include/poetry/bin/poetry /usr/local/bin/poetry
WORKDIR /var/www
