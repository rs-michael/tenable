"""Tenable Jira integration script"""
# Built-in
import os
import json

# Libraries
import pydash as py_
import requests
from jira import JIRA
from dotenv import load_dotenv, find_dotenv

# Imports
from config import CONFIG
from io_helpers import compare_files, read_file, write_file

load_dotenv(find_dotenv())


# Get the OS variables
access_key = os.getenv("tenable_access_key")
secret_key = os.getenv("tenable_secret_key")
jira_token = os.getenv("jira_token")
jira_email = os.getenv("jira_email")

issues_cache = {}


def get_description(plugin_id: int) -> str:
    """Thie function will fetch the description for the givne plugin_id"""

    get_url = f"https://cloud.tenable.com/workbenches/vulnerabilities/{plugin_id}/info"
    headers = {
        "accept": "application/json",
        "X-ApiKeys": f"accessKey={access_key}; secretKey={secret_key}",
    }

    try:
        response = requests.get(get_url, headers=headers, timeout=15)
    except requests.exceptions.RequestException as exc:  # This is the correct syntax
        raise SystemExit("Could get vulnerabilities description") from exc

    if response.status_code == 200:
        json_response = json.loads(response.content)
        return f"""**synopsis**: {py_.get(json_response, "info.synopsis", None)}
**description**: {py_.get(json_response, "info.description", None)}
**solution**: {py_.get(json_response, "info.solution", None)}

**see_also**: [{py_.get(json_response, "info.see_also.0", None)}]({py_.get(json_response, "info.see_also.0", None)})
"""
    return {}


def configure_jira_client() -> JIRA:
    """Initialise the Jira Client"""
    domain = CONFIG.get_key("jira.url")
    return JIRA(domain, basic_auth=(jira_email, jira_token))


def process_vulnerabilities(client, issues_to_open, issues_to_close) -> None:
    """Process the vulnerabilities"""
    for each in issues_to_open:
        # Parse data
        epic_name = each["plugin_family"]
        issue_name = each["plugin_name"]
        plugin_id = each["plugin_id"]

        # Check the epics exists in local cache to prevent excessive API calls
        if epic_name not in issues_cache:
            if check_issue_exists(client, epic_name, "Task"):
                epic_id = issues_cache[epic_name]
            else:
                epic_id = create_issue(client, epic_name, "Task")
            if not check_issue_exists(client, issue_name, "Subtask"):
                description = get_description(plugin_id)
                issue_id = create_issue(client, issue_name, "Subtask", description, epic_id)
                transition_issue(client, issue_id, "In Progress")
            else:
                # This should never get here as plugin_names are unique
                pass

    for each in issues_to_close:
        issue_name = each["plugin_name"]
        key = get_issue_key(client, issue_name, "Subtask")
        transition_issue(client, key, "Done")
    check_parent_needs_closing(client)


def get_issue_key(client: JIRA, name: str, issue_type: str) -> int:
    """This funciton will check whether a jira issue exists"""

    project = CONFIG.get_key("jira.key")  # Jira board name
    jql_str = f"project='{project}' AND issuetype='{issue_type}' AND summary~'{name}'"

    new_issue = client.search_issues(jql_str=jql_str, json_result=True)
    return new_issue["issues"][0]["key"]


def check_issue_exists(client: JIRA, name: str, issue_type: str) -> int:
    """This funciton will check whether a jira issue exists"""

    project = CONFIG.get_key("jira.key")
    jql_str = f"project='{project}' AND issuetype='{issue_type}' AND summary~'{name}'"

    new_issue = client.search_issues(jql_str=jql_str, json_result=True)

    if issue_type == "Task":
        if new_issue["total"]:
            issues_cache[name] = new_issue["issues"][0]["key"]
    return new_issue["total"]


def create_issue(client: JIRA, name: str, issue_type: str, desc: list = None, issue_key=None) -> int:
    """Create a jira issue"""
    project = CONFIG.get_key("jira.key")
    issue = {
        "project": {"key": project},
        "summary": name,
        "description": desc,
        "issuetype": {"name": issue_type},
    }

    if issue_key:
        issue["parent"] = {"key": issue_key}
    new_issue = client.create_issue(fields=issue)
    return new_issue.key


def transition_issue(client: JIRA, issue_key: int, state: str) -> None:
    """This funciton will transition the state of a currently opened ticket"""

    client.transition_issue(issue_key, state)


def check_parent_needs_closing(client: JIRA) -> None:
    """This function will pull all the parents issue and check if they need closing"""
    project = CONFIG.get_key("jira.key")
    jql_str = f"project='{project}' AND issuetype='Task'"

    results = client.search_issues(jql_str=jql_str, fields=["summary", "status", "subtasks"], json_result=True)
    for task in results["issues"]:
        subtask_stats = []
        task_key = task["key"]
        for subtask in task["fields"]["subtasks"]:
            status = subtask["fields"]["status"]["name"]
            subtask_stats.append(status)

        done = len(set(subtask_stats)) == 1 and subtask_stats[0] == "Done"
        if done:
            transition_issue(client, task_key, "Done")


def get_vulnerabilities() -> dict:
    """This function will get the latest vulnerability"""

    get_url = "https://cloud.tenable.com/workbenches/vulnerabilities?"
    params = {
        "filter.0.filter": "severity",
        "filter.0.quality": "eq",
        "filter.0.value": "critical",
    }
    headers = {
        "accept": "application/json",
        "X-ApiKeys": f"accessKey={access_key}; secretKey={secret_key}",
    }

    try:
        response = requests.get(get_url, headers=headers, params=params, timeout=15)
    except requests.exceptions.RequestException as exc:  # This is the correct syntax
        raise SystemExit("Could not fulfill python request") from exc

    if response.status_code == 200:
        return json.loads(response.content)
    return False


def main() -> None:
    """Main body of program"""

    # Configurations
    CONFIG.load_config_toml()
    client: JIRA = configure_jira_client()

    # Fetch vulnerabilities
    if new_vulns := get_vulnerabilities():
        pass
    else:
        print("Could not pull vulnerabilities from Tenable")
        return

    old_vulns = read_file()
    issues_to_open, issues_to_close = compare_files(new_vulns, old_vulns)
    if not issues_to_open and not issues_to_close:
        print("No new issues")
        return
    process_vulnerabilities(client, issues_to_open[0:1], issues_to_close)
    write_file(new_vulns)


if __name__ == "__main__":
    main()
