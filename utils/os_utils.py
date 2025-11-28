import os


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


def scan_folder_for_all_files(path: str) -> list[str]:
    local_files = scan_folder_for_any(path)
    files = []
    for file in local_files:
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
