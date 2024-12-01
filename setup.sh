#!/bin/bash

set -e 

# Define the environment name
ENVIRONMENT_NAME="workshop"
echo "Setting up the workshop enviornment"
# Create the environment from the YAML file, using the defined environment name
conda env create -f environment.yaml -n $ENVIRONMENT_NAME
echo "Environment setup for $ENVIRONMENT_NAME is complete."
