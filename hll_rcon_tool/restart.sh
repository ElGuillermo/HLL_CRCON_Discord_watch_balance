#!/bin/bash
clear
echo "Build CRCON"
echo "----------------------------------------"
cd /root/hll_rcon_tool
docker compose build
echo "----------------------------------------"
echo "Build CRCON : done."

# echo " "
# echo "Stop CRCON"
# echo "----------------------------------------"
# docker compose down
# echo "----------------------------------------"
# echo "Stop CRCON : done."

echo " "
echo "Start CRCON"
echo "----------------------------------------"
docker compose up -d --remove-orphans
echo "----------------------------------------"
echo "Start CRCON : done."

echo " "
echo "Clean Docker files"
echo "----------------------------------------"
docker volume rm $(docker volume ls -qf dangling=true)
# docker system prune -a -f
echo "----------------------------------------"
echo "Clean Docker files : done."

echo " "
echo "----------------------------------------"
{ du -sh -0 /root/hll_rcon_tool/db_data; echo " (database)"; }
{ du -sh -0 /root/hll_rcon_tool/logs; echo " (logs)"; }
echo "------------------"
{ du -sh -0 /root/hll_rcon_tool/; echo " (CRCON total size)"; }
echo "----------------------------------------"

echo " "
echo "Wait for a full minute before using CRCON interface"
echo " "
