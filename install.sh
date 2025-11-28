#!/bin/bash

# Installer distutils pour éviter les erreurs de build
apt-get update
apt-get install -y python3-distutils
pip install --upgrade setuptools
pip install numpy==1.24.4
