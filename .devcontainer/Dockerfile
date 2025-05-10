FROM mcr.microsoft.com/devcontainers/python:3.13

# Poetry environment variables
ENV POETRY_VERSION="2.1.3" \
  POETRY_HOME=/opt/poetry \
  POETRY_VIRTUALENVS_IN_PROJECT=true
ENV PATH="$POETRY_HOME/bin:$PATH"

# Docker engine setup
RUN apt-get update \
  && apt-get install -y apt-transport-https ca-certificates curl gnupg2 lsb-release \
  && curl -fsSL https://download.docker.com/linux/$(lsb_release -is | tr '[:upper:]' '[:lower:]')/gpg | apt-key add - 2>/dev/null \
  && echo "deb [arch=$(dpkg --print-architecture)] https://download.docker.com/linux/$(lsb_release -is | tr '[:upper:]' '[:lower:]') $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list \
  && apt-get update \
  && apt-get install -y \
      docker-ce-cli \
      docker-compose-plugin \
      bash-completion

# Poetry installation
RUN curl -sSL https://install.python-poetry.org | python3 -
