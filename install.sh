#!/bin/bash

echo install mkdocs-material
cd mkdocs-material
git checkout 9.2.0b0
pip3 install -e .

echo install other dependences
cd ..
pip3 install -r requirements.txt