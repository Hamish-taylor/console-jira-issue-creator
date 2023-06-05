# A Console based jira issue creator
## Features
There are currently only two functions of the application
1. Create templates from an issue
2. Create an issue from a template

Templates are a Json representation of a issue, after creating one from an issue you can modify it to change the fields and data, you can also write your own template (this was the original intention) however creating one from an issue is far easier so it is **highly** recommended you do not try and write it yourself.

## **Note** For the application to work you need to set two environment variables
- `jira_host` (The host url of your jira board. Example: https://yourname.atlassian.net/)
- `jira_api_key` (Your jira api key)

# Usage
There are two main ways to use the application
## **`main.py`**
This will start a cmd interactive application that you can use to create issues and templates. Annoyingly this relys on there being a '/issues/' directory in the same location as the python file. this directory is used to store all of your templates.

## `jira.py` or `jira.exe` 
**Note** the exe allows you to add the application to your path. You can build the exe from source using `pyinstaller`

This python file used command line arguments to achieve the same effect as `main.py`. use -h to see all of them and their descriptions.
The main difference between this and `main.py` is that this does not rely on the existence of the '/issues/' directory. instead you use full path names or relative path names.
Example usage
`jira --createTemplate ISSUE-1 --destination <PATH_TO_SAVE_TEMPLATE>`
`jira --createIssue <PATH_OF_SAVED_TEMPLATE>`
