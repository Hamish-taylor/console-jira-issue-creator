import requests
from requests.auth import HTTPBasicAuth
import json
import os
import glob
import platform
import time
from contextlib import contextmanager

# Helpfull explanation on how to format custom fields https://community.atlassian.com/t5/Jira-Software-articles/How-to-set-select-lists-single-multiple-cascading-radio-or/ba-p/1686871

issue_template_dir = "./issues/"

base_url = os.environ.get("jira_host")

api_key = os.environ.get("jira_api_key")

issue_url = "/rest/api/3/issue"

issue_types_url = "/rest/api/3/issuetype"

fields_url = "/rest/api/3/field"

projects_url = "/rest/api/3/project/search"

createmeta_url = "/rest/api/3/issue/createmeta"

editmeta_url = "/rest/api/3/issue/10000/editmeta"

fieldKey = ""
fields_options = "/rest/api/3/field/"

auth = HTTPBasicAuth("hamisht11@gmail.com", os.environ.get("jira_api_key"))

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}


def clear_console():
    # Clear console based on the operating system
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")


def main():
    # Get the issue templates
    valid = check_env_vars()
    if not valid:
        exit()

    banner = """
    Welcome to a JIRA Issue Creator!
    --------------------------------
    """

    while True:
        clear_console()
        print(banner)
        print("What would you like to do?")
        print("1. Create an issue from a template")
        print("2. Create a template from an issue")

        choice = input("Your choice (or 'q' to quit): ")

        if choice.lower() == 'q':
            exit()

        if not choice.isdigit():
            print(
                f"Error: '{choice}' is not a valid number. Please enter a number.")
            input("Press Enter to continue...")
            continue

        num = int(choice)

        if num not in [1, 2]:
            print(
                f"Error: '{choice}' is not a valid choice. Please enter 1 or 2.")
            input("Press Enter to continue...")
            continue

        if num == 1:
            while True:
                clear_console()
                print(banner)
                print("Creating an issue from a template...")
                json_files = glob.glob(os.path.join(
                    issue_template_dir, '*.json'))

                if not json_files:
                    print(
                        f"No JSON templates found in the specified directory: {issue_template_dir}")
                    input("Press Enter to go back...")
                    break

                print("Select a template to create from:")
                for i, json_file in enumerate(json_files, start=1):
                    file_name = os.path.basename(json_file)
                    print(f"{i}. {file_name}")

                print("0. Go back")

                choice = input("Your choice: ")

                if choice == '0':
                    break

                if not choice.isdigit():
                    print(
                        f"Error: '{choice}' is not a valid number. Please enter a number.")
                    input("Press Enter to continue...")
                    continue

                choice = int(choice)

                if choice not in range(1, len(json_files) + 1):
                    print(
                        f"Error: '{choice}' is not a valid choice. Please enter a valid option number.")
                    input("Press Enter to continue...")
                    continue

                selected_template = json_files[choice - 1]
                clear_console()
                print(banner)
                print(f"You have selected the template: {selected_template}")
                body = load_issue_template(
                    selected_template.split("\\")[-1])
                print("The following is the processed template:")
                print(json.dumps(body, sort_keys=True,
                      indent=4, separators=(",", ": ")))

                while True:
                    proceed = input("Do you wish to proceed (y/n)? ")

                    if proceed.lower() == 'y':
                        print(
                            f"Creating issue using template: {selected_template}")
                        create_issue(body)
                        exit_choice = input(
                            "Press 'b' to go back, or any other key to exit: ")

                        if exit_choice.lower() != 'b':
                            exit()

                        break

                    elif proceed.lower() == 'n':
                        break
                    else:
                        print("Invalid input. Please enter 'y' or 'n'.")
                        input("Press Enter to continue...")

                clear_console()
                print(banner)
        elif num == 2:
            clear_console()
            print(banner)
            print("Creating a template from an issue...")
            # Add your code for creating a template from an issue here

            correct = False

            while not correct:
                issue_name = input("Please enter the issue name to clone: ")
                template_name = input(
                    "Please enter a name for the template (leave blank to use the issue name): ")
                clear_console()
                print(banner)
                correct = create_template_from_issue(issue_name, template_name)
            exit_choice = input(
                "Press 'b' to go back, or any other key to exit: ")

            if exit_choice.lower() != 'b':
                exit()

            break

        if num in [1, 2]:
            go_back = input("Press 'b' to go back, or any other key to exit: ")
            if go_back.lower() == 'b':
                continue
            else:
                exit()


def check_env_vars():
    base_url = os.environ.get("jira_host")  # "https://hamisht.atlassian.net"
    api_key = os.environ.get("jira_api_key")

    found = True

    if base_url is None:
        print("Err could not find  `jira_host` environment var")
        found = False

    if api_key is None:
        print("Err could not find `jira_api_key` environment var")
        found = False

    return found


def load_issue_template(name):
    with open(issue_template_dir + name) as json_file:
        # Load the JSON data
        data = json.load(json_file)
        body = data.copy()

        # ----process the data----

        if data["type"] == "custom":
            # get the project name from template
            issue_project_name = data["fields"]["project"]["id"]

            project_id = ""
            createmeta = get_info(createmeta_url)

            # Get the issue type name from template
            issue_type_name = data["fields"]["issuetype"]["id"]
            issue_type_id = ""

            for i in createmeta["projects"]:
                if i["name"] == issue_project_name:
                    project_id = i["id"]

                    # set the issue type
                    for it in i["issuetypes"]:

                        if it["name"] == issue_type_name:
                            issue_type_id = it["id"]

            if project_id == "":
                print(
                    "ERR Could not find project id from name \n Make sure that the name is correct and that the project exists")

            if issue_type_id == "":
                print("ERR Could not find issue type id from name \n Make sure that the name is correct and that the issue type exists for this project")
            # Get the custom field id"s and options
            body["fields"]["project"]["id"] = project_id
            body["fields"]["issuetype"]["id"] = issue_type_id
            # process custom fields
            custom_fields = data["fields"]["customfields"]
            fields = get_info(fields_url)
            editmeta = get_info(editmeta_url)
            for custom_field in custom_fields:
                custom_field_name = custom_field
                custom_field_id = ""
                for field in fields:
                    if field["name"] == custom_field_name:
                        custom_field_id = field["id"]
                if custom_field_id == "":
                    print(
                        "ERR Could not find custom field id from name \n Make sure that the field name is correct and that the custom field exists")
                custom_field_options = editmeta["fields"][custom_field_id]["allowedValues"]
                if custom_field_id == "":
                    print(
                        f"ERR Could not find custom field id from name `{custom_field_name}` \n Make sure that the name is correct and that the custom field exists")

                body["fields"][custom_field_id] = data["fields"]["customfields"][custom_field_name]

            body["fields"].pop("customfields", None)
        return body


def create_template_from_issue(issue_name, template_name=None):
    fields_to_remove = [
        "aggregateprogress",
        "comment",
        "components",
        "created",
        "creator",
        "customfield_10018",
        "fixVersions",
        "issuelinks",
        "lastViewed",
        "priority",
        "progress",
        "status",
        "statuscategorychangedate",
        "subtasks",
        "timetracking",
        "updated",
        "versions",
        "votes",
        "watches",
        "worklog",
        "workratio",
        "issuerestriction",
        "rankAfterIssue",
        "rankBeforeIssue",
        "reporter",
        "customfield_10019"
    ]

    issue_data = get_info(issue_url + "/" + issue_name)
    print(f"Creating template of issue {issue_name}")

    if "fields" not in issue_data:
        print("Issue does not exist")
        return False

    new_issue = {
        "type": "generated",
        "fields": {}
    }

    # remove null fields
    for i in issue_data["fields"]:
        if issue_data["fields"][i] is not None:
            new_issue["fields"][i] = issue_data["fields"][i]

    # remove unnessesary fields
    for r in fields_to_remove:
        new_issue["fields"].pop(r, None)
    # save the template
    # Specify the path to the output file
    file_path = issue_template_dir+issue_name+".json"
    if template_name != "":
        file_path = issue_template_dir+template_name+".json"

    # Open the file in write mode
    with open(file_path, 'w') as json_file:
        # Write the JSON data to the file
        json.dump(new_issue, json_file)

    print(f"Created clone of issue {issue_name} into file {file_path}")
    return True


def get_info(url):
    response = requests.request(
        "GET",
        base_url+url,
        headers=headers,
        auth=auth,
    )
    return json.loads(response.text)


def create_issue(body):
    response = requests.request(
        "POST",
        base_url+issue_url,
        data=json.dumps(body),
        headers=headers,
        auth=auth
    )
    print("Succesfully created issue \n Response:")
    print(json.dumps(json.loads(response.text),
                     sort_keys=True, indent=4, separators=(",", ": ")))


if __name__ == "__main__":
    main()
