import os
import socket
import subprocess
import sys
import time

import arcade

from utils.constants import IMAGE_EXTENSIONS, SOUND_EXTENSIONS, MUSIC_EXTENSIONS, FONT_EXTENSIONS


def generate_dirs(path: str) -> bool:
    try:
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        return True
    except (OSError, PermissionError) as error:
        print(f"Cannot create directories for {path}: {error}")
        return False
    except Exception as error:
        print(f"Unexpected error: {error}")
        return False


def is_valid_path(path: str) -> bool:
    return os.path.exists(path)


def scan_folder_for_any(path: str) -> list[str]:
    if not is_valid_path(path):
        return []
    files = []
    for file in os.listdir(path):
        files.append(f"{path}/{file}")
    return files


def scan_folder_for_all_files(path: str, _except: list[str] = []) -> list[str]:
    local_files = scan_folder_for_any(path)
    files = []
    for file in local_files:
        if get_file_name(file) in _except:
            continue
        if os.path.isdir(file):
            files.extend(scan_folder_for_all_files(file))
        else:
            files.append(file)
    return files


def scan_folder_for_folders(path: str) -> list[str]:
    files = scan_folder_for_any(path)
    return list(filter(lambda file: os.path.isdir(file), files))


def scan_folder_for_files(path: str) -> list[str]:
    files = scan_folder_for_any(path)
    return list(filter(lambda file: os.path.isfile(file), files))


def scan_folder_for_files_names(path: str) -> list[str]:
    files = scan_folder_for_files(path)
    return list(map(lambda f: get_file_info(f)[0], files))


def get_file_info(path: str) -> tuple[str, str, str]:
    name_with_path, ext = os.path.splitext(path)
    name = os.path.basename(name_with_path)
    return name, ext, path


def get_file_name(path: str) -> str:
    name_with_path, ext = os.path.splitext(path)
    return os.path.basename(name_with_path)


def get_extension_type(ext):
    if ext in IMAGE_EXTENSIONS:
        return 'texture'
    elif ext in SOUND_EXTENSIONS:
        return 'sound'
    elif ext in MUSIC_EXTENSIONS:
        return 'music'
    elif ext in FONT_EXTENSIONS:
        return 'font'
    else:
        return 'unknown'


def restart_self():
    def true_restart(dt):
        sys.exit()

    arcade.schedule_once(true_restart, 0)


def get_local_ip():
    try:
        hostname = socket.gethostname()
        addrs = socket.getaddrinfo(hostname, None)

        for addr in addrs:
            ip = addr[4][0]
            if isinstance(ip, str):
                if ip.startswith('26.') or ip.startswith('25.'):
                    return ip

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        return "127.0.0.1"
