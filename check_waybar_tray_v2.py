import dbus
import psutil
import os
import signal
import logging
from systemd import journal

# Configure logging
logging.basicConfig(
    filename='/home/shikhar/Documents/check_waybar_tray/logs.txt', # UPDATE THE PATH ACCORDINGLY, Need to use full path or else when calling from swayidle, it will log elsewhere. 
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_message(message, level=logging.INFO):
    # Log both to local file and journalctl
    logging.log(level, message)
    journal.send(message, PRIORITY=level)

def get_connection_unix_process_id(service_name):
    try:
        # Get session bus
        session_bus = dbus.SessionBus()
        # Get proxy object and interface for org.freedesktop.DBus
        dbus_obj = session_bus.get_object('org.freedesktop.DBus', '/')
        dbus_interface = dbus.Interface(dbus_obj, 'org.freedesktop.DBus')
        # Call the GetConnectionUnixProcessID method 
        pid = dbus_interface.GetConnectionUnixProcessID(service_name)
        return pid
    except dbus.DBusException as e:
        log_message(f"An error occurred: {e}", level=logging.ERROR)
        exit

def get_process_name_from_pid(pid):
    try:
        process = psutil.Process(pid)
        return process.name()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None

def check_process_running_by_name(name):
    # Iterate over all running processes
    for proc in psutil.process_iter(['pid', 'name']):
        # Check if process name matches
        if proc.info['name'] == name:
            log_message(f"{name} is running with PID {proc.info['pid']}", level=logging.INFO)
            return True
    log_message(f"{name} is not running", level=logging.INFO)
    return False

def kill_process_by_pid(pid):
    try:
        os.kill(pid, signal.SIGTERM)  # Sends SIGTERM to the process
        log_message(f"Process with PID {pid} has been terminated.", level=logging.INFO)
    except PermissionError:
        log_message(f"No permission to kill process with PID {pid}.", level=logging.ERROR)
    except Exception as e:
        log_message(f"An error occurred when trying to terminate process with PID {pid}: {e}", level=logging.ERROR)

if __name__ == "__main__":
    if check_process_running_by_name("waybar"):
        # If waybar is running, then do the further checks. 
        service_name = 'org.kde.StatusNotifierWatcher'
        log_message(f"Checking the owner process of {service_name} d-bus service...", level=logging.INFO)
        pid = get_connection_unix_process_id(service_name)
        if pid:
            process_name = get_process_name_from_pid(pid)
            log_message(f"Owner process of {service_name} is {process_name} with PID {pid}.", level=logging.INFO)
            if process_name == "waybar":
                log_message(f"Since owner is waybar, nothing to do.", level=logging.INFO)
            else:
                log_message(f"Owner process of {service_name} is {process_name} with PID {pid}. Attempting to terminate the process.", level=logging.INFO)
                kill_process_by_pid(pid)
    else:
        log_message(f"Waybar not running, nothing to do.", level=logging.INFO)
