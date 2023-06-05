import argparse
import requests
from requests.auth import HTTPBasicAuth
import json
import os
import platform

# Helpfull explanation on how to format custom fields https://community.atlassian.com/t5/Jira-Software-articles/How-to-set-select-lists-single-multiple-cascading-radio-or/ba-p/1686871

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
    parser = argparse.ArgumentParser(
        description="Create Jira issues from user defined or generated templates")
    parser.add_argument('--createIssue', type=str,
                        help="Create an issue from a template, value should be a file path to the template")
    parser.add_argument("--createTemplate", type=str,
                        help="Create a template from an issue, value should be an issue name")

    parser.add_argument('--verbose', type=bool, help="print debug information")

    parser.add_argument("--destination", type=str,
                        help="destination location for create templates")
    args = parser.parse_args()

    if not check_env_vars():
        exit()
    if args.createTemplate is not None:
        if args.destination is not None:
            create_template_from_issue(
                str(args.createTemplate), args.verbose, args.destination)
        else:
            print("Destination flag not set outputting into current dir")
            create_template_from_issue(str(args.createTemplate), args.verbose)

    if args.createIssue is not None:
        body = load_issue_template(str(args.createIssue), args.verbose)
        create_issue(body)


def check_env_vars():
    base_url = os.environ.get("jira_host")  # "https://hamisht.atlassian.net"
    api_key = os.environ.get("jira_api_key")

    found = True

    if base_url is None:
        print("err could not find  `jira_host` environment var")
        found = False

    if api_key is None:
        print("err could not find `jira_api_key` environment var")
        found = False

    return found


def load_issue_template(name, verbose):
    with open(name) as json_file:
        # load the json data
        data = json.load(json_file)

        if verbose:
            print("\n template data:")
            print(json.dumps(data,
                             sort_keys=True, indent=4, separators=(",", ": ")))
            print("processing the data")

        body = data.copy()

        # ----process the data----

        if data["type"] == "custom":
            # get the project name from template
            issue_project_name = data["fields"]["project"]["id"]

            project_id = ""
            createmeta = get_info(createmeta_url, verbose)

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
            fields = get_info(fields_url, verbose)
            editmeta = get_info(editmeta_url, verbose)
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

        if verbose:
            print("\n final processed data:")
            print(json.dumps(body,
                             sort_keys=True, indent=4, separators=(",", ": ")))

        return body


def create_template_from_issue(issue_name, verbose, destination=""):
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

    issue_data = get_info(issue_url + "/" + issue_name, verbose)

    if verbose:
        print("\n raw issue data:")
        print(json.dumps(issue_data,
                         sort_keys=True, indent=4, separators=(",", ": ")))
        print("processing data")

    print(f"Creating template of issue {issue_name}")

    if "fields" not in issue_data:
        print("Issue does not exist, response:")
        print(issue_data)
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
    file_path = destination+issue_name+".json"

    if verbose:
        print("\n processed data")
        print(json.dumps(new_issue,
                         sort_keys=True, indent=4, separators=(",", ": ")))

    # Open the file in write mode
    with open(file_path, 'w') as json_file:
        # Write the JSON data to the file
        json.dump(new_issue, json_file)

    print(f"Created clone of issue {issue_name} into file {file_path}")
    return True


def get_info(url, verbose):
    response = requests.request(
        "GET",
        base_url+url,
        headers=headers,
        auth=auth,
    )
    if verbose:
        print("\ngetting data from url:")
        print(base_url+url)
        print("\nresponse data:")
        print(json.dumps(json.loads(response.text),
                         sort_keys=True, indent=4, separators=(",", ": ")))

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
