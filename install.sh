#!/bin/bash

echo install mkdocs-material
cd mkdocs-material
git checkout 9.5.4
pip3 install -e .

echo install other dependences
cd ..
pip3 install -r requirements.txt

echo install plugins
cd plugin
pip3 install -e .