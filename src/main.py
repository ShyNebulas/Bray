from todoist_api_python.api import TodoistAPI
from os import getenv
from dotenv import load_dotenv
from yaml import load as yamlLoad
from yaml.loader import SafeLoader
from datetime import datetime
import re
from json import load as jsonLoad
from json import dump

# Finds .env files and makes them accessible to the project
load_dotenv()
api = TodoistAPI(getenv('TODOIST_API_TOKEN'))

with open('../.config/config.yaml', 'r') as file:
    yaml = yamlLoad(file, Loader = SafeLoader)
#-----------------------------------------------------------------------------------------------------------#
def printError(content):
    print('\033[0;31m' + content + '\033[0m')

def printSuccess(content):
    print('\033[0;32m' + content + '\033[0m')

def printNeutral(content):
    print('\033[0;35m' + content + '\033[0m')
#-----------------------------------------------------------------------------------------------------------#
def isValid(task):
    if task.due == None:
        printError(f'{getContent(task)} ({task.id}) has no datetime')
        return False
    elif re.search('\[Day\s\d+\]', task.content) == None:
        printError(f'{getContent(task)} ({task.id}) has no streak counter')
        return False
    else:
        return True
#-----------------------------------------------------------------------------------------------------------#
def isDue(task):
    task_due_date = datetime.strptime(task.due.date, '%Y-%m-%d').date()
    task_due_time = datetime.strptime(task.due.datetime, '%Y-%m-%dT%H:%M:%S').time() if not task.due.datetime == None else None
    #Check if the task's date is for tomorrow
    if task_due_date > current_date: 
        return False
    #Check if the task's date is for yesterday
    elif current_date > task_due_date:
        return True
    else: 
        #Check if task has a specific time
        if task_due_time:
            #Check if task's specific time is greater then current time
            if task_due_time > current_time:
                return False
            else:
                return True
        else:
            return False
#-----------------------------------------------------------------------------------------------------------#
def getContent(task):
    return re.split('\[Day\s\d+\]', task.content)[0].strip()
#-----------------------------------------------------------------------------------------------------------#
def getStreak(task):
    streak = re.search('\[Day\s\d+\]', api.get_task(task_id = task.id).content)
    return int(streak.group().split(' ')[1][:-1])

def resetStreak(task):
    api.update_task(task_id = task.id, content = getContent(task) + ' [Day 0]')

def incrementStreak(task):
    api.update_task(task_id = task.id, content = getContent(task) + f' [Day {getStreak(task) + 1}]')
#-----------------------------------------------------------------------------------------------------------#
def updateDescription(task):
    json = openJson("json/habits.json")[str(task.id)]
    #If task has a description, update it
    if not task.description == '':
        updated_description = ''                
        for line in task.description.split('\n'):
            match line[2:line.find(':')]:
                case '**Description':
                    updated_description += line + '\n'
                case '**Created on':
                    updated_description += f'- **Created on:** {task_created_date.strftime("%d-%m-%Y")} ({abs((current_date - task_created_date).days)} days)\n'
                case '**Longest streak':
                    updated_description += f'- **Longest streak:** {json["longest_streak"]}\n'
                case '**Completion rate':
                    if json['completion_rate'] == 'N/A':
                        updated_description += '- **Completion rate:** N/A\n'
                    else:
                        updated_description += f'- **Completion rate:** {json["completion_rate"]}%\n'
        updated_description += '- **Powered by Bray \u2666**'
        api.update_task(task_id = task.id, description = updated_description)
    #Else, create a description
    else:
        description_description = '- **Description:** N/A\n'
        description_created_on = f'- **Created on:** {task_created_date.strftime("%d-%m-%Y")} ({json["created_ago"]} days)\n'
        description_longest_streak = f'- **Longest streak:** {json["longest_streak"]}\n'
        description_completion_rate = '- **Completion rate:** N/A\n'
        description_credits = '- **Powered by Bray \u2666**'
        api.update_task(task_id = task.id, description = description_description + description_created_on + description_longest_streak + description_completion_rate + description_credits)
#-----------------------------------------------------------------------------------------------------------#
def openJson(filepath):
    with open(filepath, 'r') as file:
        return jsonLoad(file)   

def dumpJson(filepath, payload):
    with open(filepath, 'w') as file:
        dump(payload, file)

def updateJson(task):
    json = openJson('json/habits.json')
    task_id = str(task.id)
    task_streak = getStreak(task)
    if not task_id in json:
        payload = {
            task_id: {
                'completion_rate': 'N/A',
                'content': getContent(task),
                'created_ago': abs(current_date - task_created_date).days,
                'current_streak': 1,
                'longest_streak': 1,
                'misses': 0
            }
        }
        json.update(payload)
    else:
        created_ago = abs(current_date - task_created_date).days
        misses = json[task_id]['misses'] + 1 if isDue(task) else json[task_id]['misses']
        if created_ago > 0:
            json[task_id]['completion_rate'] = round(((created_ago - misses) / created_ago) * 100)
        json[task_id]['content'] = getContent(task)
        json[task_id]['created_ago'] = created_ago
        json[task_id]['current_streak'] = task_streak
        longest_streak = json[task_id]['longest_streak']
        if longest_streak:
            json[task_id]['longest_streak'] = longest_streak if longest_streak > task_streak else task_streak
        else:
            json[task_id]['longest_streak'] = task_streak
        json[task_id]['misses'] += 1 if isDue(task) else 0
    dumpJson('json/habits.json', json)
#-----------------------------------------------------------------------------------------------------------#
current_date = datetime.now().date()
current_time = datetime.now().time()
for task in api.get_tasks(project_id = yaml['project_id']):
    if not isValid(task):
        continue
    task_created_date = datetime.strptime(task.created, '%Y-%m-%dT%H:%M:%S.%fZ').date()
    if isDue(task):
        resetStreak(task)
        printNeutral(f'{getContent(task)} ({task.id}) streak has been reset')
    else:
        incrementStreak(task)
        printSuccess(f'{getContent(task)} ({task.id}) streak has been incremented')
    updateJson(task)
    updateDescription(task)