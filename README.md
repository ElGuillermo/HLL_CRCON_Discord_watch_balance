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
- Restart CRCON :
  ```shell
  cd /root/hll_rcon_tool
  sh ./restart.sh
  ```

## Limitations
⚠️ Any change to these files :
- `/root/hll_rcon_tool/custom_tools/watch_balance.py` ;
- `/root/hll_rcon_tool/custom_tools/custom_common.py` ;
- `/root/hll_rcon_tool/custom_tools/custom_translations.py` ;  
...will require a CRCON restart (using `restart.sh` script) to be taken in account.

⚠️ This plugin requires a modification of the `/root/hll_rcon_tool/config/supervisord.conf` file, which originates from the official CRCON depot.  
If any CRCON upgrade implies updating this file, the usual upgrade procedure, as given in official CRCON instructions, will **FAIL**.  
To successfully upgrade your CRCON, you'll have to revert the changes back, then reinstall this plugin.  
To revert to the original file :  
```shell
cd /root/hll_rcon_tool
git restore config/supervisord.conf
```
