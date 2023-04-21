from datetime import datetime
from pathlib import Path
from typing import List, Union


def rename_versions(location: str, version: int, ext: str, prefix: Union[str, None] = None):
    old_filename = f"{prefix}-latest" if prefix else "latest"
    current_latest_version = Path(f"{location}/{old_filename}.{ext}")
    new_filename = f"{prefix}-version-{version}" if prefix else f"version-{version}"
    renamed_file = Path(f"{location}/{new_filename}.{ext}")
    current_latest_version.rename(renamed_file)


def create_directory(root: str, ext: str, prefixes: Union[List[str], None] = None):
    current_date = datetime.now().date().isoformat()
    location = f"{root}/{current_date}"
    Path(location).mkdir(parents=True, exist_ok=True)

    divider = len(prefixes) if prefixes else 1
    version = len([file for file in Path(location).glob("*") if file.is_file()]) // divider

    if version:
        if prefixes:
            for prefix in prefixes:
                rename_versions(location, version, ext, prefix)
        else:
            rename_versions(location, version, ext)

    return location
