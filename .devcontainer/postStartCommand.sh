#!/bin/bash

# Install packages
bash -c 'poetry install --no-interaction --no-ansi -vvv'
# Set docker socket permission
sudo chown vscode /var/run/docker.sock
# Setup poetry completions
poetry completions bash | sudo tee /etc/bash_completion.d/poetry.bash-completion >/dev/null
