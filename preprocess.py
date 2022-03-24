import os
import json
from copy import deepcopy

def get_projects(folder = 'projects'):
    """ Get projects names and subfolders inside a specific root folder.

    Args:
        folder (str, optional): Defines the folder path where subfolders of projects data are located.
        In our study, each subfolder represents a project containing the activities of 
        developers in JSON format. Defaults to 'projects'.

    Returns:
        list of projects names, list of paths to projects subfolders
    """
    subfolders = [subfolder.path for subfolder in os.scandir(folder) if subfolder.is_dir()]
    names = [subfolder.name for subfolder in os.scandir(folder) if subfolder.is_dir()]
    return names, subfolders

def get_developers_activities_per_project(projects_name, projects_folder, month_range):
    """ For a specific range of months, counts the activites per month of each developer
    in a list of projects.

    Args:
        projects_name (list of strings): A list of projects names.
        projects_folder (list of strings): A list of folder paths where projects data are located.

    Returns:
        A dictionary where each key represents a project. Each project key contains a list of dictionaries,
        each representing a developer. Inside each developer dictionary, the activities per month are counted.

        Example of final output:
        {
            'vscode': {
                'John': { '201501': 1, '201502': 2} // i.e., John, who works in the vscode project, contributed 1 time in January of 2015, and 2 times in February of 2015. 
                'Martha': { '201501': 5, '201502': 6}
            }
        }
    """
    developers_activities = {}

    for project_name, project_folder in zip(projects_name, projects_folder):
        # Initialize the dictionar of developers activities for the respective project
        developers_activities[project_name] = {}

        # Gets the JSON filepaths available in the project's folder
        json_filepaths = [json_file.path for json_file in os.scandir(project_folder) if json_file.is_file()]

        # For each file, counts the number of elite events performed 
        # for each developer who worked in that month.
        for filepath in json_filepaths:
            current_month = filepath.split('_')[1].split('.')[0] # Removes project's name and .json from filename
            json_file = open(filepath, 'r', encoding='utf-8')
            json_file_rows = json_file.readlines()

            for row in json_file_rows:
                event = json.loads(row)
                elite_event_types = ['PushEvent', 'CreateEvent', 'DeleteEvent', 'GollumEvent']

                if event['type'] in elite_event_types:
                    developer = event['actor_login'] # Developer's username

                    if developer in developers_activities[project_name]:
                        developers_activities[project_name][developer][current_month] += 1
                    else:
                        # If the developer was not included in the past months, initialize
                        # its activities with the initial value of zero for each month.
                        developers_activities[project_name][developer] = dict(zip([month for month in month_range], [0] * len(month_range)))
                        developers_activities[project_name][developer][current_month] += 1

    return developers_activities

def export_developers_activities_as_csv(activities_per_project, month_range):
    headers = ['project_name', 'developer'] + month_range

    # for project in activities_per_project:
    #    for developer in project:


# In order to make KSC work, each instance must have the same range of months. 
# For this reason, we start each developer with a same dictionary of contributions per month,
# ranging from January 2015 to December 2018.
years = ['2015', '2016', '2017', '2018']
months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
month_range = []

for year in years:
    for month in months:
        month_range.append(year + month)

names, folders = get_projects()
activities_per_project = get_developers_activities_per_project(names, folders, month_range)
print(activities_per_project)
export_developers_activities_as_csv(activities_per_project, month_range)
