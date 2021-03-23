#! /bin/bash

set -ex

# This file make it easy to run the program quickly from the command line

FILENAME=input/portrait.jpg
if [ "$(whoami)" == "duncan" ]; then
  FILENAME=input/callum-1.jpg
fi

# FILENAME=input/cat.jpeg

python3 pointillism.py ${FILENAME}
