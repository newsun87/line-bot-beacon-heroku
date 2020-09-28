#!/bin/bash
ngrok http 5000& 
sleep 3
curl -s localhost:4040/api/tunnels | awk -F"https" '{print $2}' | awk -F"//" '{print $2}' | awk -F'"' '{print $1}' > URL5000.txt
sleep 2
