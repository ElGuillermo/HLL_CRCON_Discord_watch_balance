# HLL_CRCON_Discord_watch_balance

Unofficial plugin for the Hell Let Loose (HLL) [CRCON](https://github.com/MarechJ/hll_rcon_tool)

### Publishes the teams players levels in a dedicated Discord channel.

![HLL_CRCON_Discord_watch_balance](https://github.com/user-attachments/assets/9eb80af9-970f-421e-854a-80686f499082)

---

> [!IMPORTANT]
> - The shell commands given below assume your CRCON is installed in `/root/hll_rcon_tool`  
>   You may have installed your CRCON in a different folder.  
>   If so, you'll have to adapt the commands below accordingly.
>
> - Always copy/paste/execute commands :warning: one line at a time :warning:

## Installation

### 1/3 - Log into your CRCON host machine using SSH

- See [this guide](https://github.com/MarechJ/hll_rcon_tool/wiki/Troubleshooting-&-Help-‐-Common-procedures-‐-How-to-enter-a-SSH-terminal) if you need help to do it.

### 2/3 - Download files

- Copy/paste/execute these commands :  
  ```shell
  cd /root/hll_rcon_tool
  ```
  ```shell
  wget -N https://raw.githubusercontent.com/ElGuillermo/HLL_CRCON_restart/refs/heads/main/restart.sh
  ```
  ```shell
  mkdir -p custom_tools
  ```
  ```shell
  cd custom_tools
  ```
  ```shell
  wget -N https://raw.githubusercontent.com/ElGuillermo/HLL_CRCON_custom_common_functions.py/refs/heads/main/common_functions.py
  ```
  ```shell
  wget -N https://raw.githubusercontent.com/ElGuillermo/HLL_CRCON_custom_common_translations.py/refs/heads/main/common_translations.py
    ```
  ```shell
  wget -N https://raw.githubusercontent.com/ElGuillermo/HLL_CRCON_Discord_watch_balance/refs/heads/main/hll_rcon_tool/custom_tools/watch_balance.py
  ```
  ```shell
  wget -N https://raw.githubusercontent.com/ElGuillermo/HLL_CRCON_Discord_watch_balance/refs/heads/main/hll_rcon_tool/custom_tools/watch_balance_config.py
  ```

### 3/3 - Edit `/root/hll_rcon_tool/config/supervisord.conf`

- Add this section (wherever you want, but along with the others `[program:...]` is preferable)
  ```conf
  [program:watch_balance]
  command=python -m custom_tools.watch_balance
  environment=LOGGING_FILENAME=custom_tools_watch_balance_%(ENV_SERVER_NUMBER)s.log
  startretries=100
  startsecs=10
  autostart=true
  autorestart=true
  ```

---


## Configuration

### 1/2 - Edit `/root/hll_rcon_tool/custom_tools/watch_balance_config.py`

- Set the parameters to fit your needs (see inner comments for guidance).

### 2/2 - Rebuild and restart CRCON Docker containers

- Copy/paste/execute these commands :  
  ```shell
  cd /root/hll_rcon_tool
  ```
  ```shell
  sh ./restart.sh
  ```

> [!TIP]
> 
>  If you don't want to use the `restart.sh` script :  
>  - Copy/paste/execute these commands :  
>  ```shell
>  cd /root/hll_rcon_tool
>  ```
>  ```shell
>  sudo docker compose build && sudo docker compose down && sudo docker compose up -d --remove-orphans
>  ```

---

## Maintenance

### Disable this plugin

- Revert the changes made in [Installation 3/3](#33---edit-roothll_rcon_toolconfigsupervisordconf)

--

### Modify code or settings

:exclamation: Any change to these files requires to rebuild and restart CRCON Docker containers (same procedure as in [Configuration 2/2](#22---rebuild-and-restart-crcon-docker-containers)) :  
  - `/root/hll_rcon_tool/custom_tools/common_functions.py`
  - `/root/hll_rcon_tool/custom_tools/common_translations.py`
  - `/root/hll_rcon_tool/custom_tools/watch_killrate.py`
  - `/root/hll_rcon_tool/custom_tools/watch_killrate_config.py`

--

### Upgrade CRCON

This plugin requires a modification of original CRCON file(s).  
:exclamation: If any CRCON update contains a new version of this file(s), the usual CRCON upgrade procedure will **FAIL**.

To successfully upgrade your CRCON, you will need to undo the changes in :
- `/root/hll_rcon_tool/config/supervisord.conf`  

#### Undo the changes

- Copy/paste/execute these commands :  
  ```shell
  cd /root/hll_rcon_tool
  ```
  ```shell
  cp config/supervisord.conf config/supervisord.conf.backup
  ```
  ```shell
  git restore config/supervisord.conf
  ```

#### Upgrade

- Follow the official upgrade instructions given in the new CRCON version announcement.
- Don't restart CRCON Docker containers yet (don't execute `docker compose up -d`).

#### Reapply changes

- copy/paste the changes from  
  `/root/hll_rcon_tool/config/supervisord.conf.backup`  
  into  
  `/root/hll_rcon_tool/config/supervisord.conf`
- Rebuild and restart CRCON Docker containers (same procedure as in [Configuration 2/2](#22---rebuild-and-restart-crcon-docker-containers)).
- If everything works as intended, you can delete the backup file :
  - Copy/paste/execute these commands :  
    ```shell
    cd /root/hll_rcon_tool
    ```
    ```shell
    rm config/supervisord.conf.backup
    ```
