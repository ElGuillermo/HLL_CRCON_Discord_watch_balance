# HLL_CRCON_Discord_watch_balance

A plugin for HLL CRCON (see : https://github.com/MarechJ/hll_rcon_tool)
that watches the teams players levels.

![375489638-1b9f8fec-7f27-49a0-a4a7-a825fbbf174b](https://github.com/user-attachments/assets/2357b6a2-3a79-492b-8d9c-c1aaff9abf33)

## Install
- Create a `custom_tools` folder in CRCON's root (`/root/hll_rcon_tool/`) ;
- Copy `watch_balance.py` in `/root/hll_rcon_tool/custom_tools/` ;
- Copy `custom_common.py` in `/root/hll_rcon_tool/custom_tools/` ;
- Copy `custom_translations.py` in `/root/hll_rcon_tool/custom_tools/` ;
- Copy `restart.sh` in CRCON's root (`/root/hll_rcon_tool/`) ;
- Edit `/root/hll_rcon_tool/config/supervisord.conf` to add this bot section : 
  ```conf
  [program:watch_balance]
  command=python -m custom_tools.watch_balance
  environment=LOGGING_FILENAME=watch_balance_%(ENV_SERVER_NUMBER)s.log
  startretries=100
  startsecs=10
  autostart=true
  autorestart=true
  ```

## Config
- Edit `/root/hll_rcon_tool/custom_tools/watch_balance.py` and set the parameters to your needs ;
- Edit `/root/hll_rcon_tool/custom_tools/custom_common.py` and set the parameters to your needs ;
- Restart CRCON :
  ```shell
  cd /root/hll_rcon_tool
  sh ./restart.sh
  ```
Any change to the `/root/hll_rcon_tool/custom_tools/watch_balance.py` or `/root/hll_rcon_tool/custom_tools/custom_common.py` file will need a CRCON restart with the above command to be taken in account.
