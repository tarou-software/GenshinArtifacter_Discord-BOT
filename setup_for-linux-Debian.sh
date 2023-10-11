#!/bin/sh

# Pythonとpipをインストール
sudo apt-get update
sudo apt-get install python3
sudo apt-get install python3-pip

# ライブラリをインストール
pip3 install discord.py
pip3 install python-dotenv
pip3 install Pillow==10.0.1
pip3 install pyyaml
pip3 install requests