# check_waybar_tray
A simple python 3 script and systemd service file to check if waybar is connected to org.kde.StatusNotifierWatcher. Refer  [#3468 issue](https://github.com/Alexays/Waybar/issues/3468#issuecomment-2262074645) for more background information. 

## WARNING 
_This script is highly experimental and may be unstable or unreliable. Before using this script, ensure you have taken appropriate measures to safeguard your data and systems, such as creating backups and testing in a controlled environment. Proceed with caution and use at your own discretion._

## Info
- There are three files : a python script `check_waybar_tray.py` and systemd system template unit `check_waybar_tray@.service` and a systemd user service file `check_waybar_tray.service`
- `check_waybar_tray.py` : Python script which first checks if waybar is running. If waybar is running, then it check for the owner/connected process of `org.kde.StatusNotifierWatcher` D-bus service. If the process is not `waybar`, then it kills the process owning (or connected to) `org.kde.StatusNotifierWatcher`.
- `check_waybar_tray@.service` : Template service file that acts a proxy to run the user service file after suspend resume. We need this as we are using `suspend.target`, which further calls `sleep.target` which is specific to system services [Ref 1]. If `check_waybar_tray.py` is directly called from this service, its runs with root privilege which causes an issue with getting the SessionBus [Ref 4]. To circumvent this, we can either run the python script as root and then use `setuid` to target user UID and then call  `dbus.bus.BusConnection` with the socket address for the target user, or we can create a proxy template service file which furthers calles a user service file [Ref 4]. The latter approach has been used here. 
- `check_waybar_tray.service` : User service that runs the `check_waybar_tray.py`.

## Installation
1. Clone the git repository anywhere you want. Lets assume it is /home/_USER_/Documents, where USER is your username.
```
cd ~/Documents/
git clone https://github.com/ShikharArvind/check_waybar_tray.git
```
2. Install the required python3 packages : `dbus-python`, `psutils`. For Arch users, all are available in the repo, install them from there and not pip. 
3. Test run the python file to see if everything is working fine.
```
cd ~/Documents/check_waybar_tray
python3 check_waybar_tray.py
```
4. Edit the following line in `check_waybar_tray.service` to add the right path for the `check_waybar_tray.py` file.
```
ExecStart=python3 %h/Documents/check_waybar_tray/check_waybar_tray.py
```
4. Copy the `check_waybar_tray@.service` to `/etc/systemd/system/`
```
sudo cp check_waybar_tray@.service /etc/systemd/system/
```
5. Reload systemd daemon
```
sudo systemctl daemon-reload
```
6. Enable the `check_waybar_tray@.service`.
```
sudo systemctl enable check_waybar_tray@USER.service # Replace USER with username
```
7. Copy the `check_waybar_tray.service` to `~/.config/systemd/user/`
```
cp check_waybar_tray.service ~/.config/systemd/user/
```
8. Suspend. resume and check logs using :
``` 
systemctl --user status check_waybar_tray.service
```

## References
1. https://unix.stackexchange.com/questions/152039/how-to-run-a-user-script-after-systemd-wakeup
2. https://unix.stackexchange.com/questions/379810/find-out-the-owner-of-a-dbus-service-name
3. ChatGPT and Google Gemini to help me get started.
4. https://stackoverflow.com/questions/71425861/connecting-to-user-dbus-as-root