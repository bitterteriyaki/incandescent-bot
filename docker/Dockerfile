# This Dockerfile uses multi-stage build to customize DEV and PROD images:
# https://docs.docker.com/develop/develop-images/multistage-build/

FROM python:3.11.4-slim-buster AS development_build

ARG BOT_ENV \
  # Needed for fixing permissions of files created by Docker:
  UID=1000 \
  GID=1000

ENV DJANGO_ENV=${DJANGO_ENV} \
  # Python:
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PYTHONDONTWRITEBYTECODE=1 \
  # Pip:
  PIP_NO_CACHE_DIR=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PIP_DEFAULT_TIMEOUT=100 \
  # Poetry:
  POETRY_VERSION=1.3.1 \
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  POETRY_HOME='/usr/local' \
  # Tini
  TINI_VERSION=v0.19.0 \
  # Dockerize:
  DOCKERIZE_VERSION=v0.6.1

SHELL ["/bin/bash", "-eo", "pipefail", "-c"]

RUN apt-get update && apt-get upgrade -y \
  && apt-get install --no-install-recommends -y \
    bash \
    brotli \
    build-essential \
    curl \
    gettext \
    git \
    libpq-dev \
  # Installing Poetry:
  && curl -sSL 'https://install.python-poetry.org' | python - \
  && poetry --version \
  # Installing Dockerize:
  && curl -sSLO "https://github.com/jwilder/dockerize/releases/download/${DOCKERIZE_VERSION}/dockerize-linux-amd64-${DOCKERIZE_VERSION}.tar.gz" \
  && tar -C /usr/local/bin -xzvf "dockerize-linux-amd64-${DOCKERIZE_VERSION}.tar.gz" \
  && rm "dockerize-linux-amd64-${DOCKERIZE_VERSION}.tar.gz" \
  && dockerize --version \
  # installing Tini:
  && dpkgArch="$(dpkg --print-architecture | awk -F- '{ print $NF }')" \
  && curl -o /usr/local/bin/tini -sSLO "https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini-${dpkgArch}" \
  && chmod +x /usr/local/bin/tini \
  && tini --version \
  # Cleaning cache:
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && apt-get clean -y && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN groupadd -g "${GID}" -r bot \
  && useradd -d '/app' -g bot -l -r -u "${UID}" bot \
  && chown bot:bot -R '/app'

# Copy only requirements, to cache them in Docker layer.
COPY --chown=web:web ./poetry.lock ./pyproject.toml /app/

# Project initialization:
RUN --mount=type=cache,target="$POETRY_CACHE_DIR" \
  echo "$BOT_ENV" \
  && poetry version \
  && poetry run pip install -U pip \
  && poetry install \
    $(if [ "$BOT_ENV" = 'production' ]; then echo '--only main'; fi) \
    --no-interaction --no-ansi

# We need to run this script as an entrypoint:
COPY ./docker/entrypoint.sh /docker-entrypoint.sh

# Setting up proper permissions:
RUN chmod +x '/docker-entrypoint.sh'

# Running as non-root user:
USER bot

# We customize how our app is loaded with the custom entrypoint:
ENTRYPOINT ["tini", "--", "/docker-entrypoint.sh"]


FROM development_build AS production_build

COPY --chown=web:web . /app
