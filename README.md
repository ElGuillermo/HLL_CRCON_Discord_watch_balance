# HLL_CRCON_Discord_watch_balance
A plugin for Hell Let Loose (HLL) CRCON (see : https://github.com/MarechJ/hll_rcon_tool)
that watches the teams players levels and display a report in a dedicated Discord channel.

![375489638-1b9f8fec-7f27-49a0-a4a7-a825fbbf174b](https://github.com/user-attachments/assets/2357b6a2-3a79-492b-8d9c-c1aaff9abf33)

> [!NOTE]
> The shell commands given below assume your CRCON is installed in `/root/hll_rcon_tool`.  
> You may have installed your CRCON in a different folder.  
>   
> Some Ubuntu Linux distributions disable the `root` user and `/root` folder by default.  
> In these, your default user is `ubuntu`, using the `/home/ubuntu` folder.  
> You should then find your CRCON in `/home/ubuntu/hll_rcon_tool`.  
>   
> If so, you'll have to adapt the commands below accordingly.

## Install
- Log into your CRCON host machine using SSH and enter these commands (one line at at time) :  

  First part (if you already have installed any other "custom tools" from ElGuillermo, you can skip this part)
  ```shell
  cd /root/hll_rcon_tool
  wget https://raw.githubusercontent.com/ElGuillermo/HLL_RCON_restart/refs/heads/main/restart.sh
  mkdir custom_tools
  cd custom_tools
  wget https://raw.githubusercontent.com/ElGuillermo/HLL_CRCON_custom_common_functions.py/refs/heads/main/common_functions.py
  wget https://raw.githubusercontent.com/ElGuillermo/HLL_CRCON_custom_common_translations.py/refs/heads/main/common_translations.py
  ```
  Second part
  ```shell
  cd /root/hll_rcon_tool/custom_tools
  wget https://raw.githubusercontent.com/ElGuillermo/HLL_CRCON_Discord_watch_balance/refs/heads/main/hll_rcon_tool/custom_tools/watch_balance.py
  wget https://raw.githubusercontent.com/ElGuillermo/HLL_CRCON_Discord_watch_balance/refs/heads/main/hll_rcon_tool/custom_tools/watch_balance_config.py
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
- Edit `/root/hll_rcon_tool/custom_tools/watch_balance_config.py` and set the parameters to fit your needs.
- Restart CRCON :
  ```shell
  cd /root/hll_rcon_tool
  sh ./restart.sh
  ```

## Limitations
⚠️ Any change to these files requires a CRCON rebuild and restart (using the `restart.sh` script) to be taken in account :
- `/root/hll_rcon_tool/custom_tools/common_functions.py`
- `/root/hll_rcon_tool/custom_tools/common_translations.py`
- `/root/hll_rcon_tool/custom_tools/watch_balance.py`
- `/root/hll_rcon_tool/custom_tools/watch_balance_config.py`

⚠️ This plugin requires a modification of the `/root/hll_rcon_tool/config/supervisord.conf` file, which originates from the official CRCON depot.  
If any CRCON upgrade implies updating this file, the usual upgrade procedure, as given in official CRCON instructions, will **FAIL**.  
To successfully upgrade your CRCON, you'll have to revert the changes back, then reinstall this plugin.  
To revert to the original file :  
```shell
cd /root/hll_rcon_tool
git restore config/supervisord.conf
```
