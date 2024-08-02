import dbus
import psutil
import os, signal

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
        print(f"An error occurred: {e}")
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
            print(f"{name} is running with PID {proc.info['pid']}")
            return True
    print(f"{name} is not running")
    return False


def kill_process_by_pid(pid):
    try:
        os.kill(pid, signal.SIGTERM)  # Sends SIGTERM to the process
        print(f"Process with PID {pid} has been terminated.")
    except PermissionError:
        print(f"No permission to kill process with PID {pid}.")
    except Exception as e:
        print(f"An error occurred when trying terminate process with PID {pid}: {e}")

if __name__ == "__main__":
    if check_process_running_by_name("waybar") :
        # If waybar is running, then do the further checks. 
        service_name = 'org.kde.StatusNotifierWatcher'
        print(f"Checking the owner process of {service_name} d-bus service...")
        pid = get_connection_unix_process_id(service_name)
        if pid:
            process_name = get_process_name_from_pid(pid)
            print(f"Owner process of {service_name} is {process_name} with PID {pid}.")
            if process_name == "waybar":
                print(f"Since owner is waybar, nothing to do.")
            else:
                print(f"Owner process of {service_name} is {process_name} with PID {pid}. Attempting to terminate the process.")
                kill_process_by_pid(pid)
    else:
        print(f"Waybar not running, nothing to do.")
