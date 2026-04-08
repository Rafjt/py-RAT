import platform
import socket
import getpass


def get_system_info():

    return {
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "release": platform.release(),
        "user": getpass.getuser(),
        "architecture": platform.machine(),
    }
