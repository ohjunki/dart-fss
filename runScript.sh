#!/bin/bash 
mkdir -p ./logFile
nohup python3 ./MainFlow.py > ./logFile/$(date +%Y%m%d-%H%I%M%S)_log &
