FROM python:3.13-slim-bookworm

WORKDIR /src

ENV PIP_NO_CACHE_DIR=false \
    PIP_DISABLE_PIP_VERSION_CHECK=true

# Poetry setup
ENV POETRY_VERSION="2.1.3" \
    POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_IN_PROJECT=true
ENV PATH="$POETRY_HOME/bin:$PATH"

# Install Poetry and clean apt cache
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    curl \
    make \
    && curl -sSL https://install.python-poetry.org | python - \
    && apt-get -y autoremove \
    && apt-get clean autoclean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENV PATH="${PATH}:${POETRY_VENV}/bin"

COPY poetry.lock pyproject.toml ./

RUN poetry install --only main

COPY . .

ENTRYPOINT ["make"]
