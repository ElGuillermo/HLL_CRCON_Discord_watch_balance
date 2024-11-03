#!/bin/bash
clear
echo "Build CRCON"
echo "----------------------------------------"
cd /root/hll_rcon_tool
docker compose build
echo "Build CRCON : done."

# echo " "
# echo "Stop CRCON"
# echo "----------------------------------------"
# docker compose down
# echo "Stop CRCON : done."

echo " "
echo "Start CRCON"
echo "----------------------------------------"
docker compose up -d --remove-orphans
echo "Start CRCON : done."

echo "Clean Docker files"
echo "----------------------------------------"
docker volume rm $(docker volume ls -qf dangling=true)
# docker system prune -a -f
echo "Clean Docker files : done."

echo " "
echo "Actual CRCON size :"
du -sh /root/hll_rcon_tool/
echo "(included logs)"
du -sh /root/hll_rcon_tool/logs
echo "----------------------------------------"

echo " "
echo "Wait for a full minute before using CRCON interface"
echo " "
