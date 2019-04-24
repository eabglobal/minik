#!/usr/bin/env bash

echo "Starting to package $1"

mkdir lambda
# Requirements file specified in the manifest will ALWAYS be in this path!
requirements="common/requirements.txt"
zip_path="$(which zip)"

if [ ! $zip_path ]; then
    echo "Unable To Package - This docker image does not have the zip command."
    echo "Try using a docker image from lambci/lambda:build-python<py_version>"
    exit 1
fi

if [ ! -f $requirements ]; then
    : # Do nothing! The use does not need to specify a requirements.txt file.
else
    echo "pip install -r requirements.txt"
    pip install -q -t lambda -r ${requirements}
fi

cp -r common/* lambda/

# Exclude non essential files and folders from the deployment package.
find lambda -type f -name "requirements.txt"   -delete
find lambda -type f -name "manifest.yml"       -delete
find lambda -type f -name "setup.cfg"          -delete
find lambda -type f -name "*.py[co]"           -delete
find lambda -type d -name "__pycache__"        -delete
find lambda -type d -name ".juni"             -exec rm -rf {} +
find lambda -type d -name "tests"              -exec rm -rf {} +
find lambda -type d -name "features"           -exec rm -rf {} +
find lambda -type d -name "*.dist-info*"       -exec rm -rf {} +
find lambda -type d -name "*.egg-info*"        -exec rm -rf {} +

# python -m compileall -q lambda
cd lambda
zip -q -9r "../dist/$1.zip" .

echo 'Finished packaging'