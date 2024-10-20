#!/bin/bash
clear
echo "Build new CRCON"
echo "----------------------------------------"
cd /root/hll_rcon_tool
docker compose build
echo "Done."

# echo " "
# echo "Stopping CRCON"
# echo "----------------------------------------"
# docker compose down
# echo "Done."

echo " "
echo "Start new CRCON"
echo "----------------------------------------"
docker compose up -d --remove-orphans
echo "Done."

# echo "Cleaning"
# echo "----------------------------------------"
# docker volume rm $(docker volume ls -qf dangling=true)
# docker system prune -a -f

echo " "
echo "Actual CRCON size :"
du -sh /root/hll_rcon_tool/
echo "(included logs)"
du -sh /root/hll_rcon_tool/logs
echo "----------------------------------------"
