FROM nvidia/cuda:12.4.0-devel-ubuntu22.04

ENV PYTHONFAULTHANDLER=1 \
PYTHONUNBUFFERED=1 \
PYTHONHASHSEED=random \
PIP_NO_CACHE_DIR=off \
PIP_DISABLE_PIP_VERSION_CHECK=on \
PIP_DEFAULT_TIMEOUT=100 \
POETRY_NO_INTERACTION=1 \
POETRY_VIRTUALENVS_CREATE=false \
POETRY_CACHE_DIR='/var/cache/pypoetry' \
POETRY_HOME='/usr/local' \
POETRY_VERSION=1.8.2

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /code
COPY poetry.lock pyproject.toml /code/

RUN poetry install --only=main --no-interaction --no-ansi

COPY . /code

