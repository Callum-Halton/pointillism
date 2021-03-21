#! /bin/bash

set -ex

# This file make it easy to run the program quickly from the command line

FILENAME=bros.png
if [ "$(whoami)" == "duncan" ]; then
  FILENAME=cat.jpeg
fi

# FILENAME=cat-large.jpeg

python3 pointillism.py ${FILENAME}
