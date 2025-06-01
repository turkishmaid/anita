#!/bin/bash

which python3

# exit when "anita/venv" is not in the output of `which python3`
if [[ $(which python3) != *"anita/venv"* ]]; then
    echo "Please activate the virtual environment first."
    exit 1
fi

pip install -e ~/clonezoo/github/turkishmaid/anita