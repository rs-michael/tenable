"""Module that writes / reads from vulnerabilities.json and parses it content"""
import json
from typing import Optional
import os


def write_file(data: dict) -> None:
    """Wrte the file"""
    if not os.path.isdir("data"):
        os.mkdir("data/")
    with open("data/vulnerabilities.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def read_file() -> Optional[dict]:
    """Read the file"""
    try:
        with open("data/vulnerabilities.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"vulnerabilities": []}


def compare_files(new_data, old_data) -> tuple[dict, dict]:
    """This function will compare two dictionaries to determine new issues to be open/closed"""

    new_data = {entry["plugin_name"]: entry for entry in new_data["vulnerabilities"]}
    old_data = {entry["plugin_name"]: entry for entry in old_data["vulnerabilities"]}
    new_issues_diff = set(new_data) - set(old_data)
    closed_issues_diff = set(old_data) - set(new_data)

    new_vuln = [new_data[name] for name in new_issues_diff]
    old_vuln = [old_data[name] for name in closed_issues_diff]
    return new_vuln, old_vuln
